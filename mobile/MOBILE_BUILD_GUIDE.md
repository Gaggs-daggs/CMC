# 📱 Atlas — Mobile App Build Guide

## Project Structure

```
mobile/
├── ios/
│   └── Atlas/
│       ├── Atlas.xcodeproj/     ← Open this in Xcode
│       └── Atlas/
│           ├── AtlasApp.swift    ← App entry point
│           ├── ContentView.swift   ← WKWebView + Splash screen
│           ├── Info.plist          ← Permissions & config
│           └── Assets.xcassets/    ← App icon + splash logo
│
├── android/
│   ├── build.gradle
│   ├── settings.gradle
│   └── app/
│       ├── build.gradle           ← Dependencies + TWA config
│       ├── proguard-rules.pro
│       └── src/main/
│           ├── AndroidManifest.xml ← TWA launcher + permissions
│           └── res/
│               ├── drawable/       ← Splash logo
│               ├── mipmap-*/       ← Launcher icons (all densities)
│               ├── values/         ← Theme, colors, strings
│               └── xml/            ← File provider paths
```

---

## 🍎 iOS — Build & Submit

### Prerequisites
- **Xcode 15+** (download from Mac App Store)
- **Apple Developer Account** ($99/year) — https://developer.apple.com

### Steps

1. **Open the project in Xcode:**
   ```bash
   open /Users/gugank/CMC/mobile/ios/Atlas/Atlas.xcodeproj
   ```

2. **Set your production URL** in `ContentView.swift`:
   ```swift
   // Change this line to your deployed URL:
   static let appURL = URL(string: "https://atlas.vercel.app")!
   ```

3. **Configure signing:**
   - Select the "Atlas" target → Signing & Capabilities
   - Choose your Apple Developer Team
   - Xcode auto-generates provisioning profiles

4. **Test on device:**
   - Connect your iPhone via USB
   - Select your device as build target
   - Press ⌘R to build & run

5. **Submit to App Store:**
   - Product → Archive
   - Distribute App → App Store Connect
   - Fill in App Store listing (description, screenshots, etc.)
   - Submit for review

### Key Features
- ✅ Native splash screen with Atlas logo
- ✅ Camera/Mic permissions (prescription photos, voice input)
- ✅ Swipe back/forward navigation
- ✅ Loading progress bar
- ✅ Dark theme matching PWA
- ✅ Safe area handling (notch, home indicator)
- ✅ External links open in Safari
- ✅ Google OAuth works in-app

---

## 🤖 Android — Build & Submit

### Prerequisites
- **Android Studio** — https://developer.android.com/studio
- **Google Play Console** ($25 one-time) — https://play.google.com/console

### Steps

1. **Open in Android Studio:**
   ```bash
   # Open Android Studio → File → Open → select:
   /Users/gugank/CMC/mobile/android/
   ```

2. **Set your production URL** in:
   - `app/build.gradle` → `manifestPlaceholders`
   - `app/src/main/res/values/strings.xml` → `asset_statements`

3. **Generate Digital Asset Links** (required for TWA):
   ```bash
   # After signing the APK, get your SHA-256 fingerprint:
   keytool -list -v -keystore your-keystore.jks | grep SHA256
   
   # Add this file to your web server at:
   # https://atlas.vercel.app/.well-known/assetlinks.json
   ```
   
   Content of `assetlinks.json`:
   ```json
   [{
     "relation": ["delegate_permission/common.handle_all_urls"],
     "target": {
       "namespace": "android_app",
       "package_name": "com.atlas.health",
       "sha256_cert_fingerprints": ["YOUR_SHA256_FINGERPRINT"]
     }
   }]
   ```

4. **Build APK:**
   - Build → Generate Signed Bundle/APK
   - Choose "Android App Bundle"
   - Create a new keystore (save this safely!)
   - Build Release

5. **Submit to Play Store:**
   - Go to Google Play Console
   - Create new app → "Atlas AI"
   - Upload the .aab file
   - Fill in listing, screenshots, privacy policy
   - Submit for review

### Key Features
- ✅ TWA (Trusted Web Activity) — fullscreen, no browser chrome
- ✅ Splash screen with Atlas logo on dark background
- ✅ Deep linking to atlas.vercel.app
- ✅ Camera/Mic permissions
- ✅ Dark theme matching PWA
- ✅ Adaptive icons (round + square)

---

## ⚠️ Before Submitting — Checklist

### Deploy Your Web App First
Both iOS and Android wrappers load your PWA from a URL. You need:
1. Deploy frontend to **Vercel/Netlify** (e.g., `atlas.vercel.app`)
2. Deploy backend to **Render/Railway** (e.g., `atlas-api.onrender.com`)
3. Update the URL in both mobile apps

### App Store Requirements
| Requirement | iOS | Android |
|-------------|-----|---------|
| Developer Account | $99/year | $25 one-time |
| Privacy Policy URL | Required | Required |
| Screenshots | 6.5" + 5.5" iPhone | Phone + Tablet |
| Review Time | 1-3 days | 1-7 days |
| Age Rating | Required | Required |

### Privacy Policy
Since the app handles health data, you'll need a privacy policy. Create one at:
- https://app-privacy-policy-generator.firebaseapp.com/
- Or use https://www.termsfeed.com/

---

## 🚀 Quick Test (Without App Store)

### iOS — TestFlight
1. Archive in Xcode
2. Upload to App Store Connect
3. Add testers via TestFlight
4. They get a link to install

### Android — Direct APK
1. Build → Build APK
2. Share the `.apk` file
3. Users enable "Install from Unknown Sources"
4. Install directly
