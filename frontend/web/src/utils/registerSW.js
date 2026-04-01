// ============================================================
// Atlas — Service Worker Registration
// ============================================================

export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
        })

        console.log('[SW] Registered:', registration.scope)

        // Check for updates periodically (every 60 minutes)
        setInterval(() => {
          registration.update()
        }, 60 * 60 * 1000)

        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
                // New content available — dispatch custom event
                window.dispatchEvent(new CustomEvent('sw-update-available'))
              }
            })
          }
        })
      } catch (error) {
        console.error('[SW] Registration failed:', error)
      }
    })
  }
}

// Unregister (useful for debugging)
export async function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.ready
    await registration.unregister()
    console.log('[SW] Unregistered')
  }
}
