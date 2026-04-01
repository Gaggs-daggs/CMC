package com.atlas.health

import android.content.Context
import android.util.Log
import android.webkit.MimeTypeMap
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.ServerSocket
import java.net.Socket
import java.net.URLDecoder
import java.util.concurrent.Executors

/**
 * Lightweight HTTP server that serves files from Android assets/webapp/.
 * Runs on localhost:LOCAL_PORT so the WebView has a proper http:// origin,
 * avoiding all file:// CORS, MIME-type, and ServiceWorker issues.
 */
class LocalAssetServer(private val context: Context) {

    companion object {
        const val PORT = 18080
        private const val TAG = "LocalAssetServer"
    }

    private var serverSocket: ServerSocket? = null
    private val executor = Executors.newCachedThreadPool()
    @Volatile private var running = false

    fun start() {
        if (running) return
        running = true
        executor.execute {
            try {
                // Close any lingering socket from a previous instance
                try { serverSocket?.close() } catch (_: Exception) {}
                
                val ss = ServerSocket()
                ss.reuseAddress = true
                ss.bind(java.net.InetSocketAddress(PORT))
                serverSocket = ss
                Log.i(TAG, "Local server started on port $PORT")
                while (running) {
                    try {
                        val client = serverSocket?.accept() ?: break
                        executor.execute { handleClient(client) }
                    } catch (e: Exception) {
                        if (running) Log.e(TAG, "Accept error", e)
                    }
                }
            } catch (e: java.net.BindException) {
                Log.w(TAG, "Port $PORT already in use, retrying in 1s...")
                try { Thread.sleep(1000) } catch (_: Exception) {}
                running = false
                start()  // Retry
            } catch (e: Exception) {
                Log.e(TAG, "Server start failed", e)
            }
        }
    }

    fun stop() {
        running = false
        try { serverSocket?.close() } catch (_: Exception) {}
    }

    fun getBaseUrl(): String = "http://localhost:$PORT"

    private fun handleClient(client: Socket) {
        try {
            val reader = BufferedReader(InputStreamReader(client.getInputStream()))
            val requestLine = reader.readLine() ?: return
            // e.g. "GET /assets/index-xxx.js HTTP/1.1"
            val parts = requestLine.split(" ")
            if (parts.size < 2) return

            var path = URLDecoder.decode(parts[1], "UTF-8")
            // Remove query string
            val queryIdx = path.indexOf('?')
            if (queryIdx >= 0) path = path.substring(0, queryIdx)
            // Remove leading slash
            if (path.startsWith("/")) path = path.substring(1)
            // Default to index.html
            if (path.isEmpty()) path = "index.html"

            val assetPath = "webapp/$path"
            val mimeType = getMimeType(path)

            try {
                val inputStream = context.assets.open(assetPath)
                val bytes = inputStream.readBytes()
                inputStream.close()

                val headers = buildString {
                    append("HTTP/1.1 200 OK\r\n")
                    append("Content-Type: $mimeType\r\n")
                    append("Content-Length: ${bytes.size}\r\n")
                    append("Access-Control-Allow-Origin: *\r\n")
                    append("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n")
                    append("Access-Control-Allow-Headers: *\r\n")
                    append("Cache-Control: no-cache\r\n")
                    append("Connection: close\r\n")
                    append("\r\n")
                }

                val out = client.getOutputStream()
                out.write(headers.toByteArray())
                out.write(bytes)
                out.flush()
            } catch (e: Exception) {
                // File not found — return 404
                val body = "Not Found: $path"
                val headers = "HTTP/1.1 404 Not Found\r\nContent-Length: ${body.length}\r\nConnection: close\r\n\r\n"
                val out = client.getOutputStream()
                out.write(headers.toByteArray())
                out.write(body.toByteArray())
                out.flush()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Handle client error", e)
        } finally {
            try { client.close() } catch (_: Exception) {}
        }
    }

    private fun getMimeType(path: String): String {
        val ext = path.substringAfterLast('.', "").lowercase()
        return when (ext) {
            "html", "htm" -> "text/html; charset=utf-8"
            "js", "mjs" -> "application/javascript; charset=utf-8"
            "css" -> "text/css; charset=utf-8"
            "json" -> "application/json; charset=utf-8"
            "png" -> "image/png"
            "jpg", "jpeg" -> "image/jpeg"
            "gif" -> "image/gif"
            "svg" -> "image/svg+xml"
            "ico" -> "image/x-icon"
            "webp" -> "image/webp"
            "woff" -> "font/woff"
            "woff2" -> "font/woff2"
            "ttf" -> "font/ttf"
            "otf" -> "font/otf"
            "mp3" -> "audio/mpeg"
            "wav" -> "audio/wav"
            "mp4" -> "video/mp4"
            "webm" -> "video/webm"
            "xml" -> "application/xml"
            "txt" -> "text/plain; charset=utf-8"
            "webmanifest" -> "application/manifest+json"
            else -> "application/octet-stream"
        }
    }
}
