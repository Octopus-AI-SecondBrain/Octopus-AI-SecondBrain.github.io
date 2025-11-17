/**
 * Service Worker for Octopus Second Brain PWA
 * Implements offline-first caching strategy with Workbox patterns
 */

/* eslint-env serviceworker */

const CACHE_NAME = 'octopus-v1'
const API_CACHE = 'octopus-api-v1'
const STATIC_CACHE = 'octopus-static-v1'

// Assets to precache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html'
]

// Install event - precache critical assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...')
  
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[ServiceWorker] Precaching app shell')
      return cache.addAll(PRECACHE_ASSETS)
    }).then(() => {
      console.log('[ServiceWorker] Skip waiting on install')
      return self.skipWaiting()
    })
  )
})

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            return name !== CACHE_NAME && name !== API_CACHE && name !== STATIC_CACHE
          })
          .map((name) => {
            console.log('[ServiceWorker] Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    }).then(() => {
      console.log('[ServiceWorker] Claiming clients')
      return self.clients.claim()
    })
  )
})

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    // Cache API requests from backend
    if (url.pathname.startsWith('/api') || url.pathname.startsWith('/auth')) {
      event.respondWith(
        caches.open(API_CACHE).then((cache) => {
          return fetch(request).then((response) => {
            // Only cache successful GET requests
            if (request.method === 'GET' && response.status === 200) {
              cache.put(request, response.clone())
            }
            return response
          }).catch(() => {
            // Return cached response if network fails
            return cache.match(request).then((cached) => {
              if (cached) {
                return cached
              }
              // Return offline page if no cache
              return caches.match('/offline.html')
            })
          })
        })
      )
      return
    }
    return
  }

  // Handle navigation requests (HTML pages)
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match('/offline.html')
      })
    )
    return
  }

  // Cache-first strategy for static assets
  if (
    request.destination === 'image' ||
    request.destination === 'font' ||
    request.destination === 'style' ||
    request.destination === 'script'
  ) {
    event.respondWith(
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.match(request).then((cached) => {
          if (cached) {
            // Return cached, but update in background
            fetch(request).then((response) => {
              if (response.status === 200) {
                cache.put(request, response.clone())
              }
            }).catch(() => {
              // Silently fail background update
            })
            return cached
          }

          // Not in cache, fetch and cache
          return fetch(request).then((response) => {
            if (response.status === 200) {
              cache.put(request, response.clone())
            }
            return response
          }).catch(() => {
            // Return offline page for failed requests
            return caches.match('/offline.html')
          })
        })
      })
    )
    return
  }

  // Default: network first, fallback to cache
  event.respondWith(
    fetch(request).then((response) => {
      // Cache successful GET requests
      if (request.method === 'GET' && response.status === 200) {
        const responseClone = response.clone()
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseClone)
        })
      }
      return response
    }).catch(() => {
      return caches.match(request).then((cached) => {
        return cached || caches.match('/offline.html')
      })
    })
  )
})

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-notes') {
    event.waitUntil(syncNotes())
  }
})

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {}
  const title = data.title || 'Octopus Second Brain'
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: data.actions || []
  }

  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  )
})

// Helper function to sync notes when back online
async function syncNotes() {
  try {
    const cache = await caches.open('pending-notes')
    const requests = await cache.keys()
    
    await Promise.all(
      requests.map(async (request) => {
        try {
          await fetch(request.clone())
          await cache.delete(request)
        } catch (error) {
          console.error('Failed to sync note:', error)
        }
      })
    )
  } catch (error) {
    console.error('Sync failed:', error)
  }
}

// Message handler for commands from main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.addAll(event.data.urls)
      })
    )
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((names) => {
        return Promise.all(names.map((name) => caches.delete(name)))
      })
    )
  }
})
