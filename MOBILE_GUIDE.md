# 📱 Build Native Apps with Capacitor

Convert your web app → iOS/Android apps in under an hour. Publish to App Store / Play Store.

## Why Capacitor?

- **No rewriting code** – Your HTML/JS app stays as-is
- **Native features** – Access device camera, mic, storage, push notifications
- **Real apps** – True .ipa (iOS) and .apk/.aab (Android) files
- **One codebase** – Web + iOS + Android from the same source
- **Open source & free** – Community-friendly, no vendor lock-in

## Prerequisites

- Node.js (v16+) and npm
- For iOS: macOS + Xcode
- For Android: Android Studio
- Apple Developer account ($99/year) or Google Play account ($25 one-time)

## Step 1: Prepare Your Web App (5 minutes)

Your web app files must be in a clean directory (`dist/`):

```bash
cd client
npm install
npm run build
```

This copies `index.html` and `app.js` to `dist/`.

**Check:** You should now have:
```
client/
  dist/
    index.html
    app.js
  package.json
  capacitor.config.ts
  ...
```

## Step 2: Initialize Capacitor (1 minute)

Already done! The repo includes:
- `package.json` – Dependencies
- `capacitor.config.ts` – Config file

Add native platforms:

```bash
cd client
npx cap add ios
npx cap add android
```

This creates:
- `ios/` folder (Xcode project)
- `android/` folder (Android Studio project)

## Step 3: Deploy Your Backend + Frontend (10 minutes)

**Critical:** Mobile apps need a **live URL** to reach your backend.

### Option A: Deploy Full Stack to Render (Recommended)

1. Create `render.yaml` in repo root:
```yaml
services:
  - type: web
    name: ai-dungeon-master
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server.main:app --host 0.0.0.0 --port 8000
    staticFiles:
      - path: client
        routes:
          - path: /*
            destination: /index.html
envVars:
  - key: OPENAI_API_KEY
    scope: all
    sync: false
```

2. Push to GitHub
3. Go to render.com → New → Web Service → Connect repo
4. Set `OPENAI_API_KEY` in Render environment
5. Deploy

**Your backend lives at:** `https://your-app.render.com`

### Option B: Deploy Frontend Separately (Vercel/Netlify)

If you prefer separate hosting:

1. Deploy frontend to Vercel/Netlify
2. Deploy server to Render/Fly.io/Railway separately
3. In `client/capacitor.config.ts`, point to your backend URL:

```ts
server: {
  url: 'https://your-backend.render.com',
  cleartext: false
}
```

## Step 4: Configure Capacitor with Your URL (2 minutes)

Open `client/capacitor.config.ts`:

```ts
server: {
  url: 'https://your-app.render.com',  // Your live backend URL
  cleartext: false                       // true only in development
}
```

Then sync:

```bash
npx cap sync
```

## Step 5a: Build for iOS (10 minutes)

1. Open Xcode project:
   ```bash
   npx cap open ios
   ```

2. Select simulator or connected iPhone
3. Click **Play** button (top left)
4. Wait for build

That's it. App runs.

### Troubleshooting iOS

| Issue | Fix |
|-------|-----|
| "Cannot find module" | Run `npm install` again, then `npx cap sync` |
| WebSocket connection fails | Check URL in `capacitor.config.ts` |
| Microphone won't work | See "Permissions" section below |
| App can't reach backend | Make sure backend URL is public (check Render logs) |

## Step 5b: Build for Android (10 minutes)

1. Open Android Studio project:
   ```bash
   npx cap open android
   ```

2. Create emulator (AVD Manager) or connect phone (USB debugging on)
3. Click **Run** button
4. Wait for build

Done.

### Troubleshooting Android

Same as iOS (see above) + check USB drivers installed.

## Microphone Permissions (Important!)

Voice input won't work without proper permissions.

### iOS
1. Open `ios/App/App/Info.plist`
2. Add these keys:
```xml
<key>NSMicrophoneUsageDescription</key>
<string>AI Dungeon Master needs microphone access for voice input</string>
<key>NSCameraUsageDescription</key>
<string>AI Dungeon Master uses camera for QR code scanning</string>
```

3. Rebuild in Xcode

### Android
Permissions are auto-added. Users will see a prompt when app first runs.

## Publish to App Stores

### iOS: App Store

1. Create Apple Developer account (developer.apple.com) – $99/year
2. In Xcode:
   - Set bundle ID: `com.yourcompany.aidm`
   - Set version number
   - Add icon (1024x1024 PNG)
3. Product → Archive
4. Organizer → Validate → Upload
5. Go to App Store Connect → Manage metadata → Submit

Takes 24–48 hours for review.

### Android: Google Play

1. Create Google Play Developer account (play.google.com) – $25 one-time
2. In Android Studio:
   - Set app signing key (keystore)
   - Build Release APK/AAB
3. Upload to Google Play Console
4. Add icon, screenshots, description
5. Submit

Takes 2–4 hours for review.

## Fork & Create Your Own App

This is the beauty of the approach:

1. Fork this repo
2. Change `appName` and `appId` in `capacitor.config.ts`:
   ```ts
   appId: 'com.yourcompany.yourname'
   appName: 'My Epic D&D Companion'
   ```
3. Add your icon / splash screen
4. Deploy & publish

Your branded app, live in app stores.

## Next Steps (Roadmap)

These are easier now that you have native apps:

- **Push Notifications** – Session reminders
- **Camera plugin** – Direct QR scanning (instead of browser)
- **Offline cache** – Play without WiFi (with limitations)
- **Ambient sounds** – Rain, tavern chatter, battle music

See [README.md](../README.md) for full roadmap.

## Questions?

- Capacitor docs: https://capacitorjs.com
- Render deployment: https://render.com/docs
- iOS signing: https://developer.apple.com
- Android signing: https://developer.android.com/studio/publish/app-signing
