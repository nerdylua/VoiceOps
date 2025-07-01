'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Fan, Lightbulb, Volume2, Mic, Settings, AlertTriangle, ArrowLeft, BarChart3, CheckCircle, XCircle, Loader2, LogOut } from 'lucide-react';
import { HomePageBackground } from '@/components/gradients/home-page-background';
import { useAuth } from '@/contexts/auth-context';
import Link from 'next/link';
import { assistantService, VoiceCommandResponse } from '@/lib/assistant-service';

export function ControlsPage() {
  const { isAuthenticated, logout } = useAuth();
  const [fanStatus, setFanStatus] = useState(false);
  const [lightStatus, setLightStatus] = useState(false);
  const [partyStatus, setPartyStatus] = useState(false);
  const [voiceCommand, setVoiceCommand] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState<VoiceCommandResponse | null>(null);
  const [assistantStatus, setAssistantStatus] = useState<'checking' | 'available' | 'unavailable'>('checking');
  const [listenDuration, setListenDuration] = useState(3);

  const firebaseUrl = 'https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app';

  // Check assistant service status on component mount
  useEffect(() => {
    checkAssistantStatus();
    loadDeviceStates();
  }, []);

  const loadDeviceStates = async () => {
    try {
      // Fetch current device states from Firebase
      const responses = await Promise.all([
        fetch(`${firebaseUrl}/commands/fan.json`),
        fetch(`${firebaseUrl}/commands/lights.json`),
        fetch(`${firebaseUrl}/commands/party.json`)
      ]);

      const [fanData, lightsData, partyData] = await Promise.all(
        responses.map(response => response.json())
      );

      setFanStatus(fanData === 'on');
      setLightStatus(lightsData === 'on');
      setPartyStatus(partyData === 'on');
    } catch (error) {
      console.error('Failed to load device states:', error);
    }
  };

  const updateFirebaseDevice = async (device: string, state: 'on' | 'off') => {
    try {
      const response = await fetch(`${firebaseUrl}/commands/${device}.json`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      });

      if (!response.ok) {
        throw new Error(`Failed to update ${device}`);
      }
      return true;
    } catch (error) {
      console.error(`Failed to control ${device}:`, error);
      return false;
    }
  };

  const checkAssistantStatus = async () => {
    setAssistantStatus('checking');
    try {
      const isAvailable = await assistantService.isServiceAvailable();
      setAssistantStatus(isAvailable ? 'available' : 'unavailable');
    } catch (error) {
      console.error('Failed to check assistant status:', error);
      setAssistantStatus('unavailable');
    }
  };

  const handleFanToggle = async () => {
    const newStatus = !fanStatus;
    setFanStatus(newStatus);
    
    const success = await updateFirebaseDevice('fan', newStatus ? 'on' : 'off');
    if (!success) {
      // Revert on error
      setFanStatus(!newStatus);
    }
  };

  const handleLightToggle = async () => {
    const newStatus = !lightStatus;
    setLightStatus(newStatus);
    
    const success = await updateFirebaseDevice('lights', newStatus ? 'on' : 'off');
    if (!success) {
      // Revert on error
      setLightStatus(!newStatus);
    }
  };

  const handlePartyToggle = async () => {
    const newStatus = !partyStatus;
    setPartyStatus(newStatus);
    
    const success = await updateFirebaseDevice('party', newStatus ? 'on' : 'off');
    if (!success) {
      // Revert on error
      setPartyStatus(!newStatus);
    }
  };

  const handleEmergencyAlert = async () => {
    const success = await updateFirebaseDevice('buzzer', 'on');
    if (success) {
      setLastResponse({
        success: true,
        command: 'Emergency Alert',
        intent: 'emergency',
        response: 'Emergency buzzer triggered for 10 seconds!',
        actions: [{ device: 'buzzer', command: 'on' }]
      });

      // Automatically turn off buzzer after 10 seconds
      setTimeout(async () => {
        await updateFirebaseDevice('buzzer', 'off');
      }, 10000);
    } else {
      setLastResponse({
        success: false,
        error: 'Failed to trigger emergency alert'
      });
    }
  };

  const handleVoiceCommand = async () => {
    if (!voiceCommand.trim()) return;
    
    setIsProcessing(true);
    try {
      const response = await assistantService.processTextCommand(voiceCommand, false);
      setLastResponse(response);
      
      if (response.success) {
        // Update UI based on response actions
        response.actions?.forEach(action => {
          if (action.device === 'fan') {
            setFanStatus(action.command === 'on');
          } else if (action.device === 'lights' || action.device === 'light') {
            setLightStatus(action.command === 'on');
          } else if (action.device === 'party') {
            setPartyStatus(action.command === 'on');
          }
        });
      }
      
      setVoiceCommand('');
    } catch (error) {
      console.error('Voice command failed:', error);
      setLastResponse({
        success: false,
        error: 'Failed to process command'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const startVoiceListening = async () => {
    if (assistantStatus !== 'available') {
      alert('Assistant service is not available. Please ensure the backend is running.');
      return;
    }

    setIsListening(true);
    setLastResponse(null);
    
    try {
      const response = await assistantService.listenForVoiceCommand(listenDuration, true);
      setLastResponse(response);
      
      if (response.success && response.command) {
        setVoiceCommand(response.command);
        
        // Update UI based on response actions
        response.actions?.forEach(action => {
          if (action.device === 'fan') {
            setFanStatus(action.command === 'on');
          } else if (action.device === 'lights' || action.device === 'light') {
            setLightStatus(action.command === 'on');
          } else if (action.device === 'party') {
            setPartyStatus(action.command === 'on');
          }
        });
      }
    } catch (error) {
      console.error('Voice listening failed:', error);
      setLastResponse({
        success: false,
        error: 'Voice listening failed'
      });
    } finally {
      setIsListening(false);
    }
  };

  const getStatusIcon = () => {
    switch (assistantStatus) {
      case 'checking':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-400" />;
      case 'available':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'unavailable':
        return <XCircle className="h-4 w-4 text-red-400" />;
    }
  };

  const getStatusText = () => {
    switch (assistantStatus) {
      case 'checking':
        return 'Checking assistant...';
      case 'available':
        return 'Assistant ready';
      case 'unavailable':
        return 'Assistant offline';
    }
  };

  return (
    <div className="min-h-screen relative">
      <HomePageBackground />
      
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-md border-b border-white/20 px-6 py-6 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">VoiceOps Controls</h1>
              <p className="text-white/80 mt-2">Manually control your workspace devices and test commands</p>
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
                  <Link href="/dashboard" className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Dashboard
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Device Controls */}
            <div className="space-y-6">
              <Card className="bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3 text-white">
                    <div className="p-2 bg-white/10 rounded-lg">
                      <Settings className="h-5 w-5 text-white/80" />
                    </div>
                    Device Controls
                  </CardTitle>
                  <CardDescription className="text-white/70">
                    Manually control your IoT devices
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Fan Control */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-500/20 rounded-lg">
                        <Fan className="h-5 w-5 text-green-300" />
                      </div>
                      <div>
                        <Label htmlFor="fan-switch" className="text-white font-medium">Workspace Fan</Label>
                        <p className="text-xs text-white/60">5V Mini Fan via Stepper Motor</p>
                      </div>
                    </div>
                    <Switch
                      id="fan-switch"
                      checked={fanStatus}
                      onCheckedChange={handleFanToggle}
                    />
                  </div>

                  {/* Light Control */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-yellow-500/20 rounded-lg">
                        <Lightbulb className="h-5 w-5 text-yellow-300" />
                      </div>
                      <div>
                        <Label htmlFor="light-switch" className="text-white font-medium">Workspace Lights</Label>
                        <p className="text-xs text-white/60">LED Status Indicator</p>
                      </div>
                    </div>
                    <Switch
                      id="light-switch"
                      checked={lightStatus}
                      onCheckedChange={handleLightToggle}
                    />
                  </div>

                  {/* Party light */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-purple-500/20 rounded-lg">
                        <Lightbulb className="h-5 w-5 text-purple-300" />
                      </div>
                      <div>
                        <Label htmlFor="party-switch" className="text-white font-medium">Party Light</Label>
                        <p className="text-xs text-white/60">Party mode Indicator</p>
                      </div>
                    </div>
                    <Switch
                      id="party-switch"
                      checked={partyStatus}
                      onCheckedChange={handlePartyToggle}
                    />
                  </div>

                  {/* Emergency Actions */}
                  <div className="pt-4 border-t border-white/10">
                    <h4 className="font-medium mb-4 text-white flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-orange-400" />
                      Emergency Actions
                    </h4>
                    <div className="space-y-3">
                      <Button 
                        onClick={handleEmergencyAlert}
                        variant="destructive" 
                        className="w-full justify-start bg-red-500/20 border-red-500/30 hover:bg-red-500/30 text-red-300"
                      >
                        🚨 Trigger Emergency Alert
                      </Button>
                      <Button 
                        onClick={logout}
                        variant="outline" 
                        className="w-full justify-start border-red-500/20 hover:bg-red-500/10 text-red-300 hover:text-red-200"
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Lock Workspace
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Communication Controls */}
            <div className="space-y-6">
              {/* Voice Commands */}
              <Card className="bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between text-white">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-purple-500/20 rounded-lg">
                        <Volume2 className="h-5 w-5 text-purple-300" />
                      </div>
                      Voice Commands
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      {getStatusIcon()}
                      <span className="text-white/70">{getStatusText()}</span>
                    </div>
                  </CardTitle>
                  <CardDescription className="text-white/70">
                    Control devices with voice commands or text input
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Listen Duration Control */}
                  <div className="flex items-center gap-4">
                    <Label htmlFor="duration" className="text-white text-sm">
                      Listen Duration:
                    </Label>
                    <select
                      id="duration"
                      value={listenDuration}
                      onChange={(e) => setListenDuration(Number(e.target.value))}
                      className="bg-white border border-white/20 rounded px-2 py-1 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value={2} className="text-gray-900 bg-white">2 sec (Quick)</option>
                      <option value={3} className="text-gray-900 bg-white">3 sec (Normal)</option>
                      <option value={4} className="text-gray-900 bg-white">4 sec (Medium)</option>
                      <option value={6} className="text-gray-900 bg-white">6 sec (Long)</option>
                    </select>
                  </div>

                  <div className="space-y-5">
                    <Label htmlFor="voice-input" className="text-white">Voice Command</Label>
                    <Textarea
                      id="voice-input"
                      placeholder="Type a command to test or use the Listen button to record..."
                      value={voiceCommand}
                      onChange={(e) => setVoiceCommand(e.target.value)}
                      rows={3}
                      className="resize-none bg-white/5 border-white/20 text-white placeholder:text-white/50"
                    />
                  </div>
                  
                  <div className="flex gap-3">
                    <Button 
                      onClick={handleVoiceCommand} 
                      disabled={!voiceCommand.trim() || isProcessing || isListening}
                      className="flex-1 bg-white text-gray-900 hover:bg-white/90 disabled:opacity-50"
                    >
                      {isProcessing ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Processing...
                        </div>
                      ) : (
                        'Send Command'
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={startVoiceListening}
                      disabled={isListening || isProcessing || assistantStatus !== 'available'}
                      className="flex items-center gap-2 border-white/20 hover:bg-white/10 text-white disabled:opacity-50"
                    >
                      {isListening ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Listening...
                        </>
                      ) : (
                        <>
                          <Mic className="h-4 w-4" />
                          Listen
                        </>
                      )}
                    </Button>
                  </div>

                  {/* Response Display */}
                  {lastResponse && (
                    <div className={`p-3 rounded-lg border ${
                      lastResponse.success 
                        ? 'bg-green-500/10 border-green-500/30' 
                        : 'bg-red-500/10 border-red-500/30'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        {lastResponse.success ? (
                          <CheckCircle className="h-4 w-4 text-green-400" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-400" />
                        )}
                        <span className="text-sm font-medium text-white">
                          {lastResponse.success ? 'Success' : 'Error'}
                        </span>
                        {lastResponse.intent && (
                          <span className="text-xs bg-white/10 px-2 py-1 rounded text-white/70">
                            {assistantService.getIntentDisplayName(lastResponse.intent)}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-white/80">
                        {assistantService.formatResponse(lastResponse)}
                      </p>
                      {lastResponse.actions && lastResponse.actions.length > 0 && (
                        <div className="mt-2 text-xs text-white/60">
                          Actions: {lastResponse.actions.map(a => `${a.device} ${a.command}`).join(', ')}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Help Text */}
                  <div className="text-xs text-white/50 space-y-1">
                    <p>💡 Try commands like:</p>
                    <ul className="list-disc list-inside ml-2 space-y-1">
                      <li>&quot;Turn on the fan&quot; or &quot;Fan on&quot;</li>
                      <li>&quot;Turn off the lights&quot; or &quot;Lights off&quot;</li>
                      <li>&quot;Turn on Party Mode&quot; or &quot;Party on&quot;</li>
                      <li>&quot;Emergency alert&quot; or &quot;Trigger buzzer&quot;</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* System Information */}
          <Card className="mt-8 bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg">
            <CardHeader>
              <CardTitle className="text-white">System Information</CardTitle>
              <CardDescription className="text-white/70">Current system status and configuration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-500/20 rounded-xl border border-green-500/30">
                  <h4 className="font-medium text-green-300">ESP32 Status</h4>
                  <p className="text-sm text-green-200 mt-1">Connected</p>
                </div>
                <div className="p-4 bg-blue-500/20 rounded-xl border border-blue-500/30">
                  <h4 className="font-medium text-blue-300">Firebase Status</h4>
                  <p className="text-sm text-blue-200 mt-1">Connected</p>
                </div>
                <div className="p-4 bg-purple-500/20 rounded-xl border border-purple-500/30">
                  <h4 className="font-medium text-purple-300">ID Authentication</h4>
                  <p className="text-sm text-purple-200 mt-1">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 