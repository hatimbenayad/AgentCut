import React from 'react';
import { Activity, Shield, Lock, Terminal, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAgentStore } from '../stores/agentStore';

export const AgentActivityPanel: React.FC = () => {
  const { agents, logs, activeLocks } = useAgentStore();

  return (
    <div className="w-80 bg-studio-900 border-l border-studio-700/60 flex flex-col h-full select-none text-xs">
      {/* Header */}
      <div className="p-3 border-b border-studio-700/60 flex items-center justify-between">
        <div className="flex items-center gap-2 font-semibold uppercase tracking-wider text-slate-300">
          <Activity className="w-3.5 h-3.5 text-cyan" />
          <span>Agent Swarm</span>
        </div>
        <div className="flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          <Shield className="w-3 h-3" />
          <span>QC Guard Active</span>
        </div>
      </div>

      {/* 7 Specialized Agent Cards */}
      <div className="p-2 border-b border-studio-700/60 bg-studio-950/40 space-y-1.5 max-h-48 overflow-y-auto">
        {agents.map((agt) => (
          <div
            key={agt.agent_id}
            className="p-1.5 rounded bg-studio-850/80 border border-studio-700/40 flex items-center justify-between"
          >
            <div className="flex items-center gap-2 overflow-hidden">
              <div
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: agt.color }}
              />
              <div className="truncate">
                <span className="font-semibold text-slate-200">{agt.name}</span>
                <p className="text-[10px] text-slate-400 truncate">{agt.current_task}</p>
              </div>
            </div>
            <span
              className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-semibold uppercase ${
                agt.status === 'active'
                  ? 'bg-cyan/20 text-cyan animate-pulse'
                  : agt.status === 'completed'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-studio-700 text-slate-400'
              }`}
            >
              {agt.status}
            </span>
          </div>
        ))}
      </div>

      {/* Active Interval Locks */}
      <div className="p-2.5 bg-studio-900 border-b border-studio-700/60">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-1.5">
          <span className="flex items-center gap-1">
            <Lock className="w-3 h-3 text-amber-400" />
            <span>Active Interval Locks</span>
          </span>
          <span className="text-amber-400 font-bold">{activeLocks.length}</span>
        </div>
        <div className="space-y-1">
          {activeLocks.map((lk, i) => (
            <div
              key={i}
              className="text-[10px] font-mono p-1 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 flex justify-between"
            >
              <span>{lk.track_id}</span>
              <span>
                [{lk.start.toFixed(1)}s - {lk.end.toFixed(1)}s]
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Monotonic Event Ledger Log Feed */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-2 px-3 bg-studio-950/60 border-b border-studio-700/40 text-[10px] font-mono text-slate-400 flex items-center justify-between">
          <span className="flex items-center gap-1">
            <Terminal className="w-3 h-3 text-cyan" />
            <span>SQLite Event Ledger</span>
          </span>
          <span>{logs.length} Operations</span>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1.5 font-mono text-[11px]">
          {logs.map((log) => (
            <div
              key={log.id}
              className="p-1.5 rounded bg-studio-850 border border-studio-700/40 space-y-0.5 hover:border-slate-500/40 transition"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full inline-block"
                    style={{ backgroundColor: log.agent_color }}
                  />
                  <span className="font-semibold text-slate-200">{log.agent_name}</span>
                </div>
                <span className="text-[10px] text-slate-400">#{log.sequence_number}</span>
              </div>
              <p className="text-[10px] text-slate-300 font-sans leading-tight pl-3.5">
                {log.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

