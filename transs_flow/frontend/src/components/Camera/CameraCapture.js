import React, { useState } from 'react';
import { CameraPlugin } from '../../plugins';
import { HapticsPlugin } from '../../plugins';
import { compressImage } from '../../utils/imageCompressor';
import { CameraResultType } from '@capacitor/core';

const CameraCapture = ({ onCapture, onError }) => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const openCamera = async () => {
    try {
      setIsProcessing(true);
      await HapticsPlugin.impact('medium');

      const photo = await CameraPlugin.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Uri,
      });

      const imagePath = photo?.webPath || photo?.path || photo?.dataUrl;
      if (!imagePath) throw new Error('No image captured');

      setCapturedImage(imagePath);
      await HapticsPlugin.notification('success');
      if (onCapture) onCapture(imagePath);
    } catch (error) {
      console.error('Camera error:', error);
      await HapticsPlugin.notification('error');
      if (onError) onError(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const openGallery = async () => {
    try {
      setIsProcessing(true);
      await HapticsPlugin.impact('medium');

      const photo = await CameraPlugin.getFromGallery();
      const imagePath = photo?.webPath || photo?.path || photo?.dataUrl;
      if (!imagePath) throw new Error('No image selected');

      setCapturedImage(imagePath);
      await HapticsPlugin.notification('success');
      if (onCapture) onCapture(imagePath);
    } catch (error) {
      console.error('Gallery error:', error);
      await HapticsPlugin.notification('error');
      if (onError) onError(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const compressAndCapture = async () => {
    if (!capturedImage) return;

    try {
      setIsProcessing(true);
      const response = await fetch(capturedImage);
      const blob = await response.blob();

      const compressedFile = await compressImage(blob, {
        maxSizeMB: 0.5,
        maxWidthOrHeight: 1280,
      });

      const compressedUrl = URL.createObjectURL(compressedFile);
      setCapturedImage(compressedUrl);

      if (onCapture) onCapture(compressedUrl);
      await HapticsPlugin.notification('success');
    } catch (error) {
      console.error('Compression error:', error);
      await HapticsPlugin.notification('error');
    } finally {
      setIsProcessing(false);
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    if (onCapture) onCapture(null);
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      {!capturedImage ? (
        <div className="flex space-x-4">
          <button
            onClick={openCamera}
            disabled={isProcessing}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 disabled:opacity-50"
          >
            <i className="fas fa-camera mr-2"></i> Take Photo
          </button>

          <button
            onClick={openGallery}
            disabled={isProcessing}
            className="bg-green-600 text-white px-4 py-2 rounded-lg shadow hover:bg-green-700 disabled:opacity-50"
          >
            <i className="fas fa-images mr-2"></i> Choose from Gallery
          </button>
        </div>
      ) : (
        <div className="w-full flex flex-col items-center space-y-3">
          <img
            src={capturedImage}
            alt="Captured"
            className="rounded-xl shadow-md w-full max-w-sm object-cover"
          />

          <div className="flex space-x-4">
            <button
              onClick={compressAndCapture}
              disabled={isProcessing}
              className="bg-yellow-500 text-white px-4 py-2 rounded-lg shadow hover:bg-yellow-600 disabled:opacity-50"
            >
              <i className="fas fa-compress mr-2"></i> Compress
            </button>

            <button
              onClick={retakePhoto}
              disabled={isProcessing}
              className="bg-red-500 text-white px-4 py-2 rounded-lg shadow hover:bg-red-600 disabled:opacity-50"
            >
              <i className="fas fa-redo mr-2"></i> Retake
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CameraCapture;
