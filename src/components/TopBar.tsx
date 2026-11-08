import React from 'react';
import { Play, Film, Sparkles, Download, Layers, ShieldCheck, Zap } from 'lucide-react';
import { useProjectStore } from '../stores/projectStore';
import { useAgentStore } from '../stores/agentStore';
import { useReplayStore } from '../stores/replayStore';

interface TopBarProps {
  onOpenExport: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenExport }) => {
  const { name, width, height, fps } = useProjectStore();
  const { agents } = useAgentStore();
  const { setIsReplayOpen } = useReplayStore();

  const isVertical = height > width;

  return (
    <header className="h-14 bg-studio-900 border-b border-studio-700/60 px-4 flex items-center justify-between z-30 select-none">
      {/* Brand & Project Info */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 bg-gradient-to-r from-cyan-500/20 to-violet-500/20 rounded-md border border-cyan-500/30">
          <Film className="w-4 h-4 text-cyan" />
          <span className="font-bold tracking-tight text-white text-sm">AGENTCUT</span>
          <span className="text-[10px] font-mono px-1 py-0.5 rounded bg-cyan/20 text-cyan font-semibold">AI-STUDIO</span>
        </div>

        <div className="h-4 w-[1px] bg-studio-700 mx-1" />

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-200">{name}</span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-studio-800 text-slate-400 border border-studio-700">
            {width}x{height} {isVertical ? '(9:16)' : '(16:9)'} • {fps}fps
          </span>
        </div>
      </div>

      {/* Center: Swarm Status & MCP Pill */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-studio-850 border border-studio-700/80">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-slate-300">MCP Gateway :8000</span>
          <span className="text-[10px] text-slate-500">•</span>
          <span className="text-xs text-slate-400">stdio / sse</span>
        </div>

        <div className="flex items-center -space-x-1.5 overflow-hidden px-2 py-1 bg-studio-850 rounded-full border border-studio-700">
          {agents.map((agt) => (
            <div
              key={agt.agent_id}
              title={`${agt.name} (${agt.role}): ${agt.current_task}`}
              className="w-5 h-5 rounded-full border border-studio-900 flex items-center justify-center text-[9px] font-bold text-black"
              style={{ backgroundColor: agt.color }}
            >
              {agt.name[0]}
            </div>
          ))}
          <span className="pl-3 pr-1 text-xs text-slate-400 font-mono">7 Agents</span>
        </div>
      </div>

      {/* Right Controls: Replay & Export */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setIsReplayOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/40 text-amber-300 hover:text-white hover:bg-amber-500/30 transition-all text-xs font-medium shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Cinematic Replay</span>
        </button>

        <button
          onClick={onOpenExport}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan hover:bg-cyan-400 text-studio-950 font-semibold transition-all text-xs shadow-sm hover:shadow-cyan/20 hover:shadow-lg"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Render</span>
        </button>
      </div>
    </header>
  );
};

