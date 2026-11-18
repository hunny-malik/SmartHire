import React from 'react';
import { ArrowRight, Layers, CheckCircle2, AlertCircle } from 'lucide-react';

interface DagNode {
  id: string;
  label: string;
  priority: string;
  importance: number;
}

interface DagEdge {
  from: string;
  to: string;
}

interface PrerequisiteGraphProps {
  dag: {
    nodes: DagNode[];
    edges: DagEdge[];
  };
  transitionPath: string[];
}

export const PrerequisiteGraph: React.FC<PrerequisiteGraphProps> = ({ dag, transitionPath }) => {
  if (!dag || !dag.nodes || dag.nodes.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 border border-slate-800 rounded-xl bg-slate-900/40">
        No prerequisite gaps detected for this role.
      </div>
    );
  }

  const getPriorityBadge = (p: string) => {
    switch (p.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'high':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'foundation':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Visual Topological Pipeline Flow */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
          <Layers className="w-4 h-4 mr-2 text-indigo-400" />
          Topological Career Transition Sequence (ESCO / O*NET Dependency Order)
        </h4>

        <div className="flex flex-wrap items-center gap-2">
          {transitionPath.map((skillName, idx) => {
            const isLast = idx === transitionPath.length - 1;
            const node = dag.nodes.find((n) => n.id === skillName);
            const priority = node?.priority || 'medium';

            return (
              <React.Fragment key={skillName}>
                <div className={`px-3 py-2 rounded-lg border text-xs font-semibold flex items-center space-x-2 shadow-sm ${getPriorityBadge(priority)}`}>
                  <span className="w-4 h-4 rounded-full bg-slate-900/80 flex items-center justify-center text-[10px]">
                    {idx + 1}
                  </span>
                  <span>{skillName}</span>
                </div>
                {!isLast && (
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Prerequisite Linkages Map */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {dag.nodes.map((node) => {
          const directPrereqs = dag.edges.filter((e) => e.to === node.id).map((e) => e.from);
          const unlocks = dag.edges.filter((e) => e.from === node.id).map((e) => e.to);

          return (
            <div key={node.id} className="p-3.5 bg-slate-900/60 border border-slate-800/80 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm text-slate-200">{node.label}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getPriorityBadge(node.priority)}`}>
                  {node.priority}
                </span>
              </div>

              <div className="space-y-1 text-xs">
                {directPrereqs.length > 0 ? (
                  <div className="text-slate-400 flex items-start">
                    <span className="text-slate-500 w-24 shrink-0">Prerequisites:</span>
                    <span className="text-indigo-300 font-medium">{directPrereqs.join(', ')}</span>
                  </div>
                ) : (
                  <div className="text-slate-500 flex items-center">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400 mr-1" /> Foundational Competency
                  </div>
                )}

                {unlocks.length > 0 && (
                  <div className="text-slate-400 flex items-start">
                    <span className="text-slate-500 w-24 shrink-0">Unlocks:</span>
                    <span className="text-purple-300 font-medium">{unlocks.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
