'use client';

import { AuthPage } from '@/components/auth/auth-page';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { useEffect, Suspense } from 'react';

function AuthContent() {
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
      
      // Small delay to ensure cookies are set before navigation
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Force full page reload to ensure server sees new cookies
      window.location.href = redirectTo;
      
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

export default function Auth() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>}>
      <AuthContent />
    </Suspense>
  );
} 