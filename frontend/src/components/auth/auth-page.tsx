'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { QrCode, Lock } from 'lucide-react';
import { HomePageBackground } from '@/components/gradients/home-page-background';
import { QRScanner } from './qr-scanner';
import { SuccessModal } from './success-modal';

interface AuthPageProps {
  onAuthSuccess: (qrData: string, userName: string) => void;
}

export function AuthPage({ onAuthSuccess }: AuthPageProps) {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [error, setError] = useState('');
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [authenticatedUser, setAuthenticatedUser] = useState('');
  const [qrDataStored, setQrDataStored] = useState('');

  const handleQRScanSuccess = async (qrData: string) => {
    setIsAuthenticating(true);
    setError('');

    try {
      // Check if the QR data is the expected string
      if (qrData === 'http://en.m.wikipedia.org') {
        // Authentication successful
        setAuthenticatedUser('Mr. Raghavendra');
        setShowSuccessModal(true);
        setQrDataStored(qrData);
        setIsAuthenticating(false);
      } else {
        throw new Error('Invalid QR code');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      setError('Invalid QR code. Please scan the correct QR code.');
      setIsAuthenticating(false);
    }
  };

  const handleQRScanError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleSuccessModalClose = () => {
    setShowSuccessModal(false);
    onAuthSuccess(qrDataStored, authenticatedUser);
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-8">
      <HomePageBackground />
      
      <Card className="w-full max-w-md bg-white/10 backdrop-blur-md border border-white/20 shadow-xl relative z-10">
        <CardHeader className="text-center pb-8">
          <div className="mx-auto w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-6">
            <QrCode className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-white">Secure QR Access</CardTitle>
          <CardDescription className="text-white/70 mt-2">
            Scan your authentication QR code to access VoiceOps
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl backdrop-blur-sm">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {isAuthenticating ? (
            <div className="text-center space-y-6">
              <div className="mx-auto w-20 h-20 bg-green-500/20 rounded-2xl flex items-center justify-center">
                <Lock className="h-10 w-10 text-green-300" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Authenticating...</h3>
                <p className="text-sm text-white/70">
                  Verifying your credentials and setting up access.
                </p>
              </div>
            </div>
          ) : (
            <QRScanner 
              onScanSuccess={handleQRScanSuccess}
              onScanError={handleQRScanError}
            />
          )}
        </CardContent>
      </Card>
      
      {/* Success Modal */}
      <SuccessModal 
        isOpen={showSuccessModal}
        userName={authenticatedUser}
        onClose={handleSuccessModalClose}
      />
    </div>
  );
} 