const CACHE_NAME = 'transsflow-cache-v1.0.0';
const API_CACHE_NAME = 'transsflow-api-v1.0.0';
const STATIC_URL = '/static/';
const API_URL = '/api/';
const OFFLINE_PAGE = '/offline/';

// Cache static resources
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/offline/'
];

// Install event - cache static resources
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static resources');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME && cache !== API_CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - handle requests
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Skip chrome-extension requests
  if (url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle API requests
  if (url.pathname.startsWith(API_URL)) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache successful API responses
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(API_CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Return cached data if offline
          return caches.match(event.request).then(response => {
            if (response) {
              return response;
            }
            // Return a basic offline response for API
            return new Response(JSON.stringify({
              error: 'Offline',
              message: 'You are currently offline. Please check your connection.'
            }), {
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            });
          });
        })
    );
    return;
  }
  
  // Handle navigation requests (HTML pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          // If fetch fails, return offline page
          return caches.match(OFFLINE_PAGE);
        })
    );
    return;
  }
  
  // Handle static resources
  event.respondWith(
    caches.match(event.request).then(response => {
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

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'sync-queue') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(syncPendingActions());
  }
});

// Push notification
self.addEventListener('push', event => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from Transs Flow',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Explore',
        icon: '/static/icons/icon-192x192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/icon-192x192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Transs Flow IPQC', options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification click received');
  event.notification.close();
  
  if (event.action === 'explore') {
    // Open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
  // If action is 'close' or default, do nothing
});

// Function to sync pending actions
async function syncPendingActions() {
  try {
    console.log('Service Worker: Syncing pending actions');
    
    // Get pending actions from IndexedDB
    const db = await openDB('ipqc-queue', 1);
    const pendingActions = await db.getAll('actions');
    
    console.log(`Service Worker: Found ${pendingActions.length} pending actions`);
    
    for (const action of pendingActions) {
      try {
        // Send action to server
        await fetch(action.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${action.token}`
          },
          body: JSON.stringify(action.data)
        });
        
        // Mark as synced
        await db.put('actions', { ...action, status: 'synced' });
        
        console.log(`Service Worker: Synced action ${action.id}`);
      } catch (error) {
        console.error(`Service Worker: Failed to sync action ${action.id}:`, error);
        // Keep as pending for next sync attempt
        await db.put('actions', { ...action, status: 'failed' });
      }
    }
  } catch (error) {
    console.error('Service Worker: Sync error:', error);
  }
}

// IndexedDB helper function
function openDB(name, version) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      
      // Create object store if it doesn't exist
      if (!db.objectStoreNames.contains('actions')) {
        db.createObjectStore('actions', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Handle message events
self.addEventListener('message', event => {
  console.log('Service Worker: Message received', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});