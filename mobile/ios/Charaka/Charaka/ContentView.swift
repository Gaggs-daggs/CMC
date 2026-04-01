import SwiftUI
import WebKit
import UIKit
import UniformTypeIdentifiers

// ─── Custom URL Scheme Handler ──────────────────────────────
// Serves local files via "atlas://" scheme so ES modules work
// (file:// URLs block type="module" scripts due to CORS)
class LocalFileSchemeHandler: NSObject, WKURLSchemeHandler {
    let rootDirectory: URL

    init(rootDirectory: URL) {
        self.rootDirectory = rootDirectory
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(NSError(domain: "LocalFile", code: 404))
            return
        }

        // Convert atlas://host/path → local file path
        var path = url.path
        if path.isEmpty || path == "/" {
            path = "/index.html"
        }
        // Remove leading slash
        let relativePath = String(path.dropFirst())
        let fileURL = rootDirectory.appendingPathComponent(relativePath)

        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            print("[Atlas] ❌ File not found: \(relativePath)")
            urlSchemeTask.didFailWithError(NSError(domain: "LocalFile", code: 404))
            return
        }

        do {
            let data = try Data(contentsOf: fileURL)
            let mimeType = Self.mimeType(for: fileURL.pathExtension)
            let response = URLResponse(url: url, mimeType: mimeType, expectedContentLength: data.count, textEncodingName: nil)
            urlSchemeTask.didReceive(response)
            urlSchemeTask.didReceive(data)
            urlSchemeTask.didFinish()
        } catch {
            print("[Atlas] ❌ Error reading: \(relativePath) — \(error)")
            urlSchemeTask.didFailWithError(error)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    static func mimeType(for ext: String) -> String {
        switch ext.lowercased() {
        case "html": return "text/html"
        case "css":  return "text/css"
        case "js":   return "application/javascript"
        case "json": return "application/json"
        case "png":  return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "gif":  return "image/gif"
        case "svg":  return "image/svg+xml"
        case "webp": return "image/webp"
        case "ico":  return "image/x-icon"
        case "woff": return "font/woff"
        case "woff2": return "font/woff2"
        case "ttf":  return "font/ttf"
        case "mp3":  return "audio/mpeg"
        case "wav":  return "audio/wav"
        case "webm": return "video/webm"
        case "mp4":  return "video/mp4"
        default:     return "application/octet-stream"
        }
    }
}

// ─── Main View ──────────────────────────────────────────────
struct ContentView: View {
    @State private var isLoading = true
    @State private var loadProgress: Double = 0
    @State private var showSplash = true

