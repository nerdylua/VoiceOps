'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/auth-context';

export function HeroSection() {
  const { isAuthenticated } = useAuth();

  return (
    <section className={'mx-auto max-w-7xl px-8 relative flex items-center justify-center mt-20 mb-16'}>
      <div className={'text-center w-full max-w-4xl'}>
        <h1 className={'text-[54px] leading-[58px] md:text-[72px] md:leading-[76px] tracking-[-2px] font-bold text-white mb-6'}>
          VoiceOps
          <span className={'block text-[36px] leading-[40px] md:text-[48px] md:leading-[52px] font-light text-white/80 mt-2'}>
            AI Workspace Assistant
          </span>
        </h1>
        <p className={'mt-8 text-[20px] leading-[32px] md:text-[22px] md:leading-[34px] text-white/80 max-w-3xl mx-auto'}>
          Transform your workspace with intelligent automation. Control your environment through voice commands, monitor sensors in real-time, and manage everything from a unified dashboard.
        </p>
        <div className={'mt-12 flex flex-col sm:flex-row justify-center gap-4 max-w-md mx-auto'}>
          <Link href={isAuthenticated ? '/dashboard' : '/auth?redirect=/dashboard'} className={'flex-1'}>
            <button className={'w-full bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-xl font-medium text-lg transition-colors shadow-lg'}>
              Enter Dashboard
            </button>
          </Link>
          <Link href={isAuthenticated ? '/controls' : '/auth?redirect=/controls'} className={'flex-1'}>
            <button className={'w-full border-2 border-white/30 backdrop-blur-sm hover:border-white/50 hover:bg-white/10 text-white px-8 py-4 rounded-xl font-medium text-lg transition-all'}>
              Device Controls
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
}
