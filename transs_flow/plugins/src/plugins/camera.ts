	import { Plugins, CameraResultType, CameraSource } from '@capacitor/core';
 
const { Camera } = Plugins;
 
export interface CameraOptions {
  quality?: number;
  allowEditing?: boolean;
  resultType?: CameraResultType;
  source?: CameraSource;
  saveToGallery?: boolean;
}
 
export class CameraPlugin {
  static async getPhoto(options: CameraOptions = {}) {
    const result = await Camera.getPhoto({
      quality: 90,
      allowEditing: true,
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
      saveToGallery: true,
      ...options
    });
    
    return result;
  }
 
  static async getFromGallery() {
    return await this.getPhoto({
      source: CameraSource.Photos
    });
  }
}