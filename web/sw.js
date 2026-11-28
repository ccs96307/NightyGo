const CACHE_PREFIX = 'nightygo-web-v';
const CACHE = CACHE_PREFIX + '30';
const ROOT = new URL('./', self.location.href);
const FILES = ['./', './index.html', './styles.css', './theme.css?v=30', './app.js', './ai-config.js', './model-storage.js', './placement-input.js', './sgf-core.js', './recovery.js', './sgf-position.js', './go-rules.js', './engine-worker.js', './assets/engine/kataeval.js', './assets/engine/kataeval.wasm', './manifest.webmanifest', './icon.svg',
  './assets/sounds/go_stone_01.wav', './assets/sounds/go_stone_02.wav', './assets/sounds/go_stone_03.wav',
  './assets/sounds/go_stone_04.wav', './assets/sounds/cat_meow.mp3', './assets/sounds/cat_meow_2.mp3', './assets/sounds/cat_meow_3.mp3', './assets/sounds/cat_capture_yowl.mp3', './assets/sounds/go_stone_05.wav', './assets/sounds/capture_single.wav',
  './assets/sounds/capture_small_group.wav', './assets/sounds/capture_group.wav', './assets/sounds/capture_large_group.wav'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

const assets = new Set(FILES.map(path => new URL(path, ROOT).href));
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET' || !assets.has(request.url)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    return await cache.match(request) || fetch(request);
  })());
});
