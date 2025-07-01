'use client';

import React from 'react';
import { CheckCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SuccessModalProps {
  isOpen: boolean;
  userName: string;
  onClose: () => void;
}

export function SuccessModal({ isOpen, userName, onClose }: SuccessModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      {/* Modal */}
      <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 max-w-sm mx-4 shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Success content */}
        <div className="text-center space-y-6">
          <div className="mx-auto w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center">
            <CheckCircle className="h-10 w-10 text-green-400" />
          </div>
          
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Authentication Successful!
            </h2>
            <p className="text-white/70 text-lg">
              Welcome back, <span className="text-white font-semibold">{userName}</span>! 🎉
            </p>
          </div>

          <div className="space-y-3">
            <Button
              onClick={onClose}
              className="w-full bg-white text-gray-900 hover:bg-white/90 font-medium"
            >
              Continue to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 