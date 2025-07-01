'use client';

import { AuthPage } from '@/components/auth/auth-page';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { useEffect } from 'react';

export default function Auth() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/dashboard';
  const { login, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleAuthSuccess = async (qrData: string, userName: string) => {
    try {
      const mockUser = {
        id: '1',
        name: userName,
        type: 'user'
      };
      
      const mockToken = 'mock-jwt-token';
      
      // Use auth context to login
      login(mockUser, mockToken);
      
      // Redirect to dashboard immediately
      router.push(redirectTo);
      
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Authentication failed. Please try again.');
    }
  };

  // Don't render auth page if already authenticated
  if (isAuthenticated) {
    return null;
  }

  return <AuthPage onAuthSuccess={handleAuthSuccess} />;
} 