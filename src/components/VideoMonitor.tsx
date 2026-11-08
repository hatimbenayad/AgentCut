import React from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, Maximize2, RotateCcw } from 'lucide-react';
import { usePlaybackStore } from '../stores/playbackStore';
import { useProjectStore } from '../stores/projectStore';

export const VideoMonitor: React.FC = () => {
  const { currentTime, duration, isPlaying, togglePlay, setCurrentTime } = usePlaybackStore();
  const { width, height, captions, tracks } = useProjectStore();

  const isVertical = height > width;

  // Format timecode HH:MM:SS:FF
  const formatTimecode = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    const frames = Math.floor((sec % 1) * 30);
    return `00:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;
  };

  // Find active caption
  const activeCaption = captions.find(
    (c) => currentTime >= c.timeline_in && currentTime <= c.timeline_out
  );

  // Check if current video clip has punch-in
  const vTrack = tracks.find((t) => t.track_type === 'video');
  const activeClip = vTrack?.clips.find(
    (c) => currentTime >= c.timeline_in && currentTime <= c.timeline_out
  );
  const isPunchedIn = (activeClip?.scale || 1.0) > 1.05;

  return (
    <div className="flex-1 bg-studio-950 flex flex-col justify-between overflow-hidden relative">
      {/* Video Framing Canvas */}
      <div className="flex-1 flex items-center justify-center p-4 relative">
        <div
          className={`relative bg-studio-900 border border-studio-700/80 rounded-lg overflow-hidden shadow-2xl flex flex-col items-center justify-center transition-all ${
            isVertical ? 'w-[320px] h-[568px]' : 'w-[640px] h-[360px]'
          }`}
        >
          {/* Simulated Frame Preview */}
          <div className="absolute inset-0 bg-gradient-to-br from-studio-900 via-studio-850 to-studio-950 flex items-center justify-center">
            {/* Visual simulation of interview scene with dynamic punch-in */}
            <div
              className={`w-full h-full flex flex-col items-center justify-center transition-transform duration-300 ${
                isPunchedIn ? 'scale-[1.15]' : 'scale-100'
              }`}
            >
              <div className="w-24 h-24 rounded-full bg-studio-800 border-2 border-cyan/40 flex items-center justify-center shadow-lg relative">
                <span className="text-3xl">🎙️</span>
                {isPunchedIn && (
                  <span className="absolute -top-3 -right-3 text-[10px] font-mono px-1.5 py-0.5 rounded bg-violet-600 text-white font-bold animate-pulse">
                    1.15x
                  </span>
                )}
              </div>
              <span className="text-xs font-mono text-slate-400 mt-3">Speaker 0 (Podcast Host)</span>
            </div>

            {/* Dynamic Animated Subtitle Overlay */}
            {activeCaption && (
              <div className="absolute bottom-10 left-4 right-4 text-center z-10 pointer-events-none">
                <span className="inline-block px-3 py-1.5 rounded-lg bg-black/85 backdrop-blur-md border border-amber-400/30 text-amber-300 font-extrabold text-sm tracking-wide shadow-xl uppercase font-sans">
                  {activeCaption.text}
                </span>
              </div>
            )}
          </div>

          {/* Aspect & Punch-in HUD Badge */}
          <div className="absolute top-3 left-3 flex gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/70 text-slate-300 backdrop-blur-sm border border-white/10">
              {width}x{height}
            </span>
            {isPunchedIn && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan/20 text-cyan border border-cyan/40">
                PUNCH-IN ZOOM
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Playback Controls & Timecode Bar */}
      <div className="h-12 bg-studio-900/90 border-t border-studio-700/60 px-4 flex items-center justify-between text-xs select-none">
        {/* Timecode display */}
        <div className="flex items-center gap-2 font-mono">
          <span className="text-cyan font-semibold text-sm">{formatTimecode(currentTime)}</span>
          <span className="text-slate-400">/</span>
          <span className="text-slate-400">{formatTimecode(duration)}</span>
        </div>

        {/* Center Transport Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentTime(0)}
            className="p-1.5 rounded hover:bg-studio-800 text-slate-400 hover:text-white transition"
            title="Rewind to Start"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentTime(Math.max(0, currentTime - 1.0))}
            className="p-1.5 rounded hover:bg-studio-800 text-slate-400 hover:text-white transition"
            title="Step Back 1s"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={togglePlay}
            className="w-8 h-8 rounded-full bg-cyan hover:bg-cyan-400 text-studio-950 flex items-center justify-center font-bold transition shadow-md"
            title="Play / Pause (Space)"
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
          </button>
          <button
            onClick={() => setCurrentTime(Math.min(duration, currentTime + 1.0))}
            className="p-1.5 rounded hover:bg-studio-800 text-slate-400 hover:text-white transition"
            title="Step Forward 1s"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* Right Tools */}
        <div className="flex items-center gap-3 text-slate-400">
          <div className="flex items-center gap-1.5">
            <Volume2 className="w-4 h-4" />
            <span className="font-mono text-[11px]">-14 LUFS</span>
          </div>
        </div>
      </div>
    </div>
  );
};

