import React, { useState } from 'react';
import { X, Download, CheckCircle2, Video, Sparkles, Layers } from 'lucide-react';
import { useProjectStore } from '../stores/projectStore';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose }) => {
  const { name, width, height, fps, duration } = useProjectStore();
  const [preset, setPreset] = useState<'tiktok' | 'youtube' | 'prores'>('tiktok');
  const [engine, setEngine] = useState<'ffmpeg' | 'melt'>('ffmpeg');
  const [isRendering, setIsRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [isRenderComplete, setIsRenderComplete] = useState(false);

  if (!isOpen) return null;

  const handleStartRender = () => {
    setIsRendering(true);
    setRenderProgress(0);
    setIsRenderComplete(false);

    // Simulated render progress
    const interval = setInterval(() => {
      setRenderProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsRendering(false);
          setIsRenderComplete(true);
          return 100;
        }
        return prev + 20;
      });
    }, 250);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 select-none">
      <div className="w-[520px] rounded-xl bg-studio-900 border border-studio-700/80 shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-studio-700/60 flex items-center justify-between bg-studio-850">
          <div className="flex items-center gap-2">
            <Download className="w-4 h-4 text-cyan" />
            <h3 className="font-semibold text-white text-sm">Export Video Broadcast Deliverable</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-studio-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Preset Selector */}
          <div>
            <label className="text-slate-400 font-mono text-[11px] block mb-2">EXPORT PRESET</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'tiktok', name: 'TikTok / Reels', res: '1080x1920 (9:16)', fps: '30fps MP4' },
                { id: 'youtube', name: 'YouTube Broadcast', res: '1920x1080 (16:9)', fps: '60fps MP4' },
                { id: 'prores', name: 'ProRes Master', res: 'Native 4K', fps: 'ProRes 422' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setPreset(item.id as any)}
                  className={`p-2.5 rounded-lg border text-left transition ${
                    preset === item.id
                      ? 'bg-cyan/15 border-cyan text-white shadow-sm'
                      : 'bg-studio-850 border-studio-700 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  <span className="font-semibold text-xs block text-slate-200">{item.name}</span>
                  <span className="text-[10px] font-mono block text-slate-400 mt-1">{item.res}</span>
                  <span className="text-[9px] font-mono text-cyan">{item.fps}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Dual-Engine Architecture Selector */}
          <div>
            <label className="text-slate-400 font-mono text-[11px] block mb-2">RENDER ENGINE (ADR-002)</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setEngine('ffmpeg')}
                className={`p-2.5 rounded-lg border text-left transition ${
                  engine === 'ffmpeg'
                    ? 'bg-cyan/15 border-cyan text-white'
                    : 'bg-studio-850 border-studio-700 text-slate-400'
                }`}
              >
                <div className="font-semibold text-xs text-slate-200 flex items-center justify-between">
                  <span>Native FFmpeg Graph</span>
                  <span className="text-[9px] font-mono px-1 py-0.5 rounded bg-cyan/20 text-cyan">Verified</span>
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  Filtergraph concat, dynamic jump cuts, and burn-in typography.
                </p>
              </button>

              <button
                onClick={() => setEngine('melt')}
                className={`p-2.5 rounded-lg border text-left transition ${
                  engine === 'melt'
                    ? 'bg-cyan/15 border-cyan text-white'
                    : 'bg-studio-850 border-studio-700 text-slate-400'
                }`}
              >
                <div className="font-semibold text-xs text-slate-200 flex items-center justify-between">
                  <span>Headless Melt / Kdenlive</span>
                  <span className="text-[9px] font-mono px-1 py-0.5 rounded bg-violet-500/20 text-violet-300">XML</span>
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  MLT producer graph & native .kdenlive project file export.
                </p>
              </button>
            </div>
          </div>

          {/* Render Progress or Status */}
          {isRendering && (
            <div className="p-3 bg-studio-950 rounded-lg border border-studio-700 space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-cyan animate-pulse">Rendering {preset.toUpperCase()}...</span>
                <span className="text-white font-bold">{renderProgress}%</span>
              </div>
              <div className="h-2 rounded-full bg-studio-800 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan to-violet-500 transition-all duration-200"
                  style={{ width: `${renderProgress}%` }}
                />
              </div>
            </div>
          )}

          {isRenderComplete && (
            <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <div>
                  <span className="font-bold">Render Verified & Complete!</span>
                  <p className="text-[10px] text-emerald-400/80 font-mono">
                    vertical_slice_final.mp4 (202 KB) • Duration: {duration}s
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                100% OK
              </span>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-studio-850 border-t border-studio-700/60 flex items-center justify-between">
          <span className="text-[11px] font-mono text-slate-400">
            Est. Size: ~18.4 MB • Codec: H.264 High 4:2:0
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg bg-studio-700 hover:bg-studio-600 text-slate-300 text-xs font-medium transition"
            >
              Cancel
            </button>
            <button
              disabled={isRendering}
              onClick={handleStartRender}
              className="px-4 py-1.5 rounded-lg bg-cyan hover:bg-cyan-400 text-studio-950 text-xs font-bold transition shadow-md flex items-center gap-1.5 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{isRendering ? 'Rendering...' : 'Dispatch Render'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

