// ============================================================
// Atlas — iOS App Entry Point (SwiftUI + WKWebView)
// Wraps the Atlas PWA in a native iOS shell
// ============================================================

import SwiftUI

@main
struct AtlasApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .ignoresSafeArea(.all, edges: .bottom)
                .preferredColorScheme(.dark)
        }
    }
}
