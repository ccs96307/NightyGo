// Keep one shared connection per tab. Old tabs can otherwise hold a schema
// upgrade open indefinitely, including retries queued behind the first open.
export function createModelStorage(translate) {
  let opening;
  let blocked = false;

  function database() {
    if (opening) return opening;
    opening = new Promise((resolve, reject) => {
      const request = indexedDB.open('nightygo-models-v1', 3);
      request.onblocked = () => {
        blocked = true;
        reject(Error(translate('modelStorageBlocked')));
      };
      request.onerror = () => {
        blocked = false;
        opening = undefined;
        reject(request.error);
      };
      request.onupgradeneeded = () => {
        const db = request.result;
        db.createObjectStore('pendingInstalls');
        const models = db.objectStoreNames.contains('models')
          ? request.transaction.objectStore('models')
          : db.createObjectStore('models', {keyPath: 'id'});
        if (!db.objectStoreNames.contains('modelChunks')) {
          db.createObjectStore('modelChunks', {keyPath: ['id', 'index']});
          return;
        }
        // All earlier connections have closed. v2 could commit chunks without
        // ever publishing their model if its installing tab was interrupted.
        const chunks = request.transaction.objectStore('modelChunks');
        const modelKeys = models.getAllKeys();
        modelKeys.onsuccess = () => {
          const published = new Set(modelKeys.result);
          const keys = chunks.openKeyCursor();
          keys.onsuccess = () => {
            const cursor = keys.result;
            if (!cursor) return;
            if (!published.has(cursor.key[0])) chunks.delete(cursor.key);
            cursor.continue();
          };
        };
      };
      request.onsuccess = () => {
        const db = request.result;
        if (blocked) {
          db.close();
          blocked = false;
          opening = undefined;
          return;
        }
        const release = () => { db.close(); opening = undefined; };
        db.onversionchange = release;
        db.onclose = release;
        resolve(db);
      };
    });
    return opening;
  }

  const lockName = id => 'nightygo:model-install:' + id;
  const chunkRange = id => IDBKeyRange.bound([id, 0], [id, Number.MAX_SAFE_INTEGER]);

  function stageInstall(db, id) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['models', 'pendingInstalls'], 'readwrite');
      tx.oncomplete = resolve;
      tx.onabort = () => reject(tx.error || Error(translate('modelStorageIncomplete')));
      const existing = tx.objectStore('models').count(id);
      existing.onsuccess = () => {
        if (existing.result) tx.abort();
        else tx.objectStore('pendingInstalls').add(true, id);
      };
    });
  }

  function discardStaged(db, id) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['pendingInstalls', 'modelChunks'], 'readwrite');
      tx.oncomplete = resolve;
      tx.onabort = () => reject(tx.error);
      const stage = tx.objectStore('pendingInstalls');
      const pending = stage.count(id);
      pending.onsuccess = () => {
        if (pending.result) {
          tx.objectStore('modelChunks').delete(chunkRange(id));
          stage.delete(id);
        }
      };
    });
  }

  async function recoverAbandoned(db) {
    if (!navigator.locks) return;
    const ids = await new Promise((resolve, reject) => {
      const tx = db.transaction('pendingInstalls');
      const keys = tx.objectStore('pendingInstalls').getAllKeys();
      tx.oncomplete = () => resolve(keys.result);
      tx.onabort = () => reject(tx.error);
    });
    for (const id of ids) {
      await navigator.locks.request(lockName(id), {ifAvailable: true}, lock => {
        if (lock) return discardStaged(db, id);
      });
    }
  }

  async function putModelChunked(model, bytes, onProgress = () => {}) {
    const db = await database();
    const chunkSize = 8 * 1024 * 1024;
    const total = bytes.byteLength;
    const count = Math.ceil(total / chunkSize);
    if (!count || total !== model.size) throw Error(translate('modelStorageIncomplete'));
    const metadata = {...model, chunks: count, storageFormat: 'chunked'};
    const locks = navigator.locks;
    if (locks) {
      // While the installing page is alive it owns this origin-wide lock.
      // The browser releases it on tab/process exit, allowing orphan cleanup.
      await locks.request(lockName(model.id), async () => {
        await stageInstall(db, model.id);
        try {
          for (let index = 0; index < count; index++) {
            const offset = index * chunkSize;
            const end = Math.min(total, offset + chunkSize);
            const last = index === count - 1;
            await new Promise((resolve, reject) => {
              const stores = last ? ['modelChunks', 'models', 'pendingInstalls'] : ['modelChunks'];
              const tx = db.transaction(stores, 'readwrite');
              tx.oncomplete = resolve;
              tx.onabort = () => reject(tx.error || Error(translate('modelStorageIncomplete')));
              tx.objectStore('modelChunks').add({id: model.id, index, offset, bytes: bytes.slice(offset, end)});
              if (last) {
                tx.objectStore('models').add(metadata);
                tx.objectStore('pendingInstalls').delete(model.id);
              }
            });
            onProgress(end, total, index + 1, count);
          }
        } catch (error) {
          await discardStaged(db, model.id).catch(() => {});
          throw error;
        }
      });
      return;
    }

    // Without Web Locks there is no reliable way to distinguish an abandoned
    // install from another active tab. Commit the whole install atomically.
    await new Promise((resolve, reject) => {
      const tx = db.transaction(['models', 'modelChunks'], 'readwrite');
      tx.oncomplete = resolve;
      tx.onabort = () => reject(tx.error || Error(translate('modelStorageIncomplete')));
      const chunks = tx.objectStore('modelChunks');
      function write(index) {
        const offset = index * chunkSize;
        const end = Math.min(total, offset + chunkSize);
        // Give the structured clone just this chunk's backing buffer.
        const request = chunks.add({id: model.id, index, offset, bytes: bytes.slice(offset, end)});
        request.onsuccess = () => {
          if (index + 1 < count) {
            write(index + 1);
          } else {
            tx.objectStore('models').add(metadata);
          }
        };
      }
      write(0);
    });
    onProgress(total, total, count, count);
  }

  async function getModel(id) {
    const db = await database();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(['models', 'modelChunks']);
      const request = tx.objectStore('models').get(id);
      let model, restored = 0, expectedIndex = 0, invalid = false;
      tx.onabort = () => reject(tx.error || Error(translate('modelStorageIncomplete')));
      tx.oncomplete = () => {
        if (invalid || (model?.chunks && (restored !== model.size || expectedIndex !== model.chunks))) {
          reject(Error(translate('modelStorageIncomplete')));
        } else {
          resolve(model);
        }
      };
      request.onsuccess = () => {
        model = request.result;
        if (!model?.chunks) return;  // v1 stored the entire buffer in the models record.
        const bytes = new Uint8Array(model.size);
        model.bytes = bytes.buffer;
        const range = chunkRange(id);
        const parts = tx.objectStore('modelChunks').openCursor(range);
        parts.onsuccess = () => {
          const cursor = parts.result;
          if (!cursor) return;
          const {index, offset, bytes: chunk} = cursor.value;
          const part = chunk instanceof Uint8Array ? chunk : new Uint8Array(chunk);
          if (index !== expectedIndex || offset !== restored || !part.length || part.length > bytes.length - restored) {
            invalid = true;
            return;
          }
          bytes.set(part, offset);
          restored += part.length;
          expectedIndex++;
          cursor.continue();
        };
      };
    });
  }

  async function listModels() {
    const db = await database();
    await recoverAbandoned(db);
    return new Promise((resolve, reject) => {
      const models = [];
      const tx = db.transaction('models');
      tx.oncomplete = () => resolve(models);
      tx.onabort = () => reject(tx.error || Error(translate('modelStorageIncomplete')));
      const rows = tx.objectStore('models').openCursor();
      rows.onsuccess = () => {
        const row = rows.result;
        if (!row) return;
        const {id, name, size, added} = row.value;
        models.push({id, name, size, added});
        row.continue();
      };
    });
  }

  return {putModelChunked, getModel, listModels};
}
