import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action } = body;

    if (action === 'welcome_raghavendra') {
      // Send commands to Firebase to turn on devices
      const firebaseUrl = 'https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app';
      
      // Turn on light
      await fetch(`${firebaseUrl}/commands/light.json`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify('on')
      });

      // Turn on fan
      await fetch(`${firebaseUrl}/commands/fan.json`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify('on')
      });

      // Log the access
      await fetch(`${firebaseUrl}/logs.json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user: 'Mr. Raghavendra',
          action: 'office_access',
          timestamp: new Date().toISOString(),
          devices: ['light', 'fan'],
          status: 'activated'
        })
      });

      return NextResponse.json({
        success: true,
        message: 'Welcome Mr. Raghavendra! Office systems activated.',
        devices: ['light', 'fan']
      });
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    );

  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to activate office systems' },
      { status: 500 }
    );
  }
} 