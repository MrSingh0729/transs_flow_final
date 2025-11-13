import { Plugins } from '@capacitor/core';
 
const { BackgroundTask } = Plugins;
 
export class BackgroundSyncPlugin {
  static async beforeExit(callback: () => Promise<void>) {
    await BackgroundTask.beforeExit(callback);
  }
 
  static async async(callback: () => Promise<void>) {
    await BackgroundTask.async(callback);
  }
}