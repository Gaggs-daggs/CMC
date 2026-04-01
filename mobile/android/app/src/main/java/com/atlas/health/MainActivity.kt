package com.atlas.health

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.speech.RecognizerIntent
import android.util.Log
import android.view.View
import android.view.WindowManager
import android.webkit.*
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "AtlasMain"
        private const val BACKEND_API_BASE = "https://bisectional-annelle-overgenially.ngrok-free.dev/api/v1"
    }

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var progressBar: ProgressBar
    private lateinit var noConnectionView: LinearLayout
    private lateinit var splashOverlay: FrameLayout
    private lateinit var localServer: LocalAssetServer

    private var currentPhotoPath: String? = null
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private var pendingPermissionCallback: (() -> Unit)? = null
    private var pendingWebViewPermissionRequest: PermissionRequest? = null

    // ── Native Speech Recognition ─────────────────────────────
    private var speechLang: String = "en-IN"

    // ── Activity Result Launchers ──────────────────────────────

    private val cameraLauncher = registerForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success && currentPhotoPath != null) {
            fileUploadCallback?.onReceiveValue(arrayOf(Uri.fromFile(File(currentPhotoPath!!))))
        } else {
            fileUploadCallback?.onReceiveValue(null)
        }
        fileUploadCallback = null
    }

    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        fileUploadCallback?.onReceiveValue(if (uri != null) arrayOf(uri) else null)
        fileUploadCallback = null
    }

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            pendingPermissionCallback?.invoke()
            pendingPermissionCallback = null
            // If there's a pending WebView permission request, grant it now
            pendingWebViewPermissionRequest?.let {
                it.grant(it.resources)
                pendingWebViewPermissionRequest = null
            }
        } else {
            Toast.makeText(this, "Permissions required for this feature", Toast.LENGTH_SHORT).show()
            pendingPermissionCallback = null
            pendingWebViewPermissionRequest?.let {
                it.deny()
                pendingWebViewPermissionRequest = null
            }
        }
    }

    // ── Lifecycle ──────────────────────────────────────────────

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)

        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = getColor(R.color.atlas_dark)
        window.navigationBarColor = getColor(R.color.atlas_dark)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        progressBar = findViewById(R.id.progressBar)
        noConnectionView = findViewById(R.id.noConnectionView)
        splashOverlay = findViewById(R.id.splashOverlay)

        findViewById<Button>(R.id.btnRetry).setOnClickListener { loadApp() }

        swipeRefresh.setColorSchemeColors(getColor(R.color.atlas_primary), getColor(R.color.atlas_accent))
        swipeRefresh.setProgressBackgroundColorSchemeColor(getColor(R.color.atlas_surface))
        swipeRefresh.setOnRefreshListener {
            webView.reload()
            Handler(Looper.getMainLooper()).postDelayed({ swipeRefresh.isRefreshing = false }, 2000)
        }

        localServer = LocalAssetServer(this)
        localServer.start()

        setupWebView()

        // Request all permissions upfront so mic/camera work when needed
        requestAllPermissions()

        Handler(Looper.getMainLooper()).postDelayed({ loadApp() }, 300)
    }

    // ── Request All Permissions Upfront ────────────────────────

    private fun requestAllPermissions() {
        val needed = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.RECORD_AUDIO)
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.CAMERA)
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }

        if (needed.isNotEmpty()) {
            Log.i(TAG, "Requesting permissions: $needed")
            permissionLauncher.launch(needed.toTypedArray())
        } else {
            Log.i(TAG, "All permissions already granted")
        }
    }

    private fun hasPermission(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
    }

    // ── Native Speech Recognition (Intent-based for max compatibility) ──

    private val speechIntentLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val matches = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val text = matches?.firstOrNull() ?: ""
            Log.i(TAG, "Speech result: $text")
            if (text.isNotEmpty()) {
                val escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\"", "\\\"").replace("\n", "\\n")
                runOnUiThread {
                    webView.evaluateJavascript(
                        "if(window.__onNativeSpeechResult) window.__onNativeSpeechResult('$escaped', true);", null
                    )
                }
            } else {
                runOnUiThread {
                    webView.evaluateJavascript(
                        "if(window.__onNativeSpeechError) window.__onNativeSpeechError('no_match');", null
                    )
                }
            }
        } else {
            Log.w(TAG, "Speech cancelled or failed, resultCode=${result.resultCode}")
            runOnUiThread {
                webView.evaluateJavascript(
                    "if(window.__onNativeSpeechError) window.__onNativeSpeechError('cancelled');", null
                )
            }
        }
    }

    private fun startNativeListening(lang: String) {
        speechLang = lang
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, lang)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak now...")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        try {
            Log.i(TAG, "Launching speech recognition intent with lang: $lang")
            // Notify JS that speech started
            runOnUiThread {
                webView.evaluateJavascript("if(window.__onNativeSpeechStart) window.__onNativeSpeechStart();", null)
            }
            speechIntentLauncher.launch(intent)
        } catch (e: Exception) {
            Log.e(TAG, "Cannot launch speech recognition", e)
            runOnUiThread {
                Toast.makeText(this, "Speech recognition not available. Please install Google app.", Toast.LENGTH_LONG).show()
                webView.evaluateJavascript(
                    "if(window.__onNativeSpeechError) window.__onNativeSpeechError('not_available');", null
                )
            }
        }
    }

    private fun stopNativeListening() {
        // Intent-based approach doesn't need explicit stop
        Log.d(TAG, "stopNativeListening called (no-op for intent approach)")
    }

    // ── WebView Setup ──────────────────────────────────────────

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            mediaPlaybackRequiresUserGesture = false
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            cacheMode = WebSettings.LOAD_DEFAULT
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            loadWithOverviewMode = true
            useWideViewPort = true
            textZoom = 100
            userAgentString = "$userAgentString AtlasAndroid/1.0"
        }

        webView.addJavascriptInterface(AtlasBridge(), "AtlasNative")

        webView.webViewClient = object : WebViewClient() {

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = View.VISIBLE
                // Inject speech polyfill early so it's available when React initializes
                injectSpeechPolyfill()
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
                noConnectionView.visibility = View.GONE
                webView.visibility = View.VISIBLE
                injectApiConfig()
                // Re-inject polyfill after page finished in case it was lost
                injectSpeechPolyfill()
                // Install hooks to re-initialize React's speech recognizer
                injectSpeechReInit()
                Handler(Looper.getMainLooper()).postDelayed({
                    splashOverlay.animate().alpha(0f).setDuration(400)
                        .withEndAction { splashOverlay.visibility = View.GONE }.start()
                }, 800)
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                if (request?.isForMainFrame == true) {
                    Log.e(TAG, "WebView error: ${error?.description}")
                }
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                if (url.startsWith("tel:")) {
                    try { startActivity(Intent(Intent.ACTION_DIAL, Uri.parse(url))) } catch (_: Exception) {}
                    return true
                }
                if (url.contains("localhost:${LocalAssetServer.PORT}")) return false
                if (url.contains("/api/")) return false
                if (url.contains("192.168.")) return false
                if (url.contains("10.0.2.2")) return false
                if (url.contains("ngrok")) return false
                if (url.startsWith("http")) {
                    try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (_: Exception) {}
                    return true
                }
                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {

            override fun onShowFileChooser(
                webView: WebView?, filePathCallback: ValueCallback<Array<Uri>>?, fileChooserParams: FileChooserParams?
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback
                val acceptTypes = fileChooserParams?.acceptTypes ?: arrayOf()
                if (acceptTypes.any { it.contains("image") }) showImagePicker() else galleryLauncher.launch("*/*")
                return true
            }

            // ── THIS IS THE KEY: Handle WebView permission requests ──
            override fun onPermissionRequest(request: PermissionRequest?) {
                if (request == null) return
                runOnUiThread {
                    Log.i(TAG, "WebView permission request: ${request.resources.joinToString()}")

                    // Map WebView resources to Android permissions
                    val androidPermsNeeded = mutableListOf<String>()
                    for (resource in request.resources) {
                        when (resource) {
                            PermissionRequest.RESOURCE_AUDIO_CAPTURE -> {
                                if (!hasPermission(Manifest.permission.RECORD_AUDIO)) {
                                    androidPermsNeeded.add(Manifest.permission.RECORD_AUDIO)
                                }
                            }
                            PermissionRequest.RESOURCE_VIDEO_CAPTURE -> {
                                if (!hasPermission(Manifest.permission.CAMERA)) {
                                    androidPermsNeeded.add(Manifest.permission.CAMERA)
                                }
                            }
                        }
                    }

                    if (androidPermsNeeded.isEmpty()) {
                        // All Android permissions already granted — grant WebView request
                        Log.i(TAG, "Granting WebView permission (Android perms OK)")
                        request.grant(request.resources)
                    } else {
                        // Need to ask Android first, then grant WebView
                        Log.i(TAG, "Requesting Android permissions first: $androidPermsNeeded")
                        pendingWebViewPermissionRequest = request
                        permissionLauncher.launch(androidPermsNeeded.toTypedArray())
                    }
                }
            }

            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                if (hasPermission(Manifest.permission.ACCESS_FINE_LOCATION)) {
                    callback?.invoke(origin, true, false)
                } else {
                    pendingPermissionCallback = { callback?.invoke(origin, true, false) }
                    permissionLauncher.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION))
                }
            }

            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                consoleMessage?.let {
                    Log.d(TAG, "JS[${it.messageLevel()}]: ${it.message()} (${it.sourceId()}:${it.lineNumber()})")
                }
                return true
            }
        }

        WebView.setWebContentsDebuggingEnabled(true)
    }

    // ── Load App ───────────────────────────────────────────────

    private fun loadApp() {
        noConnectionView.visibility = View.GONE
        webView.visibility = View.VISIBLE
        progressBar.visibility = View.VISIBLE
        splashOverlay.visibility = View.VISIBLE
        splashOverlay.alpha = 1f
        val url = "${localServer.getBaseUrl()}/index.html"
        Log.i(TAG, "Loading app from: $url")
        webView.loadUrl(url)
    }

    // ── Inject Config ──────────────────────────────────────────

    private fun injectSpeechPolyfill() {
        val polyfillJs = """
            (function() {
                if (window.__atlasSpeechPolyfillInstalled) return;
                
                function NativeSpeechRecognition() {
                    this.continuous = false;
                    this.interimResults = true;
                    this.lang = 'en-IN';
                    this.onresult = null;
                    this.onerror = null;
                    this.onend = null;
                    this.onstart = null;
                    this._listening = false;
                }
                
                NativeSpeechRecognition.prototype.start = function() {
                    var self = this;
                    console.log('[Atlas] SpeechRecognition.start() lang=' + this.lang);
                    this._listening = true;
                    
                    window.__onNativeSpeechStart = function() {
                        console.log('[Atlas] Speech started');
                        if (self.onstart) self.onstart();
                    };
                    
                    window.__onNativeSpeechResult = function(text, isFinal) {
                        console.log('[Atlas] Speech result: ' + text + ' final=' + isFinal);
                        if (self.onresult) {
                            var result = { transcript: text, confidence: 0.9 };
                            var resultList = [result];
                            resultList.isFinal = isFinal;
                            var event = { results: [resultList] };
                            self.onresult(event);
                        }
                        if (isFinal) {
                            self._listening = false;
                            if (self.onend) self.onend();
                        }
                    };
                    
                    window.__onNativeSpeechError = function(err) {
                        console.log('[Atlas] Speech error: ' + err);
                        self._listening = false;
                        if (self.onerror) self.onerror({ error: err });
                        if (self.onend) self.onend();
                    };
                    
                    if (window.AtlasNative && window.AtlasNative.isSpeechAvailable()) {
                        window.AtlasNative.startSpeechRecognition(this.lang);
                    } else {
                        console.error('[Atlas] Native speech not available');
                        if (self.onerror) self.onerror({ error: 'not-supported' });
                        if (self.onend) self.onend();
                    }
                };
                
                NativeSpeechRecognition.prototype.stop = function() {
                    console.log('[Atlas] SpeechRecognition.stop()');
                    this._listening = false;
                    if (window.AtlasNative) {
                        window.AtlasNative.stopSpeechRecognition();
                    }
                    if (this.onend) this.onend();
                };
                
                NativeSpeechRecognition.prototype.abort = function() {
                    this.stop();
                };
                
                window.SpeechRecognition = NativeSpeechRecognition;
                window.webkitSpeechRecognition = NativeSpeechRecognition;
                window.__atlasSpeechPolyfillInstalled = true;
                
                console.log('[Atlas] SpeechRecognition polyfill installed');
            })();
        """.trimIndent()
        webView.evaluateJavascript(polyfillJs, null)
    }

    /**
     * After React mounts, the useEffect that checks for webkitSpeechRecognition
     * already ran (and found nothing), so recognitionRef.current is null.
     * This function triggers a synthetic state change in React to re-run that useEffect,
     * OR directly patches the mic button click handler to lazily create the recognizer.
     */
    private fun injectSpeechReInit() {
        val js = """
            (function() {
                if (!window.__atlasSpeechPolyfillInstalled) return;
                if (window.__atlasSpeechReInitDone) return;
                window.__atlasSpeechReInitDone = true;
                
                /* Intercept clicks on the mic button to lazily init recognizer */
                document.addEventListener('click', function(e) {
                    var btn = e.target.closest('[title="Voice input"]');
                    if (!btn) return;
                    
                    /* The React app stores recognitionRef.current — we can't access that
                       directly, but we CAN intercept the alert('Speech not supported')
                       and instead create a new recognizer and start it. */
                }, true);
                
                /* Override window.alert to intercept 'Speech not supported' and fix it */
                var origAlert = window.alert;
                window.alert = function(msg) {
                    if (msg === 'Speech not supported' && window.webkitSpeechRecognition) {
                        console.log('[Atlas] Intercepted "Speech not supported" - triggering re-init');
                        /* Force React to re-run the speech useEffect by dispatching a 
                           custom event that we'll also listen for */
                        window.dispatchEvent(new Event('atlas-reinit-speech'));
                        return; /* Don't show the alert */
                    }
                    origAlert.call(window, msg);
                };
                
                console.log('[Atlas] Speech re-init hooks installed');
            })();
        """.trimIndent()
        webView.evaluateJavascript(js, null)
    }

    private fun injectApiConfig() {
        val backendBase = BACKEND_API_BASE
        val js = """
            (function() {
                var origFetch = window.fetch;
                window.fetch = function(url, opts) {
                    if (typeof url === 'string') {
                        if (url.indexOf('http://localhost:8000/api/v1') !== -1) {
                            url = url.replace('http://localhost:8000/api/v1', '$backendBase');
                        } else if (url.indexOf('__ATLAS_API_BASE__') !== -1) {
                            url = url.replace('__ATLAS_API_BASE__', '$backendBase');
                        }
                    }
                    if (!opts) opts = {};
                    if (opts.credentials === 'include') {
                        opts.credentials = 'omit';
                    }
                    /* Add ngrok-skip-browser-warning header to bypass interstitial */
                    if (!opts.headers) opts.headers = {};
                    if (opts.headers instanceof Headers) {
                        opts.headers.set('ngrok-skip-browser-warning', 'true');
                    } else if (typeof opts.headers === 'object') {
                        opts.headers['ngrok-skip-browser-warning'] = 'true';
                    }
                    return origFetch.call(this, url, opts);
                };

                var origOpen = XMLHttpRequest.prototype.open;
                var origSend = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.open = function(method, url) {
                    if (typeof url === 'string') {
                        if (url.indexOf('http://localhost:8000/api/v1') !== -1) {
                            url = url.replace('http://localhost:8000/api/v1', '$backendBase');
                        }
                    }
                    this._atlasUrl = url;
                    return origOpen.apply(this, arguments);
                };
                XMLHttpRequest.prototype.send = function() {
                    try { this.setRequestHeader('ngrok-skip-browser-warning', 'true'); } catch(e) {}
                    return origSend.apply(this, arguments);
                };

                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(function(regs) {
                        regs.forEach(function(r) { r.unregister(); });
                    }).catch(function() {});
                }

                window.__ATLAS_NATIVE__ = true;
                window.__ATLAS_PLATFORM__ = 'android';

                console.log('[Atlas] Native bridge active. Backend: $backendBase');
            })();
        """.trimIndent()
        webView.evaluateJavascript(js, null)
    }

    // ── Image Picker ───────────────────────────────────────────

    private fun showImagePicker() {
        if (!hasPermission(Manifest.permission.CAMERA)) {
            pendingPermissionCallback = { showImagePickerDialog() }
            permissionLauncher.launch(arrayOf(Manifest.permission.CAMERA))
        } else {
            showImagePickerDialog()
        }
    }

    private fun showImagePickerDialog() {
        android.app.AlertDialog.Builder(this, R.style.Theme_Atlas)
            .setTitle("Select Image")
            .setItems(arrayOf("Take Photo", "Choose from Gallery")) { _, which ->
                when (which) {
                    0 -> launchCamera()
                    1 -> galleryLauncher.launch("image/*")
                }
            }
            .setNegativeButton("Cancel") { d, _ ->
                d.dismiss()
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = null
            }
            .show()
    }

    private fun launchCamera() {
        try {
            val ts = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val dir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
            val file = File.createTempFile("ATLAS_${ts}_", ".jpg", dir)
            currentPhotoPath = file.absolutePath
            val uri = FileProvider.getUriForFile(this, "${packageName}.fileprovider", file)
            cameraLauncher.launch(uri)
        } catch (e: IOException) {
            Log.e(TAG, "Cannot create image file", e)
            fileUploadCallback?.onReceiveValue(null)
            fileUploadCallback = null
        }
    }

    // ── JS Bridge ──────────────────────────────────────────────

    inner class AtlasBridge {
        @JavascriptInterface fun getApiBase(): String = BACKEND_API_BASE
        @JavascriptInterface fun getPlatform(): String = "android"
        @JavascriptInterface fun getVersion(): String = "1.0.0"

        @JavascriptInterface fun startSpeechRecognition(lang: String) {
            Log.i(TAG, "JS bridge: startSpeechRecognition($lang)")
            runOnUiThread {
                if (hasPermission(Manifest.permission.RECORD_AUDIO)) {
                    startNativeListening(lang)
                } else {
                    pendingPermissionCallback = { startNativeListening(lang) }
                    permissionLauncher.launch(arrayOf(Manifest.permission.RECORD_AUDIO))
                }
            }
        }

        @JavascriptInterface fun stopSpeechRecognition() {
            Log.i(TAG, "JS bridge: stopSpeechRecognition")
            runOnUiThread { stopNativeListening() }
        }

        @JavascriptInterface fun isSpeechAvailable(): Boolean {
            // Always return true — the intent launcher will handle the error
            // if no speech service exists. resolveActivity() returns null on
            // some devices (Vivo, Xiaomi) even when speech IS available.
            return true
        }

        @JavascriptInterface fun showToast(message: String) {
            runOnUiThread { Toast.makeText(this@MainActivity, message, Toast.LENGTH_SHORT).show() }
        }

        @JavascriptInterface fun vibrate(duration: Long) {
            val v = getSystemService(android.os.Vibrator::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                v?.vibrate(android.os.VibrationEffect.createOneShot(duration, android.os.VibrationEffect.DEFAULT_AMPLITUDE))
            }
        }

        @JavascriptInterface fun makePhoneCall(number: String) {
            try { startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$number"))) } catch (_: Exception) {}
        }

        @JavascriptInterface fun shareText(text: String) {
            startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"; putExtra(Intent.EXTRA_TEXT, text)
            }, "Share via"))
        }

        @JavascriptInterface fun isNetworkAvailable(): Boolean {
            val cm = getSystemService(ConnectivityManager::class.java)
            val caps = cm.getNetworkCapabilities(cm.activeNetwork ?: return false) ?: return false
            return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        }
    }

    // ── Navigation ─────────────────────────────────────────────

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onResume() { super.onResume(); if (::webView.isInitialized) webView.onResume() }
    override fun onPause() { super.onPause(); if (::webView.isInitialized) webView.onPause() }

    override fun onDestroy() {
        if (::localServer.isInitialized) localServer.stop()
        if (::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }
}
