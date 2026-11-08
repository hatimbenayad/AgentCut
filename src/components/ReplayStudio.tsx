import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RotateCcw, X, Scissors, Hand, Type, MousePointer, Sparkles, Activity } from 'lucide-react';
import { useReplayStore } from '../stores/replayStore';

export const ReplayStudio: React.FC = () => {
  const {
    isReplayOpen,
    isReplayPlaying,
    replayTime,
    speedMultiplier,
    totalDuration,
    setIsReplayOpen,
    setIsReplayPlaying,
    setReplayTime,
    setSpeedMultiplier,
    restartReplay,
  } = useReplayStore();

  const animationRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(performance.now());

  // 60 FPS animation loop
  useEffect(() => {
    if (!isReplayOpen || !isReplayPlaying) return;

    lastTimeRef.current = performance.now();
    const updateLoop = (now: number) => {
      const deltaSec = (now - lastTimeRef.current) / 1000.0;
      lastTimeRef.current = now;

      const nextTime = replayTime + deltaSec * speedMultiplier;
      if (nextTime >= totalDuration) {
        setReplayTime(totalDuration);
        setIsReplayPlaying(false);
      } else {
        setReplayTime(nextTime);
        animationRef.current = requestAnimationFrame(updateLoop);
      }
    };

    animationRef.current = requestAnimationFrame(updateLoop);
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isReplayOpen, isReplayPlaying, replayTime, speedMultiplier, totalDuration]);

  if (!isReplayOpen) return null;

  // Simulated synthetic 60 FPS multi-cursor trajectory based on current replay time
  // Cursor 1: Video Editor (Cyan) - Drags clip, splits at 2.5s, applies punch-in
  const t = replayTime;
  let editorX = 200 + Math.sin(t * 1.5) * 250 + t * 40;
  let editorY = 350 + Math.cos(t * 2.0) * 80;
  let editorTool = 'grab';
  let editorAction = 'Placing raw footage on Track V1';

  if (t > 2.0 && t < 4.0) {
    editorTool = 'razor';
    editorAction = 'Razor slicing clip at 22.5s';
    editorX = 540;
    editorY = 480;
  } else if (t >= 4.0) {
    editorTool = 'pointer';
    editorAction = 'Punch-in 1.15x applied to segment B';
    editorX = 680;
    editorY = 480;
  }

  // Cursor 2: Caption Designer (Amber) - Stamping typography
  let captionX = 400 + Math.cos(t * 1.8) * 150;
  let captionY = 220 + Math.sin(t * 1.2) * 60;
  let captionTool = 'pointer';
  let captionAction = 'Analyzing transcript timing';

  if (t > 3.0) {
    captionTool = 'text_stamp';
    captionAction = 'Stamping animated kinetic subtitles';
    captionX = 500;
    captionY = 420;
  }

  // Cursor 3: Footage Analyst (Orange)
  let analystX = 180 + Math.cos(t * 0.9) * 80;
  let analystY = 280 + Math.sin(t * 0.9) * 60;

  const renderToolIcon = (iconName: string) => {
    switch (iconName) {
      case 'razor':
        return <Scissors className="w-3.5 h-3.5 text-white" />;
      case 'grab':
        return <Hand className="w-3.5 h-3.5 text-white" />;
      case 'text_stamp':
        return <Type className="w-3.5 h-3.5 text-white" />;
      default:
        return <MousePointer className="w-3.5 h-3.5 text-white" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-xl flex flex-col justify-between select-none">
      {/* Top Header */}
      <header className="h-16 border-b border-studio-700/80 px-6 flex items-center justify-between bg-studio-900/60">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-300">
            <Sparkles className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="font-bold text-white text-base tracking-wide flex items-center gap-2">
              CINEMATIC MULTI-CURSOR REPLAY STUDIO
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                60 FPS DETERMINISTIC
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Visualized directly from immutable SQLite event ledger #1 - #6
            </p>
          </div>
        </div>

        {/* Close Button */}
        <button
          onClick={() => setIsReplayOpen(false)}
          className="p-2 rounded-lg bg-studio-800 hover:bg-studio-700 text-slate-300 hover:text-white transition"
        >
          <X className="w-5 h-5" />
        </button>
      </header>

      {/* Main Replay Stage Canvas */}
      <div className="flex-1 relative overflow-hidden bg-gradient-to-b from-studio-950 via-studio-900 to-studio-950 p-8">
        {/* Stage Grid & Background Elements */}
        <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px]" />

        {/* Simulated Timeline Stage */}
        <div className="w-full max-w-5xl mx-auto h-72 rounded-xl border border-studio-700/60 bg-studio-900/80 shadow-2xl p-4 flex flex-col justify-between relative mt-24">
          <div className="flex items-center justify-between border-b border-studio-700/40 pb-2 text-xs font-mono text-slate-400">
            <span>CANONICAL TIMELINE MULTI-TRACK STAGE</span>
            <span className="text-cyan font-semibold">T = {replayTime.toFixed(2)}s</span>
          </div>

          {/* Track C1 */}
          <div className="h-10 rounded bg-studio-850/80 border border-studio-700/40 flex items-center px-3 relative">
            <span className="text-[10px] font-mono text-amber-400 w-24">C1 Subtitles:</span>
            {t > 3.0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="h-7 px-3 rounded bg-amber-500/30 border border-amber-400/60 text-amber-200 text-xs flex items-center font-bold"
              >
                "THE SECRET TO MULTI-AGENT VIDEO EDITING"
              </motion.div>
            )}
          </div>

          {/* Track V1 */}
          <div className="h-16 rounded bg-studio-850/80 border border-studio-700/40 flex items-center px-3 relative">
            <span className="text-[10px] font-mono text-cyan w-24">V1 Video:</span>
            <div className="flex items-center gap-1">
              <div className="h-12 w-64 rounded bg-cyan-600/30 border border-cyan/60 px-3 flex items-center justify-between text-xs text-cyan-200">
                <span>Clip Take 1 (1.0x)</span>
                <span className="font-mono text-[10px]">0.0s - 22.5s</span>
              </div>
              {t > 2.5 && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="h-12 w-64 rounded bg-violet-600/30 border border-violet-400/70 px-3 flex items-center justify-between text-xs text-violet-200"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Segment B</span>
                    <span className="text-[10px] font-mono px-1 py-0.5 rounded bg-violet-500 text-white font-bold">
                      1.15x Punch
                    </span>
                  </div>
                  <span className="font-mono text-[10px]">22.5s - 45.0s</span>
                </motion.div>
              )}
            </div>
          </div>

          {/* Track A1 */}
          <div className="h-10 rounded bg-studio-850/80 border border-studio-700/40 flex items-center px-3">
            <span className="text-[10px] font-mono text-indigo-400 w-24">A1 Audio:</span>
            <div className="h-7 w-full rounded bg-indigo-950/60 border border-indigo-600/40 flex items-center px-2">
              <span className="text-[10px] font-mono text-indigo-300">16kHz Stereo Master • -14 LUFS Target</span>
            </div>
          </div>
        </div>

        {/* ANIMATED MULTI-AGENT CURSOR 1: Video Editor (Cyan) */}
        <div
          className="absolute pointer-events-none transition-all duration-75 ease-out z-40"
          style={{ transform: `translate3d(${editorX}px, ${editorY}px, 0)` }}
        >
          <div className="relative">
            <div className="w-7 h-7 rounded-full bg-cyan shadow-[0_0_15px_rgba(0,217,255,0.9)] flex items-center justify-center border-2 border-white">
              {renderToolIcon(editorTool)}
            </div>
            {/* Action Card Flag */}
            <div className="absolute left-8 top-0 whitespace-nowrap bg-studio-900/90 border border-cyan/50 text-cyan-200 px-2 py-1 rounded-md text-[11px] font-mono shadow-xl backdrop-blur-md">
              <span className="font-bold text-cyan">Video Editor:</span> {editorAction}
            </div>
          </div>
        </div>

        {/* ANIMATED MULTI-AGENT CURSOR 2: Caption Designer (Amber) */}
        <div
          className="absolute pointer-events-none transition-all duration-75 ease-out z-40"
          style={{ transform: `translate3d(${captionX}px, ${captionY}px, 0)` }}
        >
          <div className="relative">
            <div className="w-7 h-7 rounded-full bg-amber-400 shadow-[0_0_15px_rgba(254,211,48,0.9)] flex items-center justify-center border-2 border-white">
              {renderToolIcon(captionTool)}
            </div>
            <div className="absolute left-8 top-0 whitespace-nowrap bg-studio-900/90 border border-amber-400/50 text-amber-200 px-2 py-1 rounded-md text-[11px] font-mono shadow-xl backdrop-blur-md">
              <span className="font-bold text-amber-400">Caption Designer:</span> {captionAction}
            </div>
          </div>
        </div>

        {/* ANIMATED MULTI-AGENT CURSOR 3: Footage Analyst (Orange) */}
        <div
          className="absolute pointer-events-none transition-all duration-75 ease-out z-30"
          style={{ transform: `translate3d(${analystX}px, ${analystY}px, 0)` }}
        >
          <div className="relative">
            <div className="w-6 h-6 rounded-full bg-orange-400 shadow-[0_0_12px_rgba(240,147,43,0.8)] flex items-center justify-center border border-white">
              <Activity className="w-3 h-3 text-black" />
            </div>
            <div className="absolute left-7 top-0 whitespace-nowrap bg-studio-900/90 border border-orange-400/40 text-orange-200 px-2 py-0.5 rounded text-[10px] font-mono">
              <span className="font-bold">Analyst:</span> Inspecting VAD pauses
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Replay Transport & Speed Controls */}
      <footer className="h-20 bg-studio-900 border-t border-studio-700/80 px-8 flex items-center justify-between">
        {/* Transport */}
        <div className="flex items-center gap-3">
          <button
            onClick={restartReplay}
            className="p-2 rounded-lg bg-studio-800 hover:bg-studio-700 text-slate-300 hover:text-white transition"
            title="Restart Replay"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsReplayPlaying(!isReplayPlaying)}
            className="w-10 h-10 rounded-full bg-amber-400 hover:bg-amber-300 text-black flex items-center justify-center font-bold transition shadow-lg"
          >
            {isReplayPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
          </button>
          <span className="text-sm font-mono text-amber-300 font-semibold">
            {replayTime.toFixed(2)}s / {totalDuration.toFixed(2)}s
          </span>
        </div>

        {/* Scrub Slider */}
        <div className="flex-1 mx-8 flex items-center gap-3">
          <input
            type="range"
            min={0}
            max={totalDuration}
            step={0.01}
            value={replayTime}
            onChange={(e) => setReplayTime(parseFloat(e.target.value))}
            className="w-full accent-amber-400 cursor-pointer h-1.5 rounded-lg bg-studio-700"
          />
        </div>

        {/* Speed Controls: 0.5x, 1x, 2x, 4x */}
        <div className="flex items-center gap-1.5 bg-studio-800 p-1 rounded-lg border border-studio-700">
          {[0.5, 1.0, 2.0, 4.0].map((spd) => (
            <button
              key={spd}
              onClick={() => setSpeedMultiplier(spd)}
              className={`px-2.5 py-1 rounded text-xs font-mono font-semibold transition ${
                speedMultiplier === spd
                  ? 'bg-amber-400 text-black'
                  : 'text-slate-400 hover:text-white hover:bg-studio-700'
              }`}
            >
              {spd}x
            </button>
          ))}
        </div>
      </footer>
    </div>
  );
};

