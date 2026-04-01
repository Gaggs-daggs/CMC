// ============================================================
// Atlas — Offline Storage (IndexedDB wrapper)
// Cache previous diagnoses, chat history, and user data
// so the app works even without connectivity.
// ============================================================

const DB_NAME = 'atlas-offline'
const DB_VERSION = 1

const STORES = {
  MESSAGES: 'messages',
  DIAGNOSES: 'diagnoses',
  QUEUE: 'outbox', // queued messages to send when back online
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = (event) => {
      const db = event.target.result

      // Chat messages store (keyed by sessionId + index)
      if (!db.objectStoreNames.contains(STORES.MESSAGES)) {
        const msgStore = db.createObjectStore(STORES.MESSAGES, { keyPath: 'id', autoIncrement: true })
        msgStore.createIndex('sessionId', 'sessionId', { unique: false })
        msgStore.createIndex('timestamp', 'timestamp', { unique: false })
      }

      // Diagnoses store
      if (!db.objectStoreNames.contains(STORES.DIAGNOSES)) {
        const dxStore = db.createObjectStore(STORES.DIAGNOSES, { keyPath: 'id', autoIncrement: true })
        dxStore.createIndex('sessionId', 'sessionId', { unique: false })
      }

      // Outbox — messages queued while offline
      if (!db.objectStoreNames.contains(STORES.QUEUE)) {
        db.createObjectStore(STORES.QUEUE, { keyPath: 'id', autoIncrement: true })
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

// ─── Messages ──────────────────────────────────────────────

export async function saveMessages(sessionId, messages) {
  const db = await openDB()
  const tx = db.transaction(STORES.MESSAGES, 'readwrite')
  const store = tx.objectStore(STORES.MESSAGES)

  // Clear old messages for this session, then re-write
  const index = store.index('sessionId')
  const range = IDBKeyRange.only(sessionId)
  let cursor = await new Promise((resolve) => {
    const req = index.openCursor(range)
    req.onsuccess = () => resolve(req.result)
  })
  while (cursor) {
    cursor.delete()
    cursor = await new Promise((resolve) => {
      cursor.continue()
      cursor.request.onsuccess = () => resolve(cursor.request.result)
    })
  }

  // Write fresh messages
  for (const msg of messages) {
    store.put({ sessionId, ...msg, timestamp: Date.now() })
  }

  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve
    tx.onerror = () => reject(tx.error)
  })
}

export async function getMessages(sessionId) {
  const db = await openDB()
  const tx = db.transaction(STORES.MESSAGES, 'readonly')
  const index = tx.objectStore(STORES.MESSAGES).index('sessionId')
  const range = IDBKeyRange.only(sessionId)

  return new Promise((resolve, reject) => {
    const req = index.getAll(range)
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ─── Diagnoses ─────────────────────────────────────────────

export async function saveDiagnosis(sessionId, diagnosis) {
  const db = await openDB()
  const tx = db.transaction(STORES.DIAGNOSES, 'readwrite')
  tx.objectStore(STORES.DIAGNOSES).put({ sessionId, ...diagnosis, timestamp: Date.now() })
  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve
    tx.onerror = () => reject(tx.error)
  })
}

export async function getDiagnoses(sessionId) {
  const db = await openDB()
  const tx = db.transaction(STORES.DIAGNOSES, 'readonly')
  const index = tx.objectStore(STORES.DIAGNOSES).index('sessionId')
  return new Promise((resolve, reject) => {
    const req = index.getAll(IDBKeyRange.only(sessionId))
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ─── Offline Outbox ────────────────────────────────────────

export async function queueMessage(payload) {
  const db = await openDB()
  const tx = db.transaction(STORES.QUEUE, 'readwrite')
  tx.objectStore(STORES.QUEUE).put({ ...payload, queuedAt: Date.now() })
  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve
    tx.onerror = () => reject(tx.error)
  })
}

export async function getQueuedMessages() {
  const db = await openDB()
  const tx = db.transaction(STORES.QUEUE, 'readonly')
  return new Promise((resolve, reject) => {
    const req = tx.objectStore(STORES.QUEUE).getAll()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

export async function clearQueue() {
  const db = await openDB()
  const tx = db.transaction(STORES.QUEUE, 'readwrite')
  tx.objectStore(STORES.QUEUE).clear()
  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve
    tx.onerror = () => reject(tx.error)
  })
}
