const CACHE_NAME = 'ipqc-pwa-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/manifest.json'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version if available
        if (response) {
          return response;
        }
        
        // Otherwise fetch from network
        return fetch(event.request).then(response => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response as it's a stream
          const responseToCache = response.clone();
          
          // Cache the fetched resource
          caches.open(CACHE_NAME)
            .then(cache => cache.put(event.request, responseToCache));
            
          return response;
        });
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'sync-queue') {
    event.waitUntil(syncPendingActions());
  }
});

// Push notification
self.addEventListener('push', event => {
  const options = {
    body: event.data.text(),
    icon: '/static/images/icon-192.png',
    badge: '/static/images/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };
  
  event.waitUntil(
    self.registration.showNotification('IPQC Inspector', options)
  );
});

// Function to sync pending actions
async function syncPendingActions() {
  try {
    // Get pending actions from IndexedDB
    const db = await openDB('ipqc-queue', 1);
    const pendingActions = await db.getAll('actions');
    
    for (const action of pendingActions) {
      try {
        // Send action to server
        await axios.post(action.endpoint, action.data, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        // Mark as synced
        await db.put('actions', { ...action, status: 'synced' });
        
        console.log(`Synced action ${action.id}`);
      } catch (error) {
        console.error(`Failed to sync action ${action.id}:`, error);
        // Keep as pending for next sync attempt
        await db.put('actions', { ...action, status: 'failed' });
      }
    }
  } catch (error) {
    console.error('Sync error:', error);
  }
}