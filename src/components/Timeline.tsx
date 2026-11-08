import React, { useRef } from 'react';
import { Scissors, ZoomIn, ZoomOut, Magnet, Sparkles } from 'lucide-react';
import { useProjectStore, TimelineClip } from '../stores/projectStore';
import { usePlaybackStore } from '../stores/playbackStore';

export const Timeline: React.FC = () => {
  const { tracks, captions, duration, splitClipAt } = useProjectStore();
  const { currentTime, setCurrentTime } = usePlaybackStore();
  const timelineRef = useRef<HTMLDivElement>(null);

  const pixelsPerSecond = 20; // 20px per second scale
  const totalWidth = duration * pixelsPerSecond;

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = Math.max(0, Math.min(duration, clickX / pixelsPerSecond));
    setCurrentTime(newTime);
  };

  const handleSplitCurrent = () => {
    // Split active video clip at playhead
    const vTrack = tracks.find((t) => t.track_type === 'video');
    if (!vTrack) return;
    const clipToSplit = vTrack.clips.find(
      (c) => currentTime > c.timeline_in && currentTime < c.timeline_out
    );
    if (clipToSplit) {
      splitClipAt(clipToSplit.clip_id, currentTime);
    }
  };

  return (
    <div className="h-64 bg-studio-900 border-t border-studio-700/60 flex flex-col select-none">
      {/* Timeline Toolbar */}
      <div className="h-9 px-4 bg-studio-950/60 border-b border-studio-700/40 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <button
            onClick={handleSplitCurrent}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-studio-800 hover:bg-studio-700 text-slate-300 border border-studio-700 hover:text-cyan transition"
            title="Split Clip at Playhead (C)"
          >
            <Scissors className="w-3.5 h-3.5" />
            <span className="text-[11px] font-medium">Split (C)</span>
          </button>
          <div className="h-3 w-[1px] bg-studio-700 mx-1" />
          <span className="text-[11px] text-slate-400 font-mono">Snap: Enabled (1 frame)</span>
        </div>

        <div className="flex items-center gap-3 text-slate-400 text-[11px] font-mono">
          <span>Scale: 1.0x (Fit)</span>
          <span>Zoom: 100%</span>
        </div>
      </div>

      {/* Multitrack Canvas */}
      <div className="flex-1 flex overflow-hidden">
        {/* Track Headers */}
        <div className="w-36 bg-studio-900 border-r border-studio-700/60 flex flex-col z-10">
          <div className="h-6 border-b border-studio-700/40 px-2 flex items-center text-[10px] text-slate-400 font-mono">
            TRACKS
          </div>
          <div className="h-10 px-2 flex items-center justify-between border-b border-studio-700/40 text-[11px] font-medium text-amber-400">
            <span>C1 Captions</span>
          </div>
          <div className="h-14 px-2 flex items-center justify-between border-b border-studio-700/40 text-[11px] font-medium text-cyan">
            <span>V1 Video</span>
          </div>
          <div className="h-12 px-2 flex items-center justify-between border-b border-studio-700/40 text-[11px] font-medium text-indigo-400">
            <span>A1 Audio</span>
          </div>
        </div>

        {/* Timeline Tracks Area */}
        <div
          ref={timelineRef}
          onClick={handleTimelineClick}
          className="flex-1 overflow-x-auto relative bg-studio-950/90 cursor-pointer"
        >
          <div style={{ width: `${Math.max(800, totalWidth)}px` }} className="h-full relative">
            {/* Time Ruler */}
            <div className="h-6 border-b border-studio-700/40 flex items-center px-1 text-[10px] font-mono text-slate-400 relative">
              {Array.from({ length: Math.ceil(duration / 5) + 1 }).map((_, i) => (
                <div
                  key={i}
                  className="absolute"
                  style={{ left: `${i * 5 * pixelsPerSecond}px` }}
                >
                  | {i * 5}s
                </div>
              ))}
            </div>

            {/* Playhead Vertical Line */}
            <div
              className="absolute top-0 bottom-0 w-[2px] bg-cyan shadow-[0_0_8px_rgba(0,217,255,0.8)] z-30 pointer-events-none"
              style={{ left: `${currentTime * pixelsPerSecond}px` }}
            >
              <div className="w-3 h-3 bg-cyan rotate-45 -ml-[5px] -mt-1 rounded-sm shadow-sm" />
            </div>

            {/* Track C1: Captions */}
            <div className="h-10 border-b border-studio-700/40 relative flex items-center px-1">
              {captions.map((cap) => (
                <div
                  key={cap.caption_id}
                  className="absolute h-7 rounded px-2 bg-amber-500/20 border border-amber-400/40 flex items-center text-[10px] font-medium text-amber-300 truncate shadow-sm overflow-hidden"
                  style={{
                    left: `${cap.timeline_in * pixelsPerSecond}px`,
                    width: `${(cap.timeline_out - cap.timeline_in) * pixelsPerSecond}px`,
                  }}
                >
                  <span className="truncate">{cap.text}</span>
                </div>
              ))}
            </div>

            {/* Track V1: Video Clips */}
            <div className="h-14 border-b border-studio-700/40 relative flex items-center px-1">
              {tracks
                .find((t) => t.track_type === 'video')
                ?.clips.map((clip) => {
                  const isPunch = clip.scale > 1.05;
                  return (
                    <div
                      key={clip.clip_id}
                      className={`absolute h-11 rounded px-2.5 flex items-center justify-between text-xs font-medium border shadow-md transition-all ${
                        isPunch
                          ? 'bg-violet-600/30 border-violet-400/60 text-violet-200'
                          : 'bg-cyan-600/25 border-cyan/50 text-cyan-200'
                      }`}
                      style={{
                        left: `${clip.timeline_in * pixelsPerSecond}px`,
                        width: `${clip.duration * pixelsPerSecond}px`,
                      }}
                    >
                      <div className="truncate flex items-center gap-1.5">
                        <span className="font-semibold">{clip.name}</span>
                        {isPunch && (
                          <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-violet-500/40 text-violet-100 font-bold">
                            1.15x
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">{clip.duration.toFixed(1)}s</span>
                    </div>
                  );
                })}
            </div>

            {/* Track A1: Audio Waveform */}
            <div className="h-12 border-b border-studio-700/40 relative flex items-center px-1">
              {tracks
                .find((t) => t.track_type === 'audio')
                ?.clips.map((clip) => (
                  <div
                    key={clip.clip_id}
                    className="absolute h-9 rounded px-2 bg-indigo-900/30 border border-indigo-500/40 flex items-center overflow-hidden"
                    style={{
                      left: `${clip.timeline_in * pixelsPerSecond}px`,
                      width: `${clip.duration * pixelsPerSecond}px`,
                    }}
                  >
                    {/* Simulated Waveform peaks */}
                    <div className="flex items-center gap-[2px] w-full h-full opacity-60">
                      {Array.from({ length: Math.min(100, Math.floor(clip.duration * 4)) }).map((_, idx) => {
                        const h = 20 + Math.sin(idx * 0.4) * 15 + Math.cos(idx * 0.9) * 10;
                        return (
                          <div
                            key={idx}
                            className="w-[2px] bg-indigo-400 rounded-full"
                            style={{ height: `${Math.max(4, h)}%` }}
                          />
                        );
                      })}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

