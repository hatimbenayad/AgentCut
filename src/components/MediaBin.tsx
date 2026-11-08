import React from 'react';
import { FolderPlus, Video, Music, Image as ImageIcon, CheckCircle2, Clock, Sparkles } from 'lucide-react';
import { useProjectStore } from '../stores/projectStore';

export const MediaBin: React.FC = () => {
  const { media_bin } = useProjectStore();

  return (
    <div className="w-64 bg-studio-900 border-r border-studio-700/60 flex flex-col h-full select-none">
      <div className="p-3 border-b border-studio-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
          <FolderPlus className="w-3.5 h-3.5 text-cyan" />
          <span>Project Bin</span>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-studio-800 px-1.5 py-0.5 rounded border border-studio-700">
          {media_bin.length} Assets
        </span>
      </div>

      {/* Asset List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {media_bin.map((asset) => (
          <div
            key={asset.asset_id}
            className="group p-2.5 rounded-lg bg-studio-850 hover:bg-studio-800 border border-studio-700/50 hover:border-cyan/40 transition-all cursor-grab active:cursor-grabbing"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-studio-800 border border-studio-700 flex items-center justify-center text-slate-400 group-hover:text-cyan group-hover:border-cyan/30">
                  <Video className="w-4 h-4" />
                </div>
                <div className="overflow-hidden">
                  <h4 className="text-xs font-medium text-slate-200 truncate w-32" title={asset.name}>
                    {asset.name}
                  </h4>
                  <p className="text-[10px] font-mono text-slate-400">
                    {asset.resolution} • {asset.fps}fps
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-mono text-slate-400 bg-studio-800 px-1 py-0.5 rounded">
                {asset.duration.toFixed(1)}s
              </span>
            </div>

            <div className="mt-2 pt-2 border-t border-studio-700/40 flex items-center justify-between text-[10px] text-slate-400">
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3 h-3" />
                <span>Analyzed</span>
              </span>
              <span className="font-mono text-slate-400">VAD + Whisper</span>
            </div>
          </div>
        ))}
      </div>

      {/* Intelligence Cache Status */}
      <div className="p-3 bg-studio-950/80 border-t border-studio-700/60 text-[11px] text-slate-400 space-y-1">
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Intelligence Cache:</span>
          <span className="text-emerald-400 font-mono font-medium">Valid (100%)</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Footage Immutability:</span>
          <span className="text-cyan font-mono">Enforced (RO)</span>
        </div>
      </div>
    </div>
  );
};

