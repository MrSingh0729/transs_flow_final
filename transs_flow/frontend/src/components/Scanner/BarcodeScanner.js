import React, { useState, useEffect, useRef } from 'react';
import Html5QrcodePlugin from 'html5-qrcode';
import { HapticsPlugin } from '../../plugins';
 
const BarcodeScanner = ({ onScan, onError, fps = 10, qrbox = 250 }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const scannerRef = useRef(null);
  const html5QrCodeRef = useRef(null);
 
  const startScanning = async () => {
    try {
      setIsScanning(true);
      setError(null);
      HapticsPlugin.impact('medium');
      
      const html5QrCode = new Html5Qrcode("reader");
      html5QrCodeRef.current = html5QrCode;
      
      await html5QrCode.start(
        { facingMode: "environment" },
        { fps, qrbox },
        (decodedText, decodedResult) => {
          HapticsPlugin.notification('success');
          if (onScan) onScan(decodedText);
          stopScanning();
        },
        (errorMessage) => {
          // Ignore scan errors
        }
      );
    } catch (err) {
      console.error('Error starting scanner:', err);
      setError('Failed to start camera. Please check permissions.');
      HapticsPlugin.notification('error');
      setIsScanning(false);
      if (onError) onError(err);
    }
  };
 
  const stopScanning = async () => {
    try {
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        await html5QrCodeRef.current.stop();
        html5QrCodeRef.current = null;
      }
    } catch (err) {
      console.error('Error stopping scanner:', err);
    } finally {
      setIsScanning(false);
    }
  };
 
  useEffect(() => {
    return () => {
      if (isScanning) {
        stopScanning();
      }
    };
  }, [isScanning]);
 
  return (
    <div className="barcode-scanner">
      <div className="scanner-container">
        <div id="reader" className="scanner-view"></div>
        
        {error && (
          <div className="scanner-error">
            <i className="fas fa-exclamation-triangle mr-2"></i>
            {error}
          </div>
        )}
      </div>
      
      <div className="scanner-controls">
        {!isScanning ? (
          <button
            onClick={startScanning}
            className="scan-button"
          >
            <i className="fas fa-qrcode mr-2"></i>
            Start Scanning
          </button>
        ) : (
          <button
            onClick={stopScanning}
            className="stop-button"
          >
            <i className="fas fa-stop mr-2"></i>
            Stop Scanning
          </button>
        )}
      </div>
    </div>
  );
};
 
export default BarcodeScanner;