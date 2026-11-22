import React from 'react';
import {
  FileText,
  Sparkles,
  Sliders,
  Globe,
  Info,
  ArrowRight,
} from 'lucide-react';
import { Language, SummaryLength, SummarizationMethod, SampleDoc } from '../types';

interface Page1InputProps {
  language: Language;
  setLanguage: (lang: Language) => void;
  sourceText: string;
  setSourceText: (text: string) => void;
  summaryLength: SummaryLength;
  setSummaryLength: (len: SummaryLength) => void;
  method?: SummarizationMethod;
  setMethod?: (method: SummarizationMethod) => void;
  sampleDocs?: SampleDoc[];
  onSelectSample?: (doc: SampleDoc) => void;
  selectedSampleId?: string;
  onGenerate: () => void;
  loading: boolean;
}

export const Page1Input: React.FC<Page1InputProps> = ({
  language,
  setLanguage,
  sourceText,
  setSourceText,
  summaryLength,
  setSummaryLength,
  onGenerate,
  loading,
}) => {
  const wordCount = sourceText.trim() ? sourceText.trim().split(/\s+/).length : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Page Title & Intro */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 text-sm font-semibold mb-1">
              <FileText className="w-4 h-4" />
              <span>PAGE 1 — SUMMARIZATION INPUT</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Interactive Multilingual Summarizer
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Select input language (Hindi, English, or Code-Mixed), set summary length, and generate factuality-verified summaries.
            </p>
          </div>
        </div>
      </div>

      {/* Main Input Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-sm">
        {/* Controls Row: Language, Length, Method */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Input Language */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 tracking-wider uppercase flex items-center space-x-1.5">
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              <span>1. Input Language</span>
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer font-medium"
            >
              <option value="hindi">Hindi</option>
              <option value="english">English</option>
              <option value="hinglish">Code-Mixed</option>
            </select>
          </div>

          {/* 2. Summary Length */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 tracking-wider uppercase flex items-center space-x-1.5">
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>2. Summary Length</span>
            </label>
            <select
              value={summaryLength}
              onChange={(e) => setSummaryLength(e.target.value as SummaryLength)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer"
            >
              <option value="short">Short (1–2 sentences, ~35 words)</option>
              <option value="medium">Medium (2–3 sentences, ~55 words) [Default]</option>
              <option value="detailed">Detailed (3–4 sentences, ~80 words)</option>
            </select>
          </div>

          {/* 3. Summarization Mode */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 tracking-wider uppercase flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>3. Evaluation Mode</span>
            </label>
            <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-300 flex items-center justify-between">
              <span className="font-semibold text-indigo-300">All 3 Conditions (A, B, C)</span>
              <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 font-mono text-[11px] border border-indigo-500/20">
                Simultaneous
              </span>
            </div>
          </div>
        </div>

        {/* Source Document Textarea */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 tracking-wider uppercase flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>Source Document (Enter or Paste Text)</span>
            </label>
            <div className="flex items-center space-x-2">
              {sourceText.trim() && (
                <button
                  type="button"
                  onClick={() => setSourceText('')}
                  className="text-xs text-rose-400 hover:text-rose-300 transition-colors font-medium cursor-pointer"
                >
                  Clear Text
                </button>
              )}
              <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded-md">
                {wordCount} words | {sourceText.length} characters
              </span>
            </div>
          </div>

          <textarea
            rows={10}
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder={
              language === 'hindi'
                ? 'यहाँ अपना मूल हिन्दी पाठ टाइप करें या पेस्ट करें (Type or paste your Hindi text here)...'
                : language === 'hinglish'
                ? 'Type or paste your Code-Mixed text here (e.g., Maine meeting cancel kar di aur call reschedule kiya)...'
                : 'Type or paste your English text here...'
            }
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-sans leading-relaxed"
          />
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Info className="w-4 h-4 text-indigo-400" />
            <span>Generates Condition A (Standard), Condition B (Factuality-Aware), and Condition C (Revision Loop).</span>
          </div>

          <button
            onClick={onGenerate}
            disabled={loading || !sourceText.trim()}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Generating All 3 Summaries...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate All 3 Summaries (A, B & C)</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
