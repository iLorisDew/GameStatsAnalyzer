import { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';

export function Splashscreen() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const duration = 3000;
    const intervalTime = 30;
    const increment = (100 / duration) * intervalTime;

    const interval = setInterval(() => {
      setProgress(prev => {
        const next = prev + increment;
        return next >= 100 ? 100 : next;
      });
    }, intervalTime);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-zinc-900 via-zinc-950 to-black">
      <div className="text-center space-y-8">
        {/* Logo/Icon */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-emerald-500/20 blur-3xl rounded-full" />
            <BarChart3 className="w-24 h-24 text-emerald-400 relative animate-pulse" />
          </div>
        </div>

        {/* App Name */}
        <div className="space-y-2">
          <h1 className="text-4xl text-white tracking-tight">
            Excel Analytics Pro
          </h1>
          <p className="text-zinc-400">
            Analysez vos données avec précision
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-80 space-y-2">
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-zinc-500 text-center">
            Chargement... {Math.round(progress)}%
          </p>
        </div>
      </div>
    </div>
  );
}
