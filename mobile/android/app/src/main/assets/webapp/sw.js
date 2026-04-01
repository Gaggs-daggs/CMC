// ============================================================
// Atlas — Service Worker (Offline-First PWA)
// ============================================================
// Strategy:
//   - App Shell (HTML/CSS/JS/fonts) → Cache First (instant load)
//   - API calls → Network First, fallback to cache
//   - Images → Stale While Revalidate
// ============================================================

const CACHE_VERSION = 'atlas-v2'
const STATIC_CACHE = `${CACHE_VERSION}-static`
const API_CACHE = `${CACHE_VERSION}-api`
const IMAGE_CACHE = `${CACHE_VERSION}-images`

// Files to pre-cache on install (app shell)
const APP_SHELL = [
  '/',
  '/index.html',
  '/manifest.json',
]

// ─── Install: Pre-cache App Shell ──────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...')
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Pre-caching app shell')
      return cache.addAll(APP_SHELL)
    })
  )
  // Activate immediately, don't wait for old tabs to close
  self.skipWaiting()
})

// ─── Activate: Clean old caches ────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...')
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            // Delete old CMC caches AND old Atlas version caches
            const isOldCmc = name.startsWith('cmc-health-')
            const isOldAtlas = name.startsWith('atlas-') && name !== STATIC_CACHE && name !== API_CACHE && name !== IMAGE_CACHE
            return isOldCmc || isOldAtlas
          })
          .map((name) => {
            console.log('[SW] Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    })
  )
  // Take control of all open tabs
  self.clients.claim()
})

// ─── Fetch: Smart caching strategies ───────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests (POST for chat, etc.)
  if (request.method !== 'GET') return

  // Skip Chrome extension requests and other schemes
  if (!url.protocol.startsWith('http')) return

  // Strategy 1: API calls → Network First (fresh data preferred)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, API_CACHE))
    return
  }

  // Strategy 2: Images → Stale While Revalidate
  if (request.destination === 'image' || url.pathname.match(/\.(png|jpg|jpeg|gif|svg|webp|ico)$/i)) {
    event.respondWith(staleWhileRevalidate(request, IMAGE_CACHE))
    return
  }

  // Strategy 3: Google Fonts & external CDN → Cache First
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(cacheFirst(request, STATIC_CACHE))
    return
  }

  // Strategy 4: App shell (HTML/CSS/JS) → Cache First, Network Fallback
  event.respondWith(cacheFirst(request, STATIC_CACHE))
})

// ─── Cache Strategies ──────────────────────────────────────────

// Network First: Try network, fallback to cache (for API data)
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request)
    // Cache successful API responses
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      console.log('[SW] Serving from cache (offline):', request.url)
      return cachedResponse
    }
    // Return offline fallback for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/index.html')
    }
    // Return offline JSON for API requests
    return new Response(
      JSON.stringify({
        offline: true,
        message: 'You are offline. This data was not available in cache.',
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}

// Cache First: Try cache, fallback to network (for static assets)
async function cacheFirst(request, cacheName) {
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    // For HTML navigation, serve cached index.html (SPA fallback)
    if (request.mode === 'navigate') {
      return caches.match('/index.html')
    }
    return new Response('Offline', { status: 503 })
  }
}

// Stale While Revalidate: Serve cache immediately, update in background
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cachedResponse = await cache.match(request)

  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone())
      }
      return networkResponse
    })
    .catch(() => cachedResponse)

  return cachedResponse || fetchPromise
}

// ─── Background Sync: Queue messages sent while offline ────────
self.addEventListener('sync', (event) => {
  if (event.tag === 'send-message') {
    event.waitUntil(sendQueuedMessages())
  }
})

async function sendQueuedMessages() {
  // Future: Read from IndexedDB queue and POST to /api/v1/conversation
  console.log('[SW] Background sync: sending queued messages')
}
