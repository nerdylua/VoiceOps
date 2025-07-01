import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-white/10 backdrop-blur-md border-t border-white/20 relative z-10">
      <div className="mx-auto max-w-7xl px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-xl font-bold text-white mb-4">VoiceOps</h3>
            <p className="text-white/70 text-sm leading-relaxed mb-4 max-w-md">
              AI-powered workspace assistant that brings intelligent automation to your environment. 
              Control devices, monitor sensors, and manage your workspace through voice and web. 
            </p>
            <div className="flex space-x-4">
              <span className="text-xs text-white/50">Built with Next.js • TypeScript • Tailwind CSS</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/" className="text-white/70 hover:text-white text-sm transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-white/70 hover:text-white text-sm transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/controls" className="text-white/70 hover:text-white text-sm transition-colors">
                  Controls
                </Link>
              </li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="font-semibold text-white mb-4">Features</h4>
            <ul className="space-y-2 text-sm text-white/70">
              <li>Voice Commands</li>
              <li>IoT Monitoring</li>
              <li>Real-time Sync</li>
              <li>Device Control</li>
              <li>Smart Automation</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/20 flex flex-col md:flex-row justify-between items-center">
          <p className="text-white/60 text-sm">
            © 2025 VoiceOps. IoT Workspace Assistant.
          </p>
          <div className="mt-4 md:mt-0 flex space-x-6">
            <span className="text-xs text-white/50">ESP32 • Firebase • Flask • AI Integration</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
