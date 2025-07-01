'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Thermometer, Droplets, Fan, Lightbulb, Shield, Activity, ArrowLeft, Settings } from 'lucide-react';
import { HomePageBackground } from '@/components/gradients/home-page-background';
import { useAuth } from '@/contexts/auth-context';
import Link from 'next/link';

export function DashboardPage() {
  const { isAuthenticated } = useAuth();
  
  // Mock data - will be replaced with Firebase data
  const sensorData = {
    temperature: (Math.random() * (27 - 25) + 24).toFixed(1), // Random between 24-26°C
    humidity: 55,
    gasLevel: 0.2,
    fanStatus: false,
    lightStatus: true,
    systemStatus: 'Active'
  };

  return (
    <div className="min-h-screen relative">
      <HomePageBackground />
      
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-md border-b border-white/20 px-6 py-6 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">VoiceOps Dashboard</h1>
              <p className="text-white/80 mt-2">Monitor your workspace environment and IoT devices in real-time</p>
            </div>
            <div className="flex items-center gap-3">
              <Button asChild variant="outline" className="border-white/20 hover:bg-white/10 text-white">
                <Link href="/" className="flex items-center gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Home
                </Link>
              </Button>
              {isAuthenticated && (
                <Button asChild variant="outline" className="border-white/20 hover:bg-white/10 text-white">
                  <Link href="/controls" className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    Controls
                  </Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Temperature Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">Temperature</CardTitle>
                <div className="p-2 bg-orange-500/20 rounded-lg">
                  <Thermometer className="h-4 w-4 text-orange-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.temperature}°C</div>
                <p className="text-xs text-white/60 mt-1">DHT22 Sensor</p>
              </CardContent>
            </Card>

            {/* Humidity Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">Humidity</CardTitle>
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Droplets className="h-4 w-4 text-blue-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.humidity}%</div>
                <p className="text-xs text-white/60 mt-1">DHT22 Sensor</p>
              </CardContent>
            </Card>

            {/* Gas Level Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">Gas Level</CardTitle>
                <div className="p-2 bg-red-500/20 rounded-lg">
                  <Shield className="h-4 w-4 text-red-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.gasLevel}</div>
                <p className="text-xs text-white/60 mt-1">MQ-2 Sensor</p>
              </CardContent>
            </Card>

            {/* Fan Status Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">Fan</CardTitle>
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Fan className="h-4 w-4 text-green-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.fanStatus ? 'ON' : 'OFF'}</div>
                <p className="text-xs text-white/60 mt-1">Relay Controlled</p>
              </CardContent>
            </Card>

            {/* Light Status Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">Lighting</CardTitle>
                <div className="p-2 bg-yellow-500/20 rounded-lg">
                  <Lightbulb className="h-4 w-4 text-yellow-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.lightStatus ? 'ON' : 'OFF'}</div>
                <p className="text-xs text-white/60 mt-1">LED Status</p>
              </CardContent>
            </Card>

            {/* System Status Card */}
            <Card className="bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-white/80">System Status</CardTitle>
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Activity className="h-4 w-4 text-green-300" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{sensorData.systemStatus}</div>
                <p className="text-xs text-white/60 mt-1">ESP32 Connection</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg">
            <CardHeader>
              <CardTitle className="text-white">Recent Activity</CardTitle>
              <CardDescription className="text-white/70">Latest voice commands and system events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-white/10 last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-sm text-white">Voice Command: &quot;Turn on the fan&quot;</span>
                  </div>
                  <span className="text-xs text-white/60">2 minutes ago</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-white/10 last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                    <span className="text-sm text-white">Temperature Alert: Above 26°C</span>
                  </div>
                  <span className="text-xs text-white/60">5 minutes ago</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-white/10 last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span className="text-sm text-white">ID Authentication: Access granted</span>
                  </div>
                  <span className="text-xs text-white/60">10 minutes ago</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 