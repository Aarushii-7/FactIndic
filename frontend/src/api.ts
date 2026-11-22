import {
  SampleDoc,
  SummaryOutput,
  VerificationResult,
  ComparisonCard,
  EvaluationRow,
  LanguageBreakdownRow,
  Language,
  SummaryLength,
  SummarizationMethod,
  MultiConditionResult,
} from './types';
import {
  DEMO_SAMPLES,
  BENCHMARK_SUMMARY_BY_CONDITION,
  BENCHMARK_LANGUAGE_BREAKDOWN,
} from './mockData';

const API_BASE = '/api';

export async function generateAllSummariesApi(params: {
  source_text: string;
  language: Language;
  summary_length?: SummaryLength;
}): Promise<MultiConditionResult> {
  const res = await fetch(`${API_BASE}/summarize_all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_text: params.source_text,
      language: params.language,
      summary_length: params.summary_length || 'medium',
    }),
  });

  if (!res.ok) {
    let errorDetail = `Backend server error (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  const data: MultiConditionResult = await res.json();
  return data;
}

export async function fetchSamples(): Promise<SampleDoc[]> {
  try {
    const res = await fetch(`${API_BASE}/samples`);
    if (res.ok) {
      const data = await res.json();
      if (data.samples && data.samples.length > 0) return data.samples;
    }
  } catch (err) {
    console.warn('API /samples offline, using demo sample catalogue:', err);
  }
  return DEMO_SAMPLES;
}

export async function generateSummaryApi(params: {
  source_text: string;
  language: Language;
  length: string;
  method: SummarizationMethod;
  sample_id?: string;
}): Promise<SummaryOutput> {
  const res = await fetch(`${API_BASE}/summarize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    let errorDetail = `Summarization failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {}
    throw new Error(errorDetail);
  }

  return await res.json();
}

export async function verifySummaryApi(params: {
  summary_text: string;
  source_text: string;
  language: Language;
  genre?: string;
}): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    let errorDetail = `Verification failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {}
    throw new Error(errorDetail);
  }

  return await res.json();
}

export async function reviseSummaryApi(params: {
  summary_text: string;
  source_text: string;
  language: Language;
}): Promise<{
  original_summary: string;
  revised_summary: string;
  revised_claims: any[];
  initial_support: number;
  final_support: number;
  initial_contradiction: number;
  final_contradiction: number;
  status: string;
}> {
  const res = await fetch(`${API_BASE}/revise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    let errorDetail = `Revision failed (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {}
    throw new Error(errorDetail);
  }

  return await res.json();
}

export async function compareConditionsApi(params: {
  source_text: string;
  language: Language;
  sample_id?: string;
}): Promise<{ cards: ComparisonCard[] }> {
  try {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('API /compare failed:', err);
  }

  throw new Error('Comparison failed on server.');
}

export async function fetchBenchmarkMetrics(): Promise<{
  summary_by_condition: EvaluationRow[];
  language_breakdown: LanguageBreakdownRow[];
  decision_distribution: any;
}> {
  try {
    const res = await fetch(`${API_BASE}/metrics`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('API /metrics offline, using static benchmark results:', err);
  }

  return {
    summary_by_condition: BENCHMARK_SUMMARY_BY_CONDITION,
    language_breakdown: BENCHMARK_LANGUAGE_BREAKDOWN,
    decision_distribution: {
      total_samples: 500,
      accepted_s0: 123,
      accepted_s1: 190,
      total_accepted: 313,
      unresolved_flagged: 187,
    },
  };
}
