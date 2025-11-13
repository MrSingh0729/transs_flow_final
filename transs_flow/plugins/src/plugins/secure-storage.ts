	import { Plugins } from '@capacitor/core';
 
const { Storage } = Plugins;
 
export interface SecureStorageOptions {
  key: string;
  value: string;
}
 
export class SecureStorage {
  static async set(options: SecureStorageOptions): Promise<void> {
    await Storage.set({
      key: options.key,
      value: options.value
    });
  }
 
  static async get(key: string): Promise<string | null> {
    const { value } = await Storage.get({ key });
    return value;
  }
 
  static async remove(key: string): Promise<void> {
    await Storage.remove({ key });
  }
 
  static async clear(): Promise<void> {
    await Storage.clear();
  }
}