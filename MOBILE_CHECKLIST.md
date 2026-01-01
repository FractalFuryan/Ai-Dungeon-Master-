# 🚀 Mobile App Checklist

Everything you need to ship native iOS & Android apps. ✅

## Quick Reference

| Step | Command | Time | Notes |
|------|---------|------|-------|
| Install deps | `cd client && npm install` | 2 min | One-time setup |
| Build dist | `npm run build` | 1 min | Prepares assets |
| Add platforms | `npx cap add ios && npx cap add android` | 2 min | Creates native folders |
| Deploy backend | Push to Render + set `OPENAI_API_KEY` | 10 min | Gets you a live URL |
| Update config | Edit `capacitor.config.ts` URL | 1 min | Point to your backend |
| Sync assets | `npx cap sync` | 1 min | Copy web → native |
| Build iOS | `npx cap open ios` → Play in Xcode | 10 min | Works on simulator/device |
| Build Android | `npx cap open android` → Run in Studio | 10 min | Works on emulator/device |

## Pre-Publish Checklist

### iOS
- [ ] Bundle ID set in Xcode (`com.yourcompany.aidm`)
- [ ] App icon (1024×1024 PNG) added
- [ ] Version number set
- [ ] Microphone permissions in `Info.plist`
- [ ] Privacy Policy URL ready
- [ ] Screenshots (3–5, 1125×2436px) for App Store
- [ ] Test on real iPhone

### Android
- [ ] App ID set in `capacitor.config.ts`
- [ ] Icon (512×512 PNG) added
- [ ] Version code incremented
- [ ] Signing key created (keystore)
- [ ] Microphone permissions included
- [ ] Privacy Policy URL ready
- [ ] Screenshots (2–8, 1080×1920px) for Play Store
- [ ] Test on real phone

## Production Settings

Once deploying for real, update `capacitor.config.ts`:

```ts
server: {
  url: 'https://your-production-url.com',
  cleartext: false  // NOT for development
}
```

And `client/package.json`:
```json
"version": "1.0.0"  // Use semver
```

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Module not found" | `npm install && npx cap sync` |
| WebSocket fails | Check backend URL is public + supports WS |
| Microphone permission denied | Add permissions to `Info.plist` (iOS) or wait for OS prompt (Android) |
| App loads blank white screen | Check browser console in Capacitor DevTools |
| Can't connect to localhost from device | Must deploy to public URL (Render.com) |

## Roadmap (Nice to Have Next)

- [ ] Push notifications (session reminders)
- [ ] Camera QR scanning (native, not browser)
- [ ] Offline mode (limited functionality without connection)
- [ ] App store badges in README

## Resources

- [Full MOBILE_GUIDE.md](MOBILE_GUIDE.md) – Step-by-step walkthrough
- [Capacitor docs](https://capacitorjs.com) – Official guide
- [Render deployment](https://render.com/docs) – Backend hosting
- [App Store Connect](https://appstoreconnect.apple.com) – iOS publishing
- [Google Play Console](https://play.google.com/console) – Android publishing

---

**Ready?** Start with: `cd client && npm install`

The path to app stores starts here. 🚀📱⚔️