    var body: some View {
        ZStack {
            Color(red: 10/255, green: 37/255, blue: 64/255)
                .ignoresSafeArea()

            AtlasWebView(isLoading: $isLoading, loadProgress: $loadProgress)
                .ignoresSafeArea(.container, edges: .bottom)
                .opacity(showSplash ? 0 : 1)

            if isLoading && !showSplash {
                VStack {
                    ProgressView(value: loadProgress)
                        .progressViewStyle(LinearProgressViewStyle(tint: Color(red: 0, green: 212/255, blue: 170/255)))
                        .frame(height: 2)
                    Spacer()
                }
                .ignoresSafeArea()
            }

            if showSplash {
                SplashView()
                    .transition(.opacity)
            }
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                withAnimation(.easeOut(duration: 0.5)) {
                    showSplash = false
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

// ─── Splash Screen ──────────────────────────────────────────
struct SplashView: View {
    @State private var logoScale: CGFloat = 0.8
    @State private var logoOpacity: Double = 0

    var body: some View {
        ZStack {
            Color(red: 10/255, green: 37/255, blue: 64/255)
                .ignoresSafeArea()
            VStack(spacing: 20) {
                Image("SplashLogo")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 120, height: 120)
                    .clipShape(Circle())
                    .shadow(color: Color(red: 0, green: 212/255, blue: 170/255).opacity(0.4), radius: 20)
                    .scaleEffect(logoScale)
                    .opacity(logoOpacity)
                Text("ATLAS AI")
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                    .opacity(logoOpacity)
                Text("AI-Powered Health Assistant")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.white.opacity(0.6))
                    .opacity(logoOpacity)
            }
        }
        .onAppear {
            withAnimation(.spring(response: 0.8, dampingFraction: 0.6)) {
                logoScale = 1.0
                logoOpacity = 1.0
            }
        }
    }
}

// ─── WKWebView with custom scheme handler ───────────────────
struct AtlasWebView: UIViewRepresentable {
    @Binding var isLoading: Bool
    @Binding var loadProgress: Double

    static let backendURL = "https://bisectional-annelle-overgenially.ngrok-free.dev"

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []

        // Register custom scheme handler to serve local files
        if let webAppDir = Bundle.main.url(forResource: "WebApp", withExtension: nil) {
            let handler = LocalFileSchemeHandler(rootDirectory: webAppDir)
            config.setURLSchemeHandler(handler, forURLScheme: "atlas")
            print("[Atlas] ✅ Registered atlas:// scheme for: \(webAppDir.path)")
        } else {
            print("[Atlas] ❌ WebApp directory not found in bundle!")
        }

        // Inject JS before page loads
        let backendURL = AtlasWebView.backendURL
        let earlyJS = WKUserScript(source: """
        // Disable service worker
        if (navigator.serviceWorker) {
            Object.defineProperty(navigator, 'serviceWorker', {
                get: function() {
                    return { register: function() { return Promise.resolve(); }, ready: Promise.resolve({}) };
                }
            });
        }
        // Proxy fetch/XHR for API calls
        var _bURL = '\(backendURL)';
        var _oF = window.fetch;
        window.fetch = function(input, init) {
            var url = (typeof input === 'string') ? input : (input instanceof Request ? input.url : String(input));
            var newUrl = url;
            // Rewrite http://localhost:8000/... to ngrok
            if (url.indexOf('://localhost:8000') !== -1) {
                newUrl = url.replace(/https?:\\/\\/localhost:8000/g, _bURL);
            }
            // Rewrite relative /api/ paths
            else if (url.startsWith('/api/')) {
                newUrl = _bURL + url;
            }
            if (newUrl !== url) {
                init = init || {};
                init.headers = init.headers || {};
                if (init.headers instanceof Headers) {
                    init.headers.set('ngrok-skip-browser-warning', 'true');
                } else {
                    init.headers['ngrok-skip-browser-warning'] = 'true';
                }
                if (typeof input === 'string') { input = newUrl; }
                else { input = new Request(newUrl, init); }
            }
            return _oF.call(this, input, init);
        };
        var _oX = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            if (typeof url === 'string') {
                if (url.indexOf('://localhost:8000') !== -1) {
                    arguments[1] = url.replace(/https?:\\/\\/localhost:8000/g, _bURL);
                } else if (url.startsWith('/api/')) {
                    arguments[1] = _bURL + url;
                }
            }
            var xhr = _oX.apply(this, arguments);
            try { this.setRequestHeader('ngrok-skip-browser-warning', 'true'); } catch(e) {}
            return xhr;
        };
        // Forward JS console to native
        window.onerror = function(msg, url, line) {
            window.webkit.messageHandlers.jsLog.postMessage('ERROR: ' + msg + ' at ' + url + ':' + line);
        };
        var _cL = console.log, _cE = console.error;
        console.log = function() { _cL.apply(console, arguments); try { window.webkit.messageHandlers.jsLog.postMessage('LOG: ' + Array.from(arguments).join(' ')); } catch(e) {} };
        console.error = function() { _cE.apply(console, arguments); try { window.webkit.messageHandlers.jsLog.postMessage('ERR: ' + Array.from(arguments).join(' ')); } catch(e) {} };
        """, injectionTime: .atDocumentStart, forMainFrameOnly: true)
        config.userContentController.addUserScript(earlyJS)
        config.userContentController.add(context.coordinator, name: "jsLog")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.scrollView.bounces = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 10/255, green: 37/255, blue: 64/255, alpha: 1)
        webView.scrollView.backgroundColor = UIColor(red: 10/255, green: 37/255, blue: 64/255, alpha: 1)
        webView.allowsBackForwardNavigationGestures = true
        webView.addObserver(context.coordinator, forKeyPath: #keyPath(WKWebView.estimatedProgress), options: .new, context: nil)

        // Load via custom scheme (NOT file://)
        if let url = URL(string: "atlas://app/index.html") {
            print("[Atlas] 📱 Loading: \(url)")
            webView.load(URLRequest(url: url))
        }

        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
        var parent: AtlasWebView
        init(_ parent: AtlasWebView) { self.parent = parent }

        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            if message.name == "jsLog", let body = message.body as? String {
                print("[Atlas JS] \(body)")
            }
        }

        override func observeValue(forKeyPath keyPath: String?, of object: Any?,
                                   change: [NSKeyValueChangeKey : Any]?, context: UnsafeMutableRawPointer?) {
            if keyPath == "estimatedProgress", let wv = object as? WKWebView {
                DispatchQueue.main.async { self.parent.loadProgress = wv.estimatedProgress }
            }
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            DispatchQueue.main.async { self.parent.isLoading = false }
            print("[Atlas] ✅ Page loaded: \(webView.url?.absoluteString ?? "nil")")
            // Inject CSS with a delay to ensure React has rendered
            webView.evaluateJavaScript("""
            function injectAtlasCSS() {
              var s = document.createElement('style');
              s.id = 'atlas-ios-overrides';
              s.innerHTML = `
                /* === iOS App — Safe Area + Layout Fixes === */

                .app-container {
                  padding-top: 0 !important;
                }

                /* === Top Nav Bar — proper safe area === */
                .premium-chat-nav {
                  padding-top: calc(env(safe-area-inset-top, 47px) + 0.4rem) !important;
                  padding-left: 0.75rem !important;
                  padding-right: 0.75rem !important;
                  padding-bottom: 0.4rem !important;
                  gap: 0.4rem !important;
                }

                .premium-chat-nav .nav-brand-icon {
                  width: 30px !important;
                  height: 30px !important;
                }

                .premium-chat-nav .nav-brand-text {
                  font-size: 1rem !important;
                }

                .premium-chat-nav .nav-action-btn {
                  width: 30px !important;
                  height: 30px !important;
                  border-radius: 8px !important;
                }

                .premium-chat-nav .nav-action-btn svg {
                  width: 14px !important;
                  height: 14px !important;
                }

                .premium-chat-nav .nav-lang-select {
                  padding: 0.25rem 0.5rem !important;
                  font-size: 0.7rem !important;
                  padding-right: 20px !important;
                  border-radius: 8px !important;
                }

                .premium-chat-nav .nav-status-pill {
                  display: none !important;
                }

                .premium-chat-nav .nav-user-pill {
                  padding: 0.2rem 0.4rem 0.2rem 0.2rem !important;
                }

                .premium-chat-nav .nav-user-avatar,
                .premium-chat-nav .nav-user-avatar-fallback {
                  width: 24px !important;
                  height: 24px !important;
                }

                .premium-chat-nav .nav-user-name {
                  display: none !important;
                }

                /* === Symptoms Bar — horizontal scroll === */
                .symptoms-bar {
                  flex-wrap: nowrap !important;
                  overflow-x: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  padding: 0.25rem 0.5rem !important;
                  gap: 0.25rem !important;
                  scrollbar-width: none !important;
                }

                .symptoms-bar::-webkit-scrollbar {
                  display: none !important;
                }

                .urgency-badge-dynamic {
                  flex-shrink: 0 !important;
                  font-size: 0.6rem !important;
                  padding: 0.2rem 0.5rem !important;
                }

                .detected-symptoms-section {
                  flex-shrink: 1 !important;
                  min-width: 0 !important;
                  overflow: hidden !important;
                }

                .symptom-tags-container {
                  flex-wrap: nowrap !important;
                  overflow-x: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  scrollbar-width: none !important;
                }

                .symptom-tags-container::-webkit-scrollbar {
                  display: none !important;
                }

                .symptom-tag {
                  white-space: nowrap !important;
                  flex-shrink: 0 !important;
                  font-size: 0.55rem !important;
                  padding: 0.15rem 0.4rem !important;
                }

                .symptoms-label {
                  flex-shrink: 0 !important;
                  white-space: nowrap !important;
                }

                /* === Diagnosis Panel — horizontal scrollable cards === */
                .diagnosis-panel {
                  max-height: 200px !important;
                  overflow-y: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  margin: 0.25rem 0.35rem !important;
                }

                .diagnosis-list {
                  display: flex !important;
                  flex-wrap: nowrap !important;
                  overflow-x: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  gap: 0.35rem !important;
                  padding: 0.3rem !important;
                  padding-bottom: 6px !important;
                  scroll-snap-type: x mandatory !important;
                }

                .diagnosis-card {
                  min-width: 220px !important;
                  max-width: 280px !important;
                  flex: 0 0 auto !important;
                  scroll-snap-align: start !important;
                }

                .diagnosis-name {
                  white-space: normal !important;
                  font-size: 0.72rem !important;
                }

                .diagnosis-desc {
                  white-space: normal !important;
                  display: -webkit-box !important;
                  -webkit-line-clamp: 2 !important;
                  -webkit-box-orient: vertical !important;
                  overflow: hidden !important;
                  font-size: 0.62rem !important;
                }

                .diagnosis-find-doctor-btn {
                  font-size: 0.7rem !important;
                  padding: 0.4rem 0.5rem !important;
                }

                .diagnosis-disclaimer {
                  font-size: 0.5rem !important;
                }

                /* === Medications Panel — scrollable === */
                .medications-panel {
                  max-height: 90px !important;
                  overflow-y: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  margin: 0.25rem 0.35rem !important;
                }

                .medications-panel.expanded {
                  max-height: 250px !important;
                }

                /* === Chat Messages — better scroll === */
                .chat-container,
                .premium-chat-container {
                  -webkit-overflow-scrolling: touch !important;
                  overflow-y: auto !important;
                }

                /* === Follow-up Questions — horizontal scroll === */
                .follow-up-questions {
                  overflow-x: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  flex-wrap: nowrap !important;
                  scrollbar-width: none !important;
                }

                .follow-up-questions::-webkit-scrollbar {
                  display: none !important;
                }

                .follow-up-btn {
                  white-space: nowrap !important;
                  flex-shrink: 0 !important;
                }

                /* === Quick Symptom Buttons — horizontal scroll === */
                .quick-symptoms {
                  overflow-x: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  flex-wrap: nowrap !important;
                  scrollbar-width: none !important;
                }

                .quick-symptoms::-webkit-scrollbar {
                  display: none !important;
                }

                .quick-symptom-btn {
                  white-space: nowrap !important;
                  flex-shrink: 0 !important;
                }

                /* === Bottom safe area + misc === */
                .premium-chat-footer {
                  padding-bottom: calc(env(safe-area-inset-bottom, 20px) + 0.3rem) !important;
                }

                .pwa-install-banner { display: none !important; }

                /* === Layout fix — ensure input area has space === */

                .premium-chat-card {
                  overflow: visible !important;
                }

                .premium-chat-layout {
                  overflow: visible !important;
                }

                /* === Input Area: 2-row layout === */

                .premium-input-area {
                  display: flex !important;
                  flex-direction: column !important;
                  gap: 8px !important;
                  padding: 10px 12px !important;
                  padding-bottom: calc(env(safe-area-inset-bottom, 20px) + 10px) !important;
                  background: linear-gradient(180deg, rgba(15, 35, 65, 0.98), rgba(8, 22, 45, 0.98)) !important;
                  border-top: 1px solid rgba(102, 126, 234, 0.2) !important;
                  flex-shrink: 0 !important;
                }

                /* Row 1: Toolbar */
                .premium-action-toolbar {
                  display: flex !important;
                  flex-direction: row !important;
                  justify-content: space-evenly !important;
                  align-items: center !important;
                  gap: 6px !important;
                  padding: 4px 0 !important;
                  min-height: 48px !important;
                }

                .premium-action-toolbar .toolbar-btn {
                  display: flex !important;
                  flex-direction: column !important;
                  align-items: center !important;
                  justify-content: center !important;
                  gap: 3px !important;
                  padding: 6px 10px !important;
                  min-width: 52px !important;
                  min-height: 44px !important;
                  background: linear-gradient(135deg, rgba(40, 70, 120, 0.8), rgba(30, 58, 100, 0.8)) !important;
                  border: 1px solid rgba(102, 126, 234, 0.35) !important;
                  border-radius: 12px !important;
                  color: #B8C9E8 !important;
                  -webkit-tap-highlight-color: transparent !important;
                }

                .premium-action-toolbar .toolbar-btn.active {
                  background: linear-gradient(135deg, rgba(0, 212, 170, 0.3), rgba(0, 184, 148, 0.25)) !important;
                  border-color: rgba(0, 212, 170, 0.6) !important;
                  color: #00D4AA !important;
                }

                .premium-action-toolbar .toolbar-btn svg {
                  width: 18px !important;
                  height: 18px !important;
                  color: inherit !important;
                }

                .premium-action-toolbar .toolbar-btn span {
                  font-size: 9px !important;
                  font-weight: 600 !important;
                  color: inherit !important;
                }

                /* Row 2: Input + Send */
                .premium-input-wrapper {
                  display: flex !important;
                  flex-direction: row !important;
                  align-items: center !important;
                  gap: 10px !important;
                  padding: 4px !important;
                  background: transparent !important;
                  border: none !important;
                  border-radius: 0 !important;
                  box-shadow: none !important;
                }

                .premium-input-wrapper .input-field {
                  flex: 1 !important;
                  min-width: 0 !important;
                  padding: 12px 18px !important;
                  border: 2px solid rgba(102, 126, 234, 0.4) !important;
                  background: rgba(25, 50, 90, 0.9) !important;
                  border-radius: 26px !important;
                  font-size: 16px !important;
                  color: #E2E8F0 !important;
                  outline: none !important;
                  -webkit-appearance: none !important;
                }

                .premium-input-wrapper .input-field::placeholder {
                  color: #8899BB !important;
                }

                .premium-input-wrapper .p-action-btn.send {
                  width: 46px !important;
                  height: 46px !important;
                  border-radius: 50% !important;
                  flex-shrink: 0 !important;
                  display: flex !important;
                  align-items: center !important;
                  justify-content: center !important;
                  background: linear-gradient(135deg, #00D4AA, #00B894) !important;
                  color: #fff !important;
                  border: none !important;
                  box-shadow: 0 3px 14px rgba(0, 212, 170, 0.4) !important;
                }

                .premium-input-wrapper .p-action-btn.send:disabled {
                  opacity: 0.3 !important;
                  box-shadow: none !important;
                }

                .premium-input-wrapper .p-action-btn.cancel-req {
                  width: 46px !important;
                  height: 46px !important;
                  border-radius: 50% !important;
                  flex-shrink: 0 !important;
                  display: flex !important;
                  align-items: center !important;
                  justify-content: center !important;
                  background: linear-gradient(135deg, #EF4444, #DC2626) !important;
                  color: #fff !important;
                  border: none !important;
                }

                .premium-input-wrapper .p-action-btn.stop {
                  width: 46px !important;
                  height: 46px !important;
                  border-radius: 50% !important;
                  flex-shrink: 0 !important;
                  background: rgba(239, 68, 68, 0.2) !important;
                  color: #EF4444 !important;
                  border: 1px solid rgba(239, 68, 68, 0.4) !important;
                }

                /* === Body Selector Modal Fix === */
                .body-selector-overlay {
                  padding: 0 !important;
                  align-items: stretch !important;
                  justify-content: stretch !important;
                }

                .body-selector-modal,
                .body-selector-modal.body-selector-large {
                  width: 100% !important;
                  max-width: 100% !important;
                  height: 100% !important;
                  max-height: 100% !important;
                  border-radius: 0 !important;
                  overflow: hidden !important;
                  display: flex !important;
                  flex-direction: column !important;
                }

                .body-selector-header {
                  flex-shrink: 0 !important;
                  padding: calc(env(safe-area-inset-top, 47px) + 0.3rem) 0.75rem 0.3rem !important;
                }

                .body-selector-header h2 {
                  font-size: 1rem !important;
                  margin: 0 !important;
                }

                .body-selector-header p {
                  font-size: 0.65rem !important;
                  margin: 2px 0 0 !important;
                }

                .body-selector-header small {
                  font-size: 0.6rem !important;
                }

                .body-svg-container {
                  flex: 1 1 0% !important;
                  min-height: 0 !important;
                  max-height: none !important;
                  overflow: auto !important;
                  -webkit-overflow-scrolling: touch !important;
                  flex-direction: row !important;
                  align-items: flex-start !important;
                  padding: 0.25rem !important;
                  gap: 0.2rem !important;
                }

                .body-view {
                  flex: 1 !important;
                  max-width: 50% !important;
                  min-width: 0 !important;
                }

                .body-view .view-label {
                  font-size: 0.55rem !important;
                  padding: 2px 8px !important;
                  margin-bottom: 2px !important;
                }

                .body-svg {
                  width: 100% !important;
                  height: auto !important;
                  max-height: none !important;
                }

                .body-selector-selected {
                  flex-shrink: 0 !important;
                  max-height: 44px !important;
                  overflow-y: auto !important;
                  padding: 0.2rem 0.5rem !important;
                }

                .body-selector-selected strong {
                  font-size: 0.65rem !important;
                  margin-bottom: 0.2rem !important;
                }

                .selected-part-tag {
                  font-size: 0.6rem !important;
                  padding: 0.1rem 0.4rem !important;
                }

                .body-selector-actions {
                  flex-shrink: 0 !important;
                  flex-direction: row !important;
                  padding: 0.35rem 0.5rem !important;
                  padding-bottom: calc(0.35rem + env(safe-area-inset-bottom, 20px)) !important;
                  gap: 0.3rem !important;
                }

                .body-selector-actions button {
                  padding: 0.45rem 0.25rem !important;
                  font-size: 0.7rem !important;
                }

                /* === SpecialistFinder / other modals === */
                .sf-overlay {
                  padding-top: env(safe-area-inset-top, 47px) !important;
                  padding-bottom: env(safe-area-inset-bottom, 20px) !important;
                }

                .sf-modal {
                  max-height: 85vh !important;
                }

                .modal-overlay {
                  padding-top: env(safe-area-inset-top, 47px) !important;
                  padding-bottom: env(safe-area-inset-bottom, 20px) !important;
                }
              `;
              document.head.appendChild(s);
              console.log('[Atlas iOS] CSS injected, input-area exists: ' + !!document.querySelector('.premium-input-area'));
            }

            // Inject immediately AND after delays (React may re-render)
            injectAtlasCSS();
            setTimeout(injectAtlasCSS, 500);
            setTimeout(injectAtlasCSS, 1500);
            setTimeout(injectAtlasCSS, 3000);
            console.log('[Atlas iOS] CSS injected. Root children: ' + document.getElementById('root').children.length);
            """)
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            print("[Atlas] 🔄 Loading...")
            DispatchQueue.main.async { self.parent.isLoading = true }
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            print("[Atlas] ❌ Failed: \(error.localizedDescription)")
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("[Atlas] ❌ Provisional fail: \(error.localizedDescription)")
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if let url = navigationAction.request.url {
                // Allow our custom scheme and common web URLs
                if url.scheme == "atlas" || url.scheme == "about" || url.scheme == "blob" {
                    decisionHandler(.allow)
                    return
                }
                // Allow HTTPS resources (fonts, CDN, Google auth)
                if url.scheme == "https" || url.scheme == "http" {
                    if navigationAction.navigationType == .linkActivated {
                        UIApplication.shared.open(url)
                        decisionHandler(.cancel)
                        return
                    }
                    decisionHandler(.allow)
                    return
                }
            }
            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView,
                     requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                     initiatedByFrame frame: WKFrameInfo,
                     type: WKMediaCaptureType,
                     decisionHandler: @escaping (WKPermissionDecision) -> Void) {
            decisionHandler(.grant)
        }

        func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                     initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
            completionHandler()
        }

        func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                     initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
            completionHandler(true)
        }

        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                     for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            if navigationAction.targetFrame == nil { webView.load(navigationAction.request) }
            return nil
        }
    }
}

#Preview {
    ContentView()
}
