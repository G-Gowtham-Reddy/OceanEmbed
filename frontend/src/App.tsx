import React, { useState, useEffect } from 'react';
import { PageId } from './types';
import { TopNavbar } from './components/TopNavbar';
import { DashboardPage } from './pages/DashboardPage';
import { ThreeDOceanPage } from './pages/ThreeDOceanPage';
import { PredictionPage } from './pages/PredictionPage';
import { ModelAnalysisPage } from './pages/ModelAnalysisPage';
import { AboutProjectPage } from './pages/AboutProjectPage';
import { API_BASE_URL } from './config/api';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);

  // Poll backend health check
  useEffect(() => {
    const checkHealth = () => {
      fetch(`${API_BASE_URL}/api/health`)
        .then((res) => {
          if (!res.ok) throw new Error('Unhealthy');
          return res.json();
        })
        .then(() => setBackendHealthy(true))
        .catch(() => setBackendHealthy(false));
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage />;
      case '3d-ocean':
        return <ThreeDOceanPage />;
      case 'prediction':
        return <PredictionPage />;
      case 'model-eval':
        return <ModelAnalysisPage />;
      case 'about':
        return <AboutProjectPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#08090d] text-zinc-100 font-sans antialiased selection:bg-cyan-500/20 selection:text-cyan-200">
      {/* Modern Top Horizontal Navbar in Charcoal & Soft Silver */}
      <TopNavbar
        activePage={activePage}
        onSelectPage={setActivePage}
        backendHealthy={backendHealthy}
      />

      {/* Main Container: Full width fluid layout with clean edge padding */}
      <main className="flex-1 w-full px-4 py-4 sm:px-6 lg:px-8">
        <div className="w-full">{renderActivePage()}</div>
      </main>
    </div>
  );
};

export default App;
