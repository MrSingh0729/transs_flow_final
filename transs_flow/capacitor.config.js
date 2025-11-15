const { CapacitorConfig } = require('@capacitor/cli');

const config = CapacitorConfig({
  webDir: 'www',
  bundledWebRuntime: false,
  plugins: {
    CapacitorHttp: {
      enabled: true
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_notification',
      iconColor: '#488AFF',
      sound: 'beep.wav'
    },
    Camera: {
      android: {
        enableZoom: true,
        autoFocus: true,
        exposureCompensation: 0
      },
      ios: {
        presentationStyle: 'popover'
      }
    },
    Filesystem: {
      permissions: ['storage'],
    },
    Haptics: {
      vibrate: true
    }
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    plugins: {
      CapacitorHttp: {
        enabled: true
      }
    }
  },
  ios: {
    allowMixedContent: true,
    webContentsDebuggingEnabled: true,
    plugins: {
      CapacitorHttp: {
        enabled: true
      }
    }
  }
});

module.exports = config;