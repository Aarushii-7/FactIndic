import React, { useState } from 'react';
import {
  CheckCircle2,
  HelpCircle,
  AlertTriangle,
  RotateCw,
  Sparkles,
  ArrowRight,
  FileCheck,
  Search,
  Check,
} from 'lucide-react';
import { MultiConditionResult, Language } from '../types';

interface Page3FactualityProps {
  sourceText: string;
  multiResult: MultiConditionResult | null;
  language: Language;
  activeCondition: 'A' | 'B' | 'C';
  setActiveCondition: (c: 'A' | 'B' | 'C') => void;
  onRevise: () => Promise<void>;
  loadingRevise: boolean;
  onBackToResults: () => void;
}

export const Page3Factuality: React.FC<Page3FactualityProps> = ({
  multiResult,
  activeCondition,
  setActiveCondition,
  onRevise,
  loadingRevise,
  onBackToResults,
}) => {
  const [filter, setFilter] = useState<'all' | 'entailment' | 'neutral' | 'contradiction'>('all');

  if (!multiResult) {
    return (
      <div className="max-w-4xl mx-auto text-center py-20 bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <CheckCircle2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Verification Data Available</h2>
        <p className="text-slate-400 text-sm mb-6">
          Please enter a document on Page 1 and click "Generate All 3 Summaries".
        </p>
        <button
          onClick={onBackToResults}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition-all inline-flex items-center space-x-2 cursor-pointer"
        >
          <span>Return to Page 1</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  const activeData =
    activeCondition === 'A'
      ? multiResult.condition_A
      : activeCondition === 'B'
      ? multiResult.condition_B
      : multiResult.condition_C;

  const filteredClaims = activeData.claims.filter((c) => {
    if (filter === 'all') return true;
    return c.label === filter;
  });

  const getLabelPill = (label: string) => {
    switch (label) {
      case 'entailment':
        return {
          icon: CheckCircle2,
          text: 'Entailment',
          bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          desc: 'The source directly confirms the reported event, entities, and actions.',
        };
      case 'contradiction':
        return {
          icon: AlertTriangle,
          text: 'Contradiction',
          bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          desc: 'The claim directly conflicts with the retrieved source evidence.',
        };
      default:
        return {
          icon: HelpCircle,
          text: 'Neutral (Unverified)',
          bg: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
          desc: 'The claim could not be sufficiently verified from retrieved evidence.',
        };
    }
  };

  const getStatusBadge = () => {
    if (activeData.accepted) {
      return {
        label: 'Policy Accepted (Support ≥90%, Contra ≤5%)',
        color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      };
    }
    if (activeData.contradiction_rate > 5) {
      return {
        label: 'Contradiction Flagged (Contra >5%)',
        color: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      };
    }
    return {
      label: 'Low-Contradiction, Support-Unverified',
      color: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    };
  };

  const statusBadge = getStatusBadge();

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-sm font-semibold mb-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>PAGE 3 — FACTUALITY REPORT & CLAIM-LEVEL AUDIT</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Claim-Level NLI Verification & Revision Audit
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Auditing atomic propositions against top-5 retrieved source sentences using mDeBERTa-v3.
          </p>
        </div>

        {/* Condition Selector Tabs */}
        <div className="flex items-center space-x-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          {(['A', 'B', 'C'] as const).map((c) => (
            <button
              key={c}
              onClick={() => setActiveCondition(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeCondition === c
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              Condition {c} {c === 'C' ? '★' : ''}
            </button>
          ))}
        </div>
      </div>

      {/* Active Condition Summary Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-800">
          <span className="font-semibold text-white uppercase tracking-wider">
            Auditing: {activeData.name}
          </span>
          <span className="font-mono text-slate-400">
            {activeData.word_count} words · {activeData.claims.length} atomic claims
          </span>
        </div>
        <p className="text-sm text-slate-200 leading-relaxed font-sans select-text">
          {activeData.summary}
        </p>
      </div>

      {/* Scorecard Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Factual Support Rate</span>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            {activeData.support_rate}%
          </div>
          <span className="text-xs text-slate-500">Threshold: ≥ 90%</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Contradiction Rate</span>
          <div className="text-2xl font-bold text-rose-400 font-mono">
            {activeData.contradiction_rate}%
          </div>
          <span className="text-xs text-slate-500">Threshold: ≤ 5%</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-xs text-slate-400 font-medium">Neutral / Unverified</span>
          <div className="text-2xl font-bold text-amber-300 font-mono">
            {activeData.neutral_rate}%
          </div>
          <span className="text-xs text-slate-500">Ungrounded claims</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">Policy Acceptance</span>
          <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold border ${statusBadge.color} inline-block truncate`}>
            {statusBadge.label}
          </span>
          <span className="text-xs text-slate-500 font-mono">{activeData.claims.length} claims audited</span>
        </div>
      </div>

      {/* Revision Box for Condition C */}
      {activeCondition === 'C' && multiResult.condition_C.revised_from_B && (
        <div className="bg-slate-900 border border-emerald-500/30 rounded-2xl p-6 space-y-4 shadow-lg shadow-emerald-950/20">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-white text-base">Targeted Revision Loop: Before vs. After (S0 → S1)</h3>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Resolved in 1 Revision Step
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Before */}
            <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>BEFORE REVISION (Condition B / S0)</span>
                <span className="text-rose-400 font-mono">
                  Contra: {multiResult.condition_B.contradiction_rate}% | Sup: {multiResult.condition_B.support_rate}%
                </span>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed font-sans">{multiResult.condition_B.summary}</p>
            </div>

            {/* After */}
            <div className="bg-slate-950/80 p-4 rounded-xl border border-emerald-500/30 space-y-2 ring-1 ring-emerald-500/20">
              <div className="flex items-center justify-between text-xs text-emerald-400 font-semibold">
                <span className="flex items-center space-x-1">
                  <Check className="w-3.5 h-3.5" />
                  <span>AFTER REVISION (Condition C / S1)</span>
                </span>
                <span className="text-emerald-400 font-mono">
                  Contra: {multiResult.condition_C.contradiction_rate}% | Sup: {multiResult.condition_C.support_rate}%
                </span>
              </div>
              <p className="text-sm text-white leading-relaxed font-sans">{multiResult.condition_C.summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs & Claims Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
        <div className="flex items-center space-x-2 text-sm font-semibold text-slate-200">
          <FileCheck className="w-4 h-4 text-indigo-400" />
          <span>Atomic Claims in Condition {activeCondition} ({filteredClaims.length} displayed)</span>
        </div>

        <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
          {(['all', 'entailment', 'neutral', 'contradiction'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all cursor-pointer ${
                filter === t ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-4">
        {filteredClaims.map((claim) => {
          const pill = getLabelPill(claim.label);
          const Icon = pill.icon;

          return (
            <div
              key={claim.claim_id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all rounded-2xl p-6 space-y-4 shadow-sm"
            >
              {/* Claim Header */}
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
                      {claim.claim_id}
                    </span>
                    <span className="text-xs text-slate-500">Atomic Proposition</span>
                  </div>
                  <h3 className="text-base font-medium text-white leading-snug">
                    {claim.claim_text}
                  </h3>
                </div>

                <div className={`px-3 py-1.5 rounded-xl border ${pill.bg} flex items-center space-x-1.5 flex-shrink-0 text-xs font-semibold`}>
                  <Icon className="w-4 h-4" />
                  <span>{pill.text}</span>
                </div>
              </div>

              {/* Confidence Mini-Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono text-slate-400">
                  <span>mDeBERTa Confidence</span>
                  <span>
                    Ent: {Math.round(claim.probabilities.entailment * 100)}% | Neu: {Math.round(claim.probabilities.neutral * 100)}% | Con: {Math.round(claim.probabilities.contradiction * 100)}%
                  </span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
                  <div style={{ width: `${claim.probabilities.entailment * 100}%` }} className="bg-emerald-500 h-full" />
                  <div style={{ width: `${claim.probabilities.neutral * 100}%` }} className="bg-amber-400 h-full" />
                  <div style={{ width: `${claim.probabilities.contradiction * 100}%` }} className="bg-rose-500 h-full" />
                </div>
              </div>

              {/* Retrieved Source Evidence */}
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 space-y-1.5 text-xs">
                <div className="flex items-center space-x-1.5 text-indigo-300 font-medium">
                  <Search className="w-3.5 h-3.5" />
                  <span>Retrieved Source Evidence Sentence:</span>
                </div>
                <p className="text-slate-300 italic leading-relaxed font-sans">
                  "{claim.primary_evidence || claim.retrieved_evidence}"
                </p>
                <p className="text-slate-500 text-xs pt-1">
                  Analysis: {claim.explanation}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
