'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function Header() {
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      setTime(new Date().toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-white text-[#192355] relative z-50 w-full">
      <div className="px-8 py-5 flex items-center justify-between">
        {/* Logo / Brand */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-[#192355] font-sans lowercase">
            sedno
          </h1>
        </div>

        {/* Time */}
        <div className="text-sm font-medium font-mono text-gray-600 opacity-80">
          {time}
        </div>
      </div>
    </header>
  );
}
