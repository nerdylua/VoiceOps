import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check for authentication status
  const authCookie = request.cookies.get('voiceops_auth');
  const userCookie = request.cookies.get('voiceops_user');
  const isAuthenticated = authCookie?.value === 'true';
  const hasUser = userCookie?.value;
  
  // If user is already authenticated and tries to access auth page, redirect to dashboard
  if (pathname === '/auth' && isAuthenticated && hasUser) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  // Public routes that don't require authentication
  const publicRoutes = ['/', '/auth'];
  
  // API routes that don't require auth
  const publicApiRoutes = ['/api/auth'];
  
  // Check if current path is a public route
  if (publicRoutes.includes(pathname)) {
    return NextResponse.next();
  }
  
  // Check if current path is a public API route
  if (publicApiRoutes.some(route => pathname.startsWith(route))) {
    return NextResponse.next();
  }
  
  // All other routes require authentication
  const protectedRoutes = ['/dashboard', '/controls'];
  
  // Check if accessing protected routes
  if (protectedRoutes.some(route => pathname.startsWith(route)) || pathname.startsWith('/api/')) {
    if (!isAuthenticated || !hasUser) {
      // If it's an API call, return 401
      if (pathname.startsWith('/api/')) {
        return NextResponse.json(
          { error: 'Authentication required' },
          { status: 401 }
        );
      }
      
      // For page routes, redirect to auth
      const authUrl = new URL('/auth', request.url);
      authUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(authUrl);
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}; 