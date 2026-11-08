import React, { useState } from 'react';
import { TopBar } from './components/TopBar';
import { MediaBin } from './components/MediaBin';
import { VideoMonitor } from './components/VideoMonitor';
import { AnalysisReview } from './components/AnalysisReview';
import { Timeline } from './components/Timeline';
import { AgentActivityPanel } from './components/AgentActivityPanel';
import { ReplayStudio } from './components/ReplayStudio';
import { ExportModal } from './components/ExportModal';
import { MonitorPlay, FileText } from 'lucide-react';

export const App: React.FC = () => {
  const [activeCenterView, setActiveCenterView] = useState<'monitor' | 'analysis'>('monitor');
  const [isExportOpen, setIsExportOpen] = useState(false);

  return (
    <div className="w-screen h-screen flex flex-col bg-studio-950 text-slate-100 overflow-hidden font-sans">
      {/* 1. Global Navigation TopBar */}
      <TopBar onOpenExport={() => setIsExportOpen(true)} />

      {/* 2. Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Media Bin */}
        <MediaBin />

        {/* Center: Stage & Multitrack Timeline */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Center Stage Top Bar: Switch between Video Monitor & Intelligence Review */}
          <div className="h-8 bg-studio-900 border-b border-studio-700/60 px-3 flex items-center gap-2">
            <button
              onClick={() => setActiveCenterView('monitor')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition ${
                activeCenterView === 'monitor'
                  ? 'bg-studio-800 text-cyan border border-cyan/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MonitorPlay className="w-3.5 h-3.5" />
              <span>Video Monitor (9:16 Canvas)</span>
            </button>

            <button
              onClick={() => setActiveCenterView('analysis')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition ${
                activeCenterView === 'analysis'
                  ? 'bg-studio-800 text-cyan border border-cyan/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Intelligence & Transcript Review</span>
            </button>
          </div>

          {/* Center Stage Body */}
          <div className="flex-1 flex overflow-hidden">
            {activeCenterView === 'monitor' ? <VideoMonitor /> : <AnalysisReview />}
          </div>

          {/* Bottom Stage: Multitrack Timeline Canvas */}
          <Timeline />
        </div>

        {/* Right: Agent Activity & Telemetry Feed */}
        <AgentActivityPanel />
      </div>

      {/* 3. Cinematic 60 FPS Multi-Cursor Replay Studio (Milestone 7) */}
      <ReplayStudio />

      {/* 4. Production Render Export Modal */}
      <ExportModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />
    </div>
  );
};

export default App;

