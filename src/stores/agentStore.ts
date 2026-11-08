import { create } from 'zustand';

export interface AgentInfo {
  agent_id: string;
  name: string;
  role: string;
  color: string;
  status: 'idle' | 'active' | 'completed';
  current_task: string;
}

export interface ActivityLog {
  id: string;
  sequence_number: number;
  agent_id: string;
  agent_name: string;
  agent_color: string;
  action_type: string;
  description: string;
  timestamp: string;
}

interface AgentState {
  agents: AgentInfo[];
  logs: ActivityLog[];
  activeLocks: Array<{ track_id: string; agent_id: string; start: number; end: number }>;
  addLog: (log: ActivityLog) => void;
  updateAgentStatus: (agentId: string, status: 'idle' | 'active' | 'completed', task: string) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [
    { agent_id: 'agt_dir', name: 'Director', role: 'director', color: '#E056FD', status: 'completed', current_task: 'Narrative structure planned' },
    { agent_id: 'agt_ana', name: 'Footage Analyst', role: 'analyst', color: '#F0932B', status: 'completed', current_task: 'Intelligence graph ingested' },
    { agent_id: 'agt_edt', name: 'Video Editor', role: 'editor', color: '#00D9FF', status: 'active', current_task: 'Applying 1.15x jump cut punch-in' },
    { agent_id: 'agt_aud', name: 'Audio Engineer', role: 'audio', color: '#686DE0', status: 'idle', current_task: 'Awaiting timeline final cut' },
    { agent_id: 'agt_cap', name: 'Caption Designer', role: 'captions', color: '#FED330', status: 'active', current_task: 'Syncing kinetic yellow captions' },
    { agent_id: 'agt_col', name: 'Colorist', role: 'colorist', color: '#6AB04C', status: 'idle', current_task: 'Ready for film curve grading' },
    { agent_id: 'agt_qc', name: 'Quality Controller', role: 'qc', color: '#EB4D4B', status: 'idle', current_task: 'Monitoring black gap invariants' },
  ],
  logs: [
    {
      id: 'log_01',
      sequence_number: 1,
      agent_id: 'agt_dir',
      agent_name: 'Director',
      agent_color: '#E056FD',
      action_type: 'plan_decompose',
      description: 'Decomposed creative prompt into 45s high-retention TikTok pacing',
      timestamp: '14:15:02'
    },
    {
      id: 'log_02',
      sequence_number: 2,
      agent_id: 'agt_ana',
      agent_name: 'Footage Analyst',
      agent_color: '#F0932B',
      action_type: 'intelligence_query',
      description: 'Isolated 3 dead air pauses (>1.5s) and 2 viral hooks from Whisper transcript',
      timestamp: '14:15:04'
    },
    {
      id: 'log_03',
      sequence_number: 3,
      agent_id: 'agt_edt',
      agent_name: 'Video Editor',
      agent_color: '#00D9FF',
      action_type: 'media_drag_drop',
      description: 'Placed raw footage take onto Video Track V1',
      timestamp: '14:15:06'
    },
    {
      id: 'log_04',
      sequence_number: 4,
      agent_id: 'agt_edt',
      agent_name: 'Video Editor',
      agent_color: '#00D9FF',
      action_type: 'clip_split',
      description: 'Razor sliced clip at 22.5s for conversational tightening',
      timestamp: '14:15:08'
    },
    {
      id: 'log_05',
      sequence_number: 5,
      agent_id: 'agt_edt',
      agent_name: 'Video Editor',
      agent_color: '#00D9FF',
      action_type: 'punch_in_apply',
      description: 'Applied 1.15x scale zoom to segment 2 to mask jump cut',
      timestamp: '14:15:10'
    },
    {
      id: 'log_06',
      sequence_number: 6,
      agent_id: 'agt_cap',
      agent_name: 'Caption Designer',
      agent_color: '#FED330',
      action_type: 'caption_stamp',
      description: 'Stamped dynamic typography overlay with cyan active word highlight',
      timestamp: '14:15:12'
    }
  ],
  activeLocks: [
    { track_id: 'track_video_1', agent_id: 'agt_edt', start: 22.0, end: 45.0 },
    { track_id: 'track_captions', agent_id: 'agt_cap', start: 0.0, end: 45.0 },
  ],
  addLog: (log) => set((state) => ({ logs: [log, ...state.logs] })),
  updateAgentStatus: (agentId, status, task) =>
    set((state) => ({
      agents: state.agents.map((a) =>
        a.agent_id === agentId ? { ...a, status, current_task: task } : a
      ),
    })),
}));

