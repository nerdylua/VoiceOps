'use client';

import { AuthPage } from '@/components/auth/auth-page';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { assistantService } from '@/lib/assistant-service';

export default function Auth() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/dashboard';
  const { login } = useAuth();

  const handleAuthSuccess = async (qrData: string, userName: string) => {
    try {
      // For now, skip backend authentication and go directly to dashboard
      // TODO: Re-enable backend auth when backend is ready
      
      // Simulate successful auth
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

  return <AuthPage onAuthSuccess={handleAuthSuccess} />;
} 