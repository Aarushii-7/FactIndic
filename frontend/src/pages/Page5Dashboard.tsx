import React from 'react';
import {
  BarChart3,
  Award,
  Clock,
  FileText,
  Percent,
  CheckCircle,
  Activity,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { MultiConditionResult } from '../types';

interface Page5DashboardProps {
  multiResult: MultiConditionResult | null;
  sourceText: string;
  onBackToInput?: () => void;
}

// Universal Unicode token cleaner (handles English, Hindi, and Hinglish)
function computeLexicalMetrics(source: string, summary: string) {
  const cleanTokens = (text: string) =>
    text
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, ' ')
      .trim()
      .split(/\s+/)
      .filter(Boolean);

  const srcTokens = cleanTokens(source);
  const sumTokens = cleanTokens(summary);

  if (sumTokens.length === 0 || srcTokens.length === 0) {
    return { precision: 0, recall: 0, f1: 0 };
  }

  const srcSet = new Set(srcTokens);
  const matchedTokens = sumTokens.filter((token) => srcSet.has(token));

  const precision = matchedTokens.length / sumTokens.length;
  const uniqueMatched = new Set(matchedTokens).size;
  const recall = uniqueMatched / srcSet.size;
  const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

  return {
    precision: Number(precision.toFixed(4)),
    recall: Number(recall.toFixed(4)),
    f1: Number(f1.toFixed(4)),
  };
}

export const Page5Dashboard: React.FC<Page5DashboardProps> = ({
  multiResult,
  sourceText,
  onBackToInput,
}) => {
  if (!multiResult || !sourceText.trim()) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-sm">
        <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Sample Evaluated Yet</h2>
        <p className="text-slate-400 text-sm mb-6 max-w-md mx-auto">
          Please enter or paste your document on Page 1 and click "Generate All 3 Summaries" to compute real-time metrics for your sample.
        </p>
        {onBackToInput && (
          <button
            onClick={onBackToInput}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition-all inline-flex items-center space-x-2 cursor-pointer shadow-lg shadow-indigo-600/20"
          >
            <span>Go to Page 1: Summarization Input</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  // Calculate live metrics for each condition for this specific sample
  const metricsA = computeLexicalMetrics(sourceText, multiResult.condition_A.summary);
  const metricsB = computeLexicalMetrics(sourceText, multiResult.condition_B.summary);
  const metricsC = computeLexicalMetrics(sourceText, multiResult.condition_C.summary);

  const sampleRows = [
    {
      condition: 'Condition A (Standard Baseline)',
      precision: metricsA.precision,
      recall: metricsA.recall,
      f1: metricsA.f1,
      length: multiResult.condition_A.word_count,
      compression: multiResult.condition_A.compression_ratio,
      time: multiResult.condition_A.inference_time_sec,
      highlight: false,
    },
    {
      condition: 'Condition B (Factuality-Aware)',
      precision: metricsB.precision,
      recall: metricsB.recall,
      f1: metricsB.f1,
      length: multiResult.condition_B.word_count,
      compression: multiResult.condition_B.compression_ratio,
      time: multiResult.condition_B.inference_time_sec,
      highlight: true,
      tag: 'Recommended',
    },
    {
      condition: 'Condition C (Targeted Revision Loop)',
      precision: metricsC.precision,
      recall: metricsC.recall,
      f1: metricsC.f1,
      length: multiResult.condition_C.word_count,
      compression: multiResult.condition_C.compression_ratio,
      time: multiResult.condition_C.inference_time_sec,
      highlight: false,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-sm font-semibold mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>PAGE 5 — EVALUATION METRICS DASHBOARD</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Live Sample Evaluation Metrics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Computed in real time based on the active sample passed on Page 1 across Condition A, Condition B, and Condition C.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Active Sample Evaluated</span>
          </span>
        </div>
      </div>

      {/* 6 Key Stat Cards (Reflecting Condition B for current sample) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Precision</span>
            <Award className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {metricsB.precision}
          </div>
          <div className="text-[11px] text-slate-500">Source alignment</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Recall</span>
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {metricsB.recall}
          </div>
          <div className="text-[11px] text-slate-500">Content coverage</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>F1-Score</span>
            <Activity className="w-3.5 h-3.5 text-violet-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {metricsB.f1}
          </div>
          <div className="text-[11px] text-slate-500">Where applicable</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Avg Length</span>
            <FileText className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {multiResult.condition_B.word_count}w
          </div>
          <div className="text-[11px] text-slate-500">Summary words</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Compression</span>
            <Percent className="w-3.5 h-3.5 text-teal-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {multiResult.condition_B.compression_ratio}%
          </div>
          <div className="text-[11px] text-slate-500">Ratio vs source</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Inference Time</span>
            <Clock className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {multiResult.condition_B.inference_time_sec}s
          </div>
          <div className="text-[11px] text-slate-500">Sample latency</div>
        </div>
      </div>

      {/* Metrics Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white tracking-tight">
              Evaluation Metrics for Active Sample
            </h2>
          </div>
          <span className="text-xs text-slate-400">Precision · Recall · F1 · Length · Compression · Latency</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Condition</th>
                <th className="py-3.5 px-4 text-indigo-300">Precision</th>
                <th className="py-3.5 px-4 text-emerald-300">Recall</th>
                <th className="py-3.5 px-4 text-violet-300">F1-Score (wherever applicable)</th>
                <th className="py-3.5 px-4 text-amber-300">Average Summary Length</th>
                <th className="py-3.5 px-4 text-teal-300">Compression Ratio</th>
                <th className="py-3.5 px-4 text-rose-300">Inference Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono text-xs">
              {sampleRows.map((row) => (
                <tr
                  key={row.condition}
                  className={`hover:bg-slate-800/40 transition-colors ${
                    row.highlight
                      ? 'bg-indigo-950/20 font-semibold text-white'
                      : 'text-slate-300'
                  }`}
                >
                  <td className="py-4 px-4 font-sans font-medium text-slate-200">
                    <div className="flex items-center space-x-2">
                      <span>{row.condition}</span>
                      {row.tag && (
                        <span className="px-2 py-0.5 text-[10px] rounded-md bg-indigo-500/20 text-indigo-300 font-sans border border-indigo-500/30">
                          {row.tag}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-4 px-4 text-indigo-300 font-semibold">{row.precision}</td>
                  <td className="py-4 px-4 text-emerald-300 font-semibold">{row.recall}</td>
                  <td className="py-4 px-4 text-violet-300 font-semibold">{row.f1}</td>
                  <td className="py-4 px-4 text-amber-200 font-semibold">{row.length} words</td>
                  <td className="py-4 px-4 text-teal-300 font-semibold">{row.compression}%</td>
                  <td className="py-4 px-4 text-rose-300 font-semibold">{row.time}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
