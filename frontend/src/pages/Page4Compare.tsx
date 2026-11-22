import React from 'react';
import {
  GitCompare,
  BarChart2,
  Clock,
  RotateCw,
  ArrowRight,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { MultiConditionResult, Language } from '../types';

interface Page4CompareProps {
  sourceText: string;
  language: Language;
  multiResult: MultiConditionResult | null;
  onBackToInput: () => void;
}

export const Page4Compare: React.FC<Page4CompareProps> = ({
  sourceText,
  language,
  multiResult,
  onBackToInput,
}) => {
  if (!multiResult) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <GitCompare className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Comparison Data Available</h2>
        <p className="text-slate-400 text-sm mb-6">
          Please enter or select a document on Page 1 and click "Generate All 3 Summaries".
        </p>
        <button
          onClick={onBackToInput}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition-all inline-flex items-center space-x-2 cursor-pointer"
        >
          <span>Go to Page 1: Summarization Input</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  const cards = [
    { key: 'A', data: multiResult.condition_A, tag: 'Standard Baseline', color: 'border-slate-800' },
    { key: 'B', data: multiResult.condition_B, tag: 'Factuality-Aware', color: 'border-indigo-500/30 ring-1 ring-indigo-500/10' },
    { key: 'C', data: multiResult.condition_C, tag: 'Verified & Revised', color: 'border-emerald-500/40 ring-1 ring-emerald-500/20 bg-emerald-950/10' },
  ];

  const chartData = [
    {
      condition: 'Condition A (Standard)',
      'Support Rate (%)': multiResult.condition_A.support_rate,
      'Contradiction Rate (%)': multiResult.condition_A.contradiction_rate,
      'Summary Words': multiResult.condition_A.word_count,
    },
    {
      condition: 'Condition B (Factuality)',
      'Support Rate (%)': multiResult.condition_B.support_rate,
      'Contradiction Rate (%)': multiResult.condition_B.contradiction_rate,
      'Summary Words': multiResult.condition_B.word_count,
    },
    {
      condition: 'Condition C (Revision)',
      'Support Rate (%)': multiResult.condition_C.support_rate,
      'Contradiction Rate (%)': multiResult.condition_C.contradiction_rate,
      'Summary Words': multiResult.condition_C.word_count,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-sm font-semibold mb-1">
            <GitCompare className="w-4 h-4" />
            <span>PAGE 4 — THREE-WAY CONDITION COMPARISON</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Methodology Comparison: Condition A vs. B vs. C
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Visualizing the impact of language-adaptive constraints (B) and NLI-guided targeted claim revision (C).
          </p>
        </div>
      </div>

      {/* 3 Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map(({ key, data, tag, color }) => (
          <div
            key={key}
            className={`bg-slate-900 border rounded-2xl p-6 space-y-4 flex flex-col justify-between shadow-sm transition-all ${color}`}
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="font-bold text-sm text-white">[{key}] {data.name}</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-semibold border bg-slate-800 text-slate-300 border-slate-700">
                  {tag}
                </span>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans min-h-[160px] whitespace-pre-wrap select-text">
                {data.summary}
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center">
                  <span className="text-slate-400 block text-[11px]">Support Rate</span>
                  <span className="font-bold text-emerald-400 text-base font-mono">{data.support_rate}%</span>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center">
                  <span className="text-slate-400 block text-[11px]">Contradiction</span>
                  <span className="font-bold text-rose-400 text-base font-mono">{data.contradiction_rate}%</span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 px-1 font-mono">
                <span>Length: {data.word_count} words</span>
                <span>Latency: {data.inference_time_sec}s</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Visual Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BarChart2 className="w-4 h-4 text-indigo-400" />
            <h3 className="font-bold text-white text-sm">Empirical Condition Delta on Current Input</h3>
          </div>
          <span className="text-xs text-slate-500">Higher support & lower contradiction indicates superior factuality</span>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="condition" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                labelStyle={{ color: '#f8fafc', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="Support Rate (%)" fill="#10b981" radius={[6, 6, 0, 0]} />
              <Bar dataKey="Contradiction Rate (%)" fill="#f43f5e" radius={[6, 6, 0, 0]} />
              <Bar dataKey="Summary Words" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
