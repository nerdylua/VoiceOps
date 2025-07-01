import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { qrData } = body;

    // Handle QR code authentication
    if (qrData === 'http://en.m.wikipedia.org') {
      // Send commands to Firebase to open the door and turn on lights
      const firebaseUrl = 'https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app';
      
      try {
        // Execute both commands simultaneously
        const [servoResponse, lightsResponse] = await Promise.all([
          // Open the door by setting servo to "on"
          fetch(`${firebaseUrl}/commands/servo.json`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify('on')
          }),
          // Turn on lights
          fetch(`${firebaseUrl}/commands/lights.json`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify('on')
          })
        ]);

        if (!servoResponse.ok || !lightsResponse.ok) {
          throw new Error('Failed to control devices');
        }

        return NextResponse.json({
          success: true,
          message: 'Authentication successful! Door opened.',
          user: {
            id: 'qr-user',
            name: 'Authorized User',
            type: 'qr-authenticated'
          },
          devices: ['servo', 'lights']
        });
      } catch (firebaseError: unknown) {
        // Auth was successful but device control failed
        console.error('Firebase error:', firebaseError);
        return NextResponse.json({
          success: true,
          message: 'Authentication successful!',
          user: {
            id: 'qr-user',
            name: 'Authorized User',
            type: 'qr-authenticated'
          },
          warning: 'Could not control devices - check device connection'
        });
      }
    }

    return NextResponse.json(
      { error: 'Invalid authentication data' },
      { status: 400 }
    );

  } catch (error) {
    console.error('Auth API error:', error);
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    );
  }
} 