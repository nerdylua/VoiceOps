import { Mic, Smartphone, Thermometer, Shield, Zap, Database } from 'lucide-react';

export function FeaturesSection() {
  const features = [
    {
      icon: Mic,
      title: 'Voice Commands',
      description: 'Control your workspace using natural voice commands powered by AI. Just speak and your environment responds.',
      color: 'bg-purple-500/20 text-purple-300'
    },
    {
      icon: Smartphone,
      title: 'Web Dashboard',
      description: 'Real-time monitoring and control through an intuitive web interface. Monitor sensors and device status.',
      color: 'bg-green-500/20 text-green-300'
    },
    {
      icon: Thermometer,
      title: 'Environmental Monitoring',
      description: 'Track temperature, humidity, and air quality using DHT22 and MQ-2 sensors for optimal workspace conditions.',
      color: 'bg-orange-500/20 text-orange-300'
    },
    {
      icon: Shield,
      title: 'Smart Security',
      description: 'Automated alerts and access control. Get instant notifications for security events and environmental hazards.',
      color: 'bg-red-500/20 text-red-300'
    },
    {
      icon: Zap,
      title: 'IoT Automation',
      description: 'Automated responses based on environmental conditions. Smart fan control, lighting, and emergency protocols.',
      color: 'bg-yellow-500/20 text-yellow-300'
    },
    {
      icon: Database,
      title: 'Real-time Data Sync',
      description: 'Firebase-powered real-time data synchronization. Instant updates across all devices and seamless ESP32 integration.',
      color: 'bg-blue-500/20 text-blue-300'
    }
  ];

  return (
    <section className={'mx-auto max-w-7xl px-8 py-20 relative'}>
      <div className={'text-center mb-16'}>
        <h2 className={'text-[36px] leading-[40px] md:text-[48px] md:leading-[52px] tracking-[-1.5px] font-bold text-white mb-4'}>
          Intelligent Workspace Features
        </h2>
        <p className={'text-[18px] leading-[28px] md:text-[20px] md:leading-[30px] text-white/80 max-w-2xl mx-auto'}>
          Experience the future of workspace automation with AI-driven controls and comprehensive monitoring
        </p>
      </div>
      
      <div className={'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'}>
        {features.map((feature, index) => (
          <div key={index} className={'group p-8 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:border-white/20 hover:bg-white/10 transition-all duration-300'}>
            <div className={`inline-flex p-4 rounded-xl ${feature.color} mb-6 group-hover:scale-110 transition-transform`}>
              <feature.icon className={'h-6 w-6'} />
            </div>
            <h3 className={'text-xl font-semibold mb-3 text-white'}>{feature.title}</h3>
            <p className={'text-white/70 text-[15px] leading-[24px]'}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
} 