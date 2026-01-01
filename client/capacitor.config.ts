import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.aidm',
  appName: 'AI Dungeon Master',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https',
    // Update this to your deployed backend URL
    // Example: https://your-app.render.com
    url: 'http://localhost:8000',
    cleartext: true // Only for development; set to false in production
  },
  plugins: {
    // Future plugins (e.g., PushNotifications, Camera)
  }
};

export default config;
