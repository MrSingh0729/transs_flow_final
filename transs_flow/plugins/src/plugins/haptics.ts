import { Plugins } from '@capacitor/core';
 
const { Haptics } = Plugins;
 
export class HapticsPlugin {
  static async impact(style: 'light' | 'medium' | 'heavy') {
    await Haptics.impact({
      style
    });
  }
 
  static async notification(type: 'success' | 'warning' | 'error') {
    await Haptics.notification({
      type
    });
  }
 
  static async vibrate() {
    await Haptics.vibrate();
  }
 
  static async selectionStart() {
    await Haptics.selectionStart();
  }
 
  static async selectionChanged() {
    await Haptics.selectionChanged();
  }
 
  static async selectionEnd() {
    await Haptics.selectionEnd();
  }
}