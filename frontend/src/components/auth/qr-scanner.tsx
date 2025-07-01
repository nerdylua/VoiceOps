'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { CheckCircle, AlertCircle, Shield } from 'lucide-react';

interface QRScannerProps {
  onScanSuccess: (data: string) => void;
  onScanError: (error: string) => void;
}

declare global {
  interface Window {
    Html5Qrcode: new (elementId: string) => {
      start: (config: unknown, options: unknown, onSuccess: (decodedText: string, decodedResult: unknown) => void, onError: (error: string) => void) => Promise<void>;
      stop: () => Promise<void>;
      clear: () => void;
    };
  }
}

export function QRScanner({ onScanSuccess, onScanError }: QRScannerProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [needsPermission, setNeedsPermission] = useState(false);
  const html5QrcodeScannerRef = useRef<{
    start: (config: unknown, options: unknown, onSuccess: (decodedText: string, decodedResult: unknown) => void, onError: (error: string) => void) => Promise<void>;
    stop: () => Promise<void>;
    clear: () => void;
  } | null>(null);
  const elementId = 'qr-reader';
  const isInitializingRef = useRef(false);

  useEffect(() => {
    // Prevent multiple initializations
    if (isInitializingRef.current) return;
    
    initializeScanner();
    
    return () => {
      cleanup();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cleanup = async () => {
    try {
      // Stop the QR scanner first
      if (html5QrcodeScannerRef.current) {
        await html5QrcodeScannerRef.current.stop();
        html5QrcodeScannerRef.current.clear();
      }
      
      // Stop all active video tracks
      await navigator.mediaDevices.enumerateDevices()
        .then(() => {
          // Get all video elements that might have active streams
          const videoElements = document.querySelectorAll('video');
          videoElements.forEach(video => {
            if (video.srcObject) {
              const stream = video.srcObject as MediaStream;
              stream.getTracks().forEach(track => track.stop());
            }
          });
        })
        .catch(() => {});
        
    } catch {
      // Silent cleanup
    }
    
    html5QrcodeScannerRef.current = null;
    setIsScanning(false);
    isInitializingRef.current = false;
  };

  const requestPermissionAndStart = async () => {
    try {
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access is not supported in this browser');
      }

      // Request camera permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      
      // Stop the stream immediately - we just needed permission
      stream.getTracks().forEach(track => track.stop());
      
      // Permission granted, start scanner
      startScanner();
      
    } catch (err: unknown) {
      const error = err as { name?: string };
      if (error.name === 'NotAllowedError') {
        setNeedsPermission(true);
        setError('Camera permission is required to scan QR codes');
      } else if (error.name === 'NotFoundError') {
        setError('No camera found on this device');
      } else {
        setError('Failed to access camera');
      }
      onScanError('Camera access failed');
      isInitializingRef.current = false;
    }
  };

  const initializeScanner = useCallback(async () => {
    if (isInitializingRef.current) return;
    isInitializingRef.current = true;

    try {
      // Clear any existing scanner first
      await cleanup();
      
      if (!window.Html5Qrcode) {
        const script = document.createElement('script');
        script.src = '/html5-qrcode.min.js';
        
        await new Promise<void>((resolve, reject) => {
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load library'));
          document.head.appendChild(script);
        });
      }
      
      setIsLoading(false);
      await requestPermissionAndStart();
    } catch {
      setError('Failed to initialize scanner');
      setIsLoading(false);
      isInitializingRef.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startScanner = async () => {
    if (isScanning || !window.Html5Qrcode || html5QrcodeScannerRef.current) return;
    
    try {
      setError('');
      
      // Clear the element content first
      const element = document.getElementById(elementId);
      if (element) {
        element.innerHTML = '';
      }
      
      const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      };
      
      const html5QrcodeScanner = new window.Html5Qrcode(elementId);
      html5QrcodeScannerRef.current = html5QrcodeScanner;
      
      await html5QrcodeScanner.start(
        { facingMode: "environment" },
        config,
        handleScanSuccess,
        handleScanError
      );
      
      setIsScanning(true);
      isInitializingRef.current = false;
      
    } catch {
      setError('Unable to start camera');
      setIsScanning(false);
      html5QrcodeScannerRef.current = null;
      isInitializingRef.current = false;
      onScanError('Failed to start scanner');
    }
  };

  const handleScanSuccess = async (decodedText: string) => {
    if (decodedText === 'http://en.m.wikipedia.org') {
      setSuccess(true);
      setIsScanning(false);
      
      // Immediately and forcefully stop all camera operations
      try {
        // Stop the scanner first
        if (html5QrcodeScannerRef.current) {
          await html5QrcodeScannerRef.current.stop();
          html5QrcodeScannerRef.current.clear();
          html5QrcodeScannerRef.current = null;
        }
        
        // Find and stop all video streams in the scanner element
        const scannerElement = document.getElementById(elementId);
        if (scannerElement) {
          const videoElements = scannerElement.querySelectorAll('video');
          videoElements.forEach(video => {
            if (video.srcObject) {
              const stream = video.srcObject as MediaStream;
              stream.getTracks().forEach(track => {
                track.stop();
                track.enabled = false;
              });
              video.srcObject = null;
            }
            // Remove the video element
            video.remove();
          });
          // Clear the scanner element completely
          scannerElement.innerHTML = '';
        }
        
        // Stop any remaining global video tracks
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            stream.getTracks().forEach(track => track.stop());
          })
          .catch(() => {}); // Silent if no permission
          
      } catch {
        // Silent cleanup
      }
      
      // Call success callback
      onScanSuccess(decodedText);
    } else {
      setError('Invalid QR code');
      onScanError('Invalid QR code');
    }
  };

  const handleScanError = () => {
    // Silent - don't show scan errors
  };

  const handleAllowCamera = async () => {
    setNeedsPermission(false);
    setError('');
    await requestPermissionAndStart();
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-6">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">Initializing scanner...</p>
        </div>
    );
  }

  if (needsPermission) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] p-6 text-center">
        <Shield className="w-12 h-12 text-blue-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold mb-2">Camera Permission Required</h3>
        <p className="text-gray-600 mb-4 text-sm">
          Allow camera access to scan QR codes
        </p>
        <button
          onClick={handleAllowCamera}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Allow Camera
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="w-full">
        <div 
          id={elementId} 
          className="border-2 border-blue-500 rounded-lg overflow-hidden bg-gray-100 min-h-[300px] w-full"
          style={{ minHeight: '300px' }}
        />
      </div>
      
      {success && (
        <div className="w-full bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
          <div className="flex items-center space-x-2 text-green-800">
            <CheckCircle className="w-5 h-5" />
      <div>
              <h3 className="font-semibold">Authentication Successful!</h3>
              <p className="text-sm">Redirecting...</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="w-full bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <h3 className="font-semibold">Error</h3>
              <p className="text-sm">{error}</p>
        </div>
      </div>
      </div>
      )}
    </div>
  );
} 