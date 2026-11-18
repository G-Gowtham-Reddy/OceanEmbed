import React from 'react';
import {
  LayoutDashboard,
  Compass,
  Box,
  TrendingUp,
  Cpu,
  CheckCircle2,
  Filter,
  Info,
  Waves,
  X,
} from 'lucide-react';
import { PageId } from '../types';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  isOpen: boolean;
  onCloseMobile: () => void;
}

interface NavItem {
  id: PageId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  isOpen,
  onCloseMobile,
}) => {
  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'explorer', label: 'Data Explorer', icon: Compass },
    { id: '3d-temp', label: '3D Temperature', icon: Box },
    { id: 'prediction', label: 'Prediction', icon: TrendingUp },
    { id: 'model-analysis', label: 'Model Analysis', icon: Cpu },
    { id: 'argo-validation', label: 'ARGO Validation', icon: CheckCircle2 },
    { id: 'preprocessing', label: 'Data Preprocessing', icon: Filter },
    { id: 'about', label: 'About Project', icon: Info },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-800 bg-[#070e1e] text-slate-200 transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header / Brand */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800/80 px-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-700 shadow-lg shadow-cyan-500/20">
              <Waves className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold tracking-tight text-white text-lg">OceanEmbed</span>
                <span className="rounded bg-cyan-950 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-cyan-400 border border-cyan-800/50">
                  v0.2
                </span>
              </div>
              <p className="text-[11px] text-slate-400">SIH26066 • Ocean Research</p>
            </div>
          </div>
          <button
            onClick={onCloseMobile}
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
            aria-label="Close Sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 overflow-y-auto px-3 py-4">
          <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectPage(item.id);
                    onCloseMobile();
                  }}
                  className={`group flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-950/80 to-blue-950/40 text-cyan-400 border-l-4 border-cyan-400 shadow-sm'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`h-4 w-4 transition-colors ${
                        isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-300'
                      }`}
                    />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-medium text-slate-400">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Footer info */}
        <div className="border-t border-slate-800/80 p-4 bg-[#050a16]">
          <div className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3">
            <div className="flex items-center justify-between text-xs font-medium text-slate-300">
              <span>Domain Area</span>
              <span className="text-cyan-400 font-mono">Indian Ocean</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400">
              <span>Depth Target</span>
              <span className="font-mono text-slate-300">0 – 1000 m</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;
