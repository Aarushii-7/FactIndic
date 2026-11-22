import React from 'react';
import {
  FileText,
  CheckCircle2,
  GitCompare,
  BarChart3,
  Layers,
  Sparkles,
} from 'lucide-react';

interface NavbarProps {
  activeTab: number;
  setActiveTab: (tab: number) => void;
  hasSummary: boolean;
  hasVerification: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  hasSummary,
  hasVerification,
}) => {
  const tabs = [
    { id: 1, name: '1. Summarization Input', icon: FileText, desc: 'Input & Options' },
    { id: 2, name: '2. Generated Summary', icon: Sparkles, desc: 'Side-by-Side Output' },
    { id: 3, name: '3. Factuality Report', icon: CheckCircle2, desc: 'Claim NLI & Revision' },
    { id: 4, name: '4. Compare A / B / C', icon: GitCompare, desc: 'Condition Delta' },
    { id: 5, name: '5. Metrics Dashboard', icon: BarChart3, desc: '500-Sample Benchmark' },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Subtitle */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab(1)}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-200 bg-clip-text text-transparent">
                  FactIndic
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Factuality-Aware Summarization & Verification System
              </p>
            </div>
          </div>

          {/* Status Badges */}
          <div className="hidden lg:flex items-center space-x-2 text-xs font-mono">
            <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
              Model: Qwen2.5-1.5B
            </span>
            <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
              NLI: mDeBERTa-v3
            </span>
            <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
              ● Mode: Live Evaluation
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-800/60 no-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{tab.name}</span>
                {tab.id === 2 && hasSummary && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
                )}
                {tab.id === 3 && hasVerification && (
                  <span className="w-2 h-2 rounded-full bg-indigo-300 ml-1" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
