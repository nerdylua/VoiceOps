import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { qrData, userName } = body;

    if (!qrData || !userName) {
      return NextResponse.json(
        { error: 'QR data and username are required' },
        { status: 400 }
      );
    }

    // Forward to Flask backend
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:5000';
    const response = await fetch(`${backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ qrData }),
    });

    const result = await response.json();

    if (response.ok) {
      return NextResponse.json(result);
    } else {
      return NextResponse.json(
        { error: result.error || 'Authentication failed' },
        { status: response.status }
      );
    }
  } catch (error) {
    console.error('QR authentication error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}