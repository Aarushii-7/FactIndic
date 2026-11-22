import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  Copy,
  Check,
  Download,
  ShieldCheck,
  Clock,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Sliders,
} from 'lucide-react';
import { MultiConditionResult, Language } from '../types';

interface Page2ResultsProps {
  sourceText: string;
  multiResult: MultiConditionResult | null;
  language: Language;
  onSelectConditionForReport: (cond: 'A' | 'B' | 'C') => void;
  onBackToInput: () => void;
}

export const Page2Results: React.FC<Page2ResultsProps> = ({
  sourceText,
  multiResult,
  language,
  onSelectConditionForReport,
  onBackToInput,
}) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [activeCondTab, setActiveCondTab] = useState<'all' | 'A' | 'B' | 'C'>('all');

  if (!multiResult) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <Sparkles className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Summaries Generated Yet</h2>
        <p className="text-slate-400 text-sm mb-6">
          Please enter or select a source document on Page 1 and click "Generate All 3 Summaries".
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

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownload = (key: string, name: string, text: string) => {
    const blob = new Blob(
      [
        `FACTINDIC SUMMARY REPORT: ${name.toUpperCase()}\n`,
        `============================================\n`,
        `Language: ${language.toUpperCase()}\n`,
        `Generated Text:\n${text}\n\n`,
        `Original Document:\n${sourceText}\n`,
      ],
      { type: 'text/plain;charset=utf-8' }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `factindic_${key}_${language}_summary.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const condList = [
    { key: 'A' as const, data: multiResult.condition_A, tag: 'Standard Baseline', color: 'border-slate-800' },
    { key: 'B' as const, data: multiResult.condition_B, tag: 'Factuality-Aware', color: 'border-indigo-500/30 ring-1 ring-indigo-500/10' },
    { key: 'C' as const, data: multiResult.condition_C, tag: 'Verified & Revised', color: 'border-emerald-500/40 ring-1 ring-emerald-500/20 bg-emerald-950/10' },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-sm font-semibold mb-1">
            <Sparkles className="w-4 h-4" />
            <span>PAGE 2 — ALL THREE GENERATED SUMMARIES</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Condition A, B, and C Generated for Your Input
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Compare Standard (A), Factuality-Aware (B), and Verified/Revised (C) outputs side-by-side with instant factuality metrics.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onBackToInput}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Input</span>
          </button>
        </div>
      </div>

      {/* Original Document Reference Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-slate-400" />
            <span className="font-semibold text-white uppercase tracking-wider">Your Input Document</span>
          </div>
          <span className="font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            {language.toUpperCase()} · {multiResult.source_words} words
          </span>
        </div>
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80 text-xs text-slate-300 max-h-32 overflow-y-auto leading-relaxed select-text font-sans">
          {sourceText}
        </div>
      </div>

      {/* 3 Summary Cards Side-by-Side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {condList.map(({ key, data, tag, color }) => {
          const isCondC = key === 'C';
          const isCondB = key === 'B';

          return (
            <div
              key={key}
              className={`bg-slate-900 border rounded-2xl p-6 space-y-5 flex flex-col justify-between shadow-sm transition-all ${color}`}
            >
              <div className="space-y-4">
                {/* Card Title Bar */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <span className="text-xs font-mono font-bold text-indigo-400 mr-2">[{key}]</span>
                    <span className="font-bold text-sm text-white">{data.name}</span>
                  </div>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                      isCondC
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : isCondB
                        ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    }`}
                  >
                    {tag}
                  </span>
                </div>

                {/* Generated Summary Text */}
                <div
                  className={`bg-slate-950 p-4 rounded-xl border text-sm text-slate-100 font-sans leading-relaxed min-h-[170px] select-text whitespace-pre-wrap ${
                    isCondC ? 'border-emerald-500/20' : isCondB ? 'border-indigo-500/20' : 'border-slate-800'
                  }`}
                >
                  {data.summary}
                </div>
              </div>

              {/* Bottom Metrics & Actions */}
              <div className="space-y-4 pt-2">
                {/* Metric Badges */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Words</span>
                    <span className="font-bold text-white font-mono">{data.word_count}w</span>
                  </div>

                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Support</span>
                    <span className="font-bold text-emerald-400 font-mono">{data.support_rate}%</span>
                  </div>

                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block text-[11px]">Contra</span>
                    <span className="font-bold text-rose-400 font-mono">{data.contradiction_rate}%</span>
                  </div>
                </div>

                {/* Button Toolbar */}
                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => handleCopy(key, data.summary)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 flex items-center space-x-1 transition-all cursor-pointer"
                    >
                      {copiedKey === key ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => handleDownload(key, data.name, data.summary)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 flex items-center space-x-1 transition-all cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>.txt</span>
                    </button>
                  </div>

                  <button
                    onClick={() => onSelectConditionForReport(key)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1 transition-all shadow-sm cursor-pointer ${
                      isCondC
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                        : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
                    }`}
                  >
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Audit Claims</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
