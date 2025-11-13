const CACHE_NAME = 'transsflow-cache-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/css/main.css',
  '/static/js/main.js',
  '/logo192.png',
  '/logo512.png',
];

// 🧩 Install: Cache important static files
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[Service Worker] Caching core assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// ⚙️ Activate: Clear old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating new version...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', name);
            return caches.delete(name);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// 🌐 Fetch: Network-first for API, Cache-first for static
self.addEventListener('fetch', event => {
  const { request } = event;

  // Skip chrome extensions and non-GET requests
  if (!request.url.startsWith(self.location.origin) || request.method !== 'GET') {
    return;
  }

  // API calls: network-first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Static files: cache-first
  event.respondWith(
    caches.match(request).then(cached => {
      return (
        cached ||
        fetch(request).then(response => {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, responseClone));
          return response;
        })
      );
    })
  );
});

// 🔄 Background sync handler
self.addEventListener('sync', event => {
  if (event.tag === 'sync-queue') {
    event.waitUntil(syncPendingActions());
  }
});

// 🔔 Push notifications
self.addEventListener('push', event => {
  const data = event.data ? event.data.text() : 'New notification';
  const options = {
    body: data,
    icon: '/logo192.png',
    badge: '/favicon.ico',
  };
  event.waitUntil(self.registration.showNotification('Transs Flow', options));
});
