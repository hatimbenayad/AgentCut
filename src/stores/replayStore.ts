import { create } from 'zustand';

export interface CursorState {
  agent_id: string;
  name: string;
  role: string;
  color: string;
  x: number;
  y: number;
  icon: string;
  is_active: boolean;
  action_label?: string;
}

export interface ReplayFrame {
  frame: number;
  timestamp_sec: number;
  cursors: CursorState[];
  haptics: Array<{ type: string; x: number; y: number; color: string }>;
}

interface ReplayState {
  isReplayOpen: boolean;
  isReplayPlaying: boolean;
  replayTime: number;
  speedMultiplier: number;
  totalDuration: number;
  frames: ReplayFrame[];
  agents: Array<{ agent_id: string; name: string; role: string; color: string }>;
  setIsReplayOpen: (open: boolean) => void;
  setIsReplayPlaying: (playing: boolean) => void;
  setReplayTime: (time: number) => void;
  setSpeedMultiplier: (speed: number) => void;
  setReplayData: (data: { total_duration_sec: number; frames: ReplayFrame[]; agents: any[] }) => void;
  restartReplay: () => void;
}

export const useReplayStore = create<ReplayState>((set) => ({
  isReplayOpen: false,
  isReplayPlaying: false,
  replayTime: 0.0,
  speedMultiplier: 1.0,
  totalDuration: 6.0,
  frames: [],
  agents: [
    { agent_id: 'agt_dir', name: 'Director', role: 'director', color: '#E056FD' },
    { agent_id: 'agt_ana', name: 'Footage Analyst', role: 'analyst', color: '#F0932B' },
    { agent_id: 'agt_edt', name: 'Video Editor', role: 'editor', color: '#00D9FF' },
    { agent_id: 'agt_aud', name: 'Audio Engineer', role: 'audio', color: '#686DE0' },
    { agent_id: 'agt_cap', name: 'Caption Designer', role: 'captions', color: '#FED330' },
    { agent_id: 'agt_col', name: 'Colorist', role: 'colorist', color: '#6AB04C' },
    { agent_id: 'agt_qc', name: 'Quality Controller', role: 'qc', color: '#EB4D4B' },
  ],
  setIsReplayOpen: (open) => set({ isReplayOpen: open, isReplayPlaying: open }),
  setIsReplayPlaying: (playing) => set({ isReplayPlaying: playing }),
  setReplayTime: (time) => set({ replayTime: time }),
  setSpeedMultiplier: (speed) => set({ speedMultiplier: speed }),
  setReplayData: (data) =>
    set({
      totalDuration: data.total_duration_sec,
      frames: data.frames,
      agents: data.agents,
    }),
  restartReplay: () => set({ replayTime: 0.0, isReplayPlaying: true }),
}));

