import { create } from 'zustand';

export interface MediaAsset {
  asset_id: string;
  name: string;
  file_path: string;
  duration: number;
  resolution: string;
  fps: number;
  thumbnail_url?: string;
  waveform_peaks?: number[];
}

export interface TimelineClip {
  clip_id: string;
  asset_id: string;
  name: string;
  timeline_in: number;
  timeline_out: number;
  source_in: number;
  source_out: number;
  duration: number;
  scale: number;
  color?: string;
}

export interface TimelineCaption {
  caption_id: string;
  text: string;
  timeline_in: number;
  timeline_out: number;
  font_size: number;
  font_color: string;
  highlight_color: string;
}

export interface Track {
  track_index: number;
  track_type: 'video' | 'audio' | 'subtitle';
  name: string;
  clips: TimelineClip[];
}

interface ProjectState {
  project_id: string;
  name: string;
  width: number;
  height: number;
  fps: number;
  duration: number;
  tracks: Track[];
  captions: TimelineCaption[];
  media_bin: MediaAsset[];
  setProject: (data: Partial<ProjectState>) => void;
  addClipToTrack: (trackIndex: number, clip: TimelineClip) => void;
  splitClipAt: (clipId: string, splitTime: number) => void;
  setClipScale: (clipId: string, scale: number) => void;
  addCaption: (caption: TimelineCaption) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  project_id: 'prj_demo_001',
  name: 'Viral TikTok Podcast Clip',
  width: 1080,
  height: 1920,
  fps: 30.0,
  duration: 45.0,
  tracks: [
    {
      track_index: 3,
      track_type: 'subtitle',
      name: 'Captions C1',
      clips: []
    },
    {
      track_index: 1,
      track_type: 'video',
      name: 'Video V1',
      clips: [
        {
          clip_id: 'c_01',
          asset_id: 'ast_raw_01',
          name: 'Interview Take 1',
          timeline_in: 0.0,
          timeline_out: 22.5,
          source_in: 0.0,
          source_out: 22.5,
          duration: 22.5,
          scale: 1.0,
          color: '#00D9FF'
        },
        {
          clip_id: 'c_02',
          asset_id: 'ast_raw_01',
          name: 'Interview Take 1 (Punch-in)',
          timeline_in: 22.5,
          timeline_out: 45.0,
          source_in: 22.5,
          source_out: 45.0,
          duration: 22.5,
          scale: 1.15,
          color: '#A55EEA'
        }
      ]
    },
    {
      track_index: 2,
      track_type: 'audio',
      name: 'Audio A1 (Dialog)',
      clips: [
        {
          clip_id: 'a_01',
          asset_id: 'ast_raw_01',
          name: '16kHz PCM Dialog Bus',
          timeline_in: 0.0,
          timeline_out: 45.0,
          source_in: 0.0,
          source_out: 45.0,
          duration: 45.0,
          scale: 1.0,
          color: '#686DE0'
        }
      ]
    }
  ],
  captions: [
    {
      caption_id: 'cap_01',
      text: 'THE SECRET TO MULTI-AGENT VIDEO EDITING',
      timeline_in: 0.5,
      timeline_out: 12.0,
      font_size: 40,
      font_color: '#FED330',
      highlight_color: '#00D9FF'
    },
    {
      caption_id: 'cap_02',
      text: 'COLLABORATIVE REASONING THROUGH MCP PROTOCOL',
      timeline_in: 12.5,
      timeline_out: 44.0,
      font_size: 40,
      font_color: '#FED330',
      highlight_color: '#00D9FF'
    }
  ],
  media_bin: [
    {
      asset_id: 'ast_raw_01',
      name: 'raw_studio_interview.mp4',
      file_path: 'experiments/timeline_mlt/clip_a.mp4',
      duration: 45.0,
      resolution: '1920x1080',
      fps: 30.0
    },
    {
      asset_id: 'ast_broll_01',
      name: 'broll_coding_screen.mov',
      file_path: 'experiments/timeline_mlt/clip_b.mp4',
      duration: 18.2,
      resolution: '1920x1080',
      fps: 30.0
    }
  ],
  setProject: (data) => set((state) => ({ ...state, ...data })),
  addClipToTrack: (trackIndex, clip) =>
    set((state) => ({
      tracks: state.tracks.map((t) =>
        t.track_index === trackIndex ? { ...t, clips: [...t.clips, clip] } : t
      ),
    })),
  splitClipAt: (clipId, splitTime) =>
    set((state) => {
      let updatedTracks = state.tracks.map((t) => {
        let clip = t.clips.find((c) => c.clip_id === clipId);
        if (!clip || splitTime <= clip.timeline_in || splitTime >= clip.timeline_out) return t;
        let leftDur = splitTime - clip.timeline_in;
        let c1: TimelineClip = {
          ...clip,
          clip_id: `${clip.clip_id}_a`,
          timeline_out: splitTime,
          source_out: clip.source_in + leftDur,
          duration: leftDur,
        };
        let c2: TimelineClip = {
          ...clip,
          clip_id: `${clip.clip_id}_b`,
          timeline_in: splitTime,
          source_in: clip.source_in + leftDur,
          duration: clip.timeline_out - splitTime,
          scale: 1.15,
        };
        return {
          ...t,
          clips: t.clips.flatMap((c) => (c.clip_id === clipId ? [c1, c2] : [c])),
        };
      });
      return { tracks: updatedTracks };
    }),
  setClipScale: (clipId, scale) =>
    set((state) => ({
      tracks: state.tracks.map((t) => ({
        ...t,
        clips: t.clips.map((c) => (c.clip_id === clipId ? { ...c, scale } : c)),
      })),
    })),
  addCaption: (caption) =>
    set((state) => ({
      captions: [...state.captions, caption],
    })),
}));

