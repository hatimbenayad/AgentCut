import React, { useState } from 'react';
import { Sparkles, MessageSquare, Mic, VolumeX, Check, Edit2, Play } from 'lucide-react';
import { usePlaybackStore } from '../stores/playbackStore';

interface WordItem {
  id: string;
  word: string;
  start: number;
  end: number;
  speaker: string;
  is_filler: boolean;
}

export const AnalysisReview: React.FC = () => {
  const { setCurrentTime, currentTime } = usePlaybackStore();

  const [words, setWords] = useState<WordItem[]>([
    { id: 'w1', word: 'Welcome', start: 0.5, end: 1.1, speaker: 'speaker_0', is_filler: false },
    { id: 'w2', word: 'to', start: 1.1, end: 1.3, speaker: 'speaker_0', is_filler: false },
    { id: 'w3', word: 'AgentCut,', start: 1.3, end: 1.9, speaker: 'speaker_0', is_filler: false },
    { id: 'w4', word: 'um,', start: 2.1, end: 2.5, speaker: 'speaker_0', is_filler: true },
    { id: 'w5', word: 'the', start: 2.8, end: 3.0, speaker: 'speaker_0', is_filler: false },
    { id: 'w6', word: 'first', start: 3.0, end: 3.4, speaker: 'speaker_0', is_filler: false },
    { id: 'w7', word: 'AI-native', start: 3.4, end: 4.1, speaker: 'speaker_0', is_filler: false },
    { id: 'w8', word: 'video', start: 4.1, end: 4.6, speaker: 'speaker_0', is_filler: false },
    { id: 'w9', word: 'production', start: 4.6, end: 5.3, speaker: 'speaker_0', is_filler: false },
    { id: 'w10', word: 'studio.', start: 5.3, end: 5.9, speaker: 'speaker_0', is_filler: false },
  ]);

  const silences = [
    { type: 'conversational', start: 1.9, end: 2.1, label: '0.2s Cadence Pause (Preserve)' },
    { type: 'filler', start: 2.1, end: 2.5, label: 'Filler word "um" (Auto-Trim Candidate)' },
    { type: 'dead_silence', start: 2.5, end: 2.8, label: '0.3s Dead Air (Tightened)' },
  ];

  return (
    <div className="flex-1 bg-studio-900 flex flex-col h-full border-r border-studio-700/60 overflow-hidden select-none">
      {/* Tab Header */}
      <div className="p-3 bg-studio-850 border-b border-studio-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-cyan" />
          <h3 className="font-semibold text-white text-xs">Video Intelligence Review</h3>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono">
          <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Whisper tiny (100%)
          </span>
          <span className="px-2 py-0.5 rounded bg-studio-700 text-slate-300">
            English (0.99)
          </span>
        </div>
      </div>

      {/* Pauses & Acoustic Energy Bar */}
      <div className="p-3 bg-studio-950/60 border-b border-studio-700/40">
        <label className="text-[10px] font-mono text-slate-400 block mb-1.5 uppercase">
          Acoustic Pause Classification (VAD)
        </label>
        <div className="flex gap-2">
          {silences.map((s, idx) => (
            <div
              key={idx}
              className={`p-2 rounded border text-[11px] flex items-center justify-between flex-1 ${
                s.type === 'conversational'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : s.type === 'filler'
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              <div className="flex items-center gap-1.5 truncate">
                <VolumeX className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate">{s.label}</span>
              </div>
              <span className="text-[10px] font-mono">
                {s.start}s - {s.end}s
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Transcript Editor */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        <div className="p-3 rounded-lg bg-studio-850 border border-studio-700/60 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan inline-block" />
              <span className="font-bold text-slate-200">Speaker 0 (Host)</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">[0.50s - 5.90s]</span>
          </div>

          {/* Interactive Word Tokens */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {words.map((w) => {
              const isWordActive = currentTime >= w.start && currentTime <= w.end;
              return (
                <button
                  key={w.id}
                  onClick={() => setCurrentTime(w.start)}
                  className={`px-2 py-1 rounded text-xs transition font-sans flex items-center gap-1 ${
                    isWordActive
                      ? 'bg-cyan text-studio-950 font-bold shadow-md shadow-cyan/30 scale-105'
                      : w.is_filler
                      ? 'bg-amber-500/15 border border-amber-400/40 text-amber-300 line-through opacity-75'
                      : 'bg-studio-800 hover:bg-studio-700 text-slate-200 border border-studio-700/60'
                  }`}
                  title={`Seek to ${w.start}s`}
                >
                  <span>{w.word}</span>
                  {w.is_filler && (
                    <span className="text-[8px] font-mono px-1 rounded bg-amber-400 text-black font-extrabold not-italic">
                      FILLER
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* OCR On-Screen Text Detections */}
        <div className="p-3 rounded-lg bg-studio-850 border border-studio-700/60 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-200 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span>RapidOCR On-Screen Text Tracking</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400">PP-OCRv4 (ONNX)</span>
          </div>

          <div className="p-2 rounded bg-studio-900 border border-studio-700/40 flex items-center justify-between text-[11px]">
            <span className="font-mono text-violet-300 font-semibold">"AGENTCUT AI-NATIVE VIDEO STUDIO"</span>
            <span className="text-[10px] font-mono text-slate-400">IoU: 0.94 • [0.5s - 4.5s]</span>
          </div>
        </div>
      </div>
    </div>
  );
};

