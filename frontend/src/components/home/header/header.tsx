'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/auth-context';
import { LogOut, Lock } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleProtectedNavigation = (path: string) => {
    if (!isAuthenticated) {
      router.push(`/auth?redirect=${path}`);
    } else {
      router.push(path);
    }
  };

  return (
    <nav className="relative z-50">
      <div className="mx-auto max-w-7xl px-8 py-6 flex items-center justify-between">
        <div className="flex items-center">
          <Link className="flex items-center" href={'/'}>
            <span className="text-2xl font-bold text-white">VoiceOps</span>
          </Link>
        </div>
        
        <div className="hidden md:flex items-center space-x-8 absolute left-1/2 transform -translate-x-1/2">
          <Link href={'/'} className="text-white/80 hover:text-white font-medium transition-colors">
            Home
          </Link>
          
          {/* Protected Dashboard Link */}
          {isAuthenticated ? (
            <Link href={'/dashboard'} className="text-white/80 hover:text-white font-medium transition-colors">
              Dashboard
            </Link>
          ) : (
            <button 
              onClick={() => handleProtectedNavigation('/dashboard')}
              className="text-white/60 hover:text-white/80 font-medium transition-colors flex items-center space-x-1"
            >
              <Lock className="h-3 w-3" />
              <span>Dashboard</span>
            </button>
          )}
          
          {/* Protected Controls Link */}
          {isAuthenticated ? (
            <Link href={'/controls'} className="text-white/80 hover:text-white font-medium transition-colors">
              Controls
            </Link>
          ) : (
            <button 
              onClick={() => handleProtectedNavigation('/controls')}
              className="text-white/60 hover:text-white/80 font-medium transition-colors flex items-center space-x-1"
            >
              <Lock className="h-3 w-3" />
              <span>Controls</span>
            </button>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          {isAuthenticated && user ? (
            <>
              <span className="text-white/90 font-medium">
                {user.name === 'Mr. Raghavendra' ? 'Welcome Mr. Raghavendra' : `Hello, ${user.name}`}
              </span>
              <Button 
                onClick={logout}
                className="bg-red-500/20 backdrop-blur-sm border border-red-500/30 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg font-medium flex items-center space-x-2"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </>
          ) : (
            <Button asChild={true} className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 text-white px-6 py-2 rounded-lg font-medium">
              <Link href={'/auth'}>Access Workspace</Link>
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}
