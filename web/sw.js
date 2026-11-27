const CACHE = 'nightygo-web-v26';
const ROOT = new URL('./', self.location.href);
const FILES = ['./', './index.html', './styles.css', './theme.css?v=26', './app.js', './ai-config.js', './placement-input.js', './sgf-core.js', './go-rules.js', './engine-worker.js', './assets/engine/kataeval.js', './assets/engine/kataeval.wasm', './manifest.webmanifest', './icon.svg',
  './assets/sounds/go_stone_01.wav', './assets/sounds/go_stone_02.wav', './assets/sounds/go_stone_03.wav',
  './assets/sounds/go_stone_04.wav', './assets/sounds/cat_meow.mp3', './assets/sounds/cat_meow_2.mp3', './assets/sounds/cat_meow_3.mp3', './assets/sounds/cat_capture_yowl.mp3', './assets/sounds/go_stone_05.wav', './assets/sounds/capture_single.wav',
  './assets/sounds/capture_small_group.wav', './assets/sounds/capture_group.wav', './assets/sounds/capture_large_group.wav'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  if (new URL(event.request.url).pathname.includes('/assets/models/')) { event.respondWith(fetch(event.request)); return; }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
    if (response.ok && new URL(event.request.url).pathname.startsWith(ROOT.pathname)) caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
    return response;
  })));
});
