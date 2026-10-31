const CACHE_NAME = 'meshcom-dashboard-v2';
const ASSETS_TO_CACHE = [
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Pass through dynamic requests to the MeshCom node
  if (event.request.url.includes('/?sendmessage') || 
      event.request.url.includes('/setparam') || 
      event.request.url.includes('/getparam') || 
      event.request.url.includes('/callfunction') ||
      event.request.url.includes('/?getmessages')) {
    return event.respondWith(fetch(event.request));
  }

  // Cache first for UI assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});
