import React from 'react';
import {
  LayoutDashboard,
  Box,
  TrendingUp,
  BarChart2,
  Info,
  Clock,
  Compass,
} from 'lucide-react';
import { PageId } from '../types';

interface TopNavbarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  backendHealthy: boolean | null;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({
  activePage,
  onSelectPage,
  backendHealthy,
}) => {
  const navItems: { id: PageId; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: '3d-ocean', label: '3D Ocean Model', icon: Box },
    { id: 'prediction', label: 'Prediction Studio', icon: TrendingUp },
    { id: 'model-eval', label: 'Model Evaluation', icon: BarChart2 },
    { id: 'about', label: 'About Project', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 flex h-14 w-full items-center justify-between border-b border-zinc-800 bg-[#090a0f]/95 px-4 backdrop-blur-md lg:px-6">
      {/* Left: OceanEmbed Brand & Clean Badge */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 border border-zinc-800 text-cyan-400 shadow-sm">
          <Compass className="h-4 w-4" />
        </div>

        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold tracking-tight text-zinc-100 lg:text-base">
              OceanEmbed
            </span>
            <span className="rounded border border-cyan-500/40 bg-cyan-950/40 px-1.5 py-0.2 text-[10px] font-mono text-cyan-300">
              v0.2
            </span>
          </div>
          <span className="text-[10px] text-zinc-400 leading-none">
            SIH26066 • Ocean Temperature Platform
          </span>
        </div>
      </div>

      {/* Center: 5 Clean Navigation Tabs */}
      <nav className="hidden md:flex items-center gap-1.5 lg:gap-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all ${
                isActive
                  ? 'border border-cyan-500/70 bg-zinc-900 text-white shadow-sm'
                  : 'text-zinc-400 hover:bg-zinc-900/60 hover:text-zinc-200'
              }`}
            >
              <Icon
                className={`h-3.5 w-3.5 ${
                  isActive ? 'text-cyan-400' : 'text-zinc-400'
                }`}
              />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right: Backend Port 8001 & UTC Status */}
      <div className="flex items-center gap-3 text-xs">
        {/* Backend Status */}
        <div className="flex items-center gap-1.5 text-zinc-400">
          <span
            className={`h-2 w-2 rounded-full ${
              backendHealthy ? 'bg-emerald-400' : 'bg-rose-400'
            }`}
          />
          <span className="text-[11px] font-mono">
            API <span className={backendHealthy ? 'text-emerald-400' : 'text-rose-400'}>
              {backendHealthy ? 'Online' : 'Offline'}
            </span>
          </span>
        </div>

        {/* UTC Clock pill */}
        <div className="hidden sm:flex items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-900/80 px-2.5 py-1 text-[11px] font-mono text-zinc-400">
          <Clock className="h-3 w-3 text-zinc-400" />
          <span>UTC 00:00</span>
        </div>
      </div>
    </header>
  );
};
export default TopNavbar;
