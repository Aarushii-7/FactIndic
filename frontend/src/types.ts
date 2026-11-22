export type Language = 'hindi' | 'hinglish' | 'english';
export type SummaryLength = 'short' | 'medium' | 'detailed';
export type SummarizationMethod = 'standard' | 'factuality' | 'verified';

export interface SampleDoc {
  sample_id: string;
  language: Language;
  genre: string;
  heading?: string;
  source_text: string;
  reference_summary?: string;
}

export interface ClaimVerification {
  claim_id: string;
  claim_text: string;
  label: 'entailment' | 'neutral' | 'contradiction';
  probabilities: {
    entailment: number;
    neutral: number;
    contradiction: number;
  };
  retrieved_evidence: string;
  primary_evidence?: string;
  explanation: string;
}

export interface VerificationResult {
  claims: ClaimVerification[];
  total_claims: number;
  support_rate: number;
  contradiction_rate: number;
  neutral_rate: number;
  accepted: boolean;
  status: 'ACCEPTED' | 'REVISE_FLAGGED' | 'UNRESOLVED_FLAGGED';
  reasons: string[];
}

export interface ConditionResult {
  name: string;
  summary: string;
  word_count: number;
  compression_ratio: number;
  inference_time_sec: number;
  support_rate: number;
  contradiction_rate: number;
  neutral_rate: number;
  accepted: boolean;
  status: string;
  claims: ClaimVerification[];
  revised_from_B?: boolean;
  revised_count?: number;
}

export interface MultiConditionResult {
  source_text: string;
  language: Language;
  source_words: number;
  condition_A: ConditionResult;
  condition_B: ConditionResult;
  condition_C: ConditionResult;
}

export interface SummaryOutput {
  summary: string;
  word_count: number;
  source_words: number;
  compression_ratio: number;
  inference_time_sec: number;
  language: Language;
  method: SummarizationMethod;
  cached?: boolean;
}

export interface ComparisonCard {
  condition: string;
  summary: string;
  words: number;
  claims: number;
  support_rate: number;
  contra_rate: number;
  inference_sec: number;
}

export interface EvaluationRow {
  Condition: string;
  Precision: number;
  Recall: number;
  'F1-Score': number;
  'Average Summary Length': number;
  'Compression Ratio (%)': number;
  'Inference Time (s)': number;
  'Factual Support (%)': number;
  'Contradiction (%)': number;
  'Strict Acceptance Rate (%)': number;
  'Low-Contradiction, Support-Unverified Rate (%)': number;
}

export interface LanguageBreakdownRow {
  Language: string;
  Samples: number;
  Precision: number;
  Recall: number;
  'F1-Score': number;
  'Average Summary Length': number;
  'Compression Ratio (%)': number;
  'Inference Time (s)': number;
  'Support Rate (%)': number;
  'Contradiction Rate (%)': number;
  'Strict Acceptance (%)': number;
  'Low-Contradiction, Support-Unverified (%)': number;
}
