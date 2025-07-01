'use client';

import React from 'react';
import '../../styles/home-page.css';
import Header from '@/components/home/header/header';
import { HeroSection } from '@/components/home/hero-section/hero-section';
import { FeaturesSection } from '@/components/home/features/features-section';
import { HomePageBackground } from '@/components/gradients/home-page-background';
import { Footer } from '@/components/home/footer/footer';

export function HomePage() {
  return (
    <>
      <div className="relative">
        <HomePageBackground />
        <Header />
        <HeroSection />
        <FeaturesSection />
        <Footer />
      </div>
    </>
  );
}
