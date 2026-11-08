import { create } from 'zustand';

interface PlaybackState {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  volume: number;
  speed: number;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  togglePlay: () => void;
  setPlaying: (playing: boolean) => void;
  setSpeed: (speed: number) => void;
  setVolume: (volume: number) => void;
}

export const usePlaybackStore = create<PlaybackState>((set) => ({
  currentTime: 0.0,
  duration: 45.0,
  isPlaying: false,
  volume: 1.0,
  speed: 1.0,
  setCurrentTime: (time) => set({ currentTime: Math.max(0, time) }),
  setDuration: (duration) => set({ duration }),
  togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
  setPlaying: (isPlaying) => set({ isPlaying }),
  setSpeed: (speed) => set({ speed }),
  setVolume: (volume) => set({ volume }),
}));

