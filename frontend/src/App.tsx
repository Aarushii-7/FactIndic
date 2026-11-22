import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Page1Input } from './pages/Page1Input';
import { Page2Results } from './pages/Page2Results';
import { Page3Factuality } from './pages/Page3Factuality';
import { Page4Compare } from './pages/Page4Compare';
import { Page5Dashboard } from './pages/Page5Dashboard';
import { AlertTriangle, X } from 'lucide-react';
import {
  Language,
  SummaryLength,
  SummarizationMethod,
  SampleDoc,
  MultiConditionResult,
} from './types';
import {
  fetchSamples,
  generateAllSummariesApi,
  reviseSummaryApi,
} from './api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<number>(1);

  // Input State
  const [language, setLanguage] = useState<Language>('hindi');
  const [sourceText, setSourceText] = useState<string>('');
  const [summaryLength, setSummaryLength] = useState<SummaryLength>('medium');
  const [method, setMethod] = useState<SummarizationMethod>('verified');
  const [sampleDocs, setSampleDocs] = useState<SampleDoc[]>([]);
  const [selectedSampleId, setSelectedSampleId] = useState<string>('');

  // 3-Condition Result State
  const [multiResult, setMultiResult] = useState<MultiConditionResult | null>(null);
  const [activeCondition, setActiveCondition] = useState<'A' | 'B' | 'C'>('C');

  // Loading & Error States
  const [loadingGenerate, setLoadingGenerate] = useState<boolean>(false);
  const [loadingRevise, setLoadingRevise] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load demo samples on startup (options only - do not prefill sourceText!)
  useEffect(() => {
    fetchSamples().then((docs) => {
      setSampleDocs(docs);
    });
  }, []);

  const handleSourceTextChange = (text: string) => {
    setSourceText(text);
    setSelectedSampleId('');
    setMultiResult(null);
    setErrorMessage(null);
  };

  const handleSelectSample = (doc: SampleDoc) => {
    setSelectedSampleId(doc.sample_id);
    setLanguage(doc.language);
    setSourceText(doc.source_text);
    setMultiResult(null);
    setErrorMessage(null);
  };

  const handleGenerateAll = async () => {
    if (!sourceText.trim()) return;
    setLoadingGenerate(true);
    setErrorMessage(null);
    setMultiResult(null);

    try {
      const result = await generateAllSummariesApi({
        source_text: sourceText,
        language,
        summary_length: summaryLength,
      });
      setMultiResult(result);
      setActiveCondition('C');
      // Auto-navigate to Page 2
      setActiveTab(2);
    } catch (err: any) {
      console.error('Generation error:', err);
      setErrorMessage(err.message || 'Failed to generate summaries from backend.');
    } finally {
      setLoadingGenerate(false);
    }
  };

  const handleSelectConditionForReport = (cond: 'A' | 'B' | 'C') => {
    setActiveCondition(cond);
    setActiveTab(3);
  };

  const handleRevise = async () => {
    if (!multiResult || !sourceText.trim()) return;
    setLoadingRevise(true);
    setErrorMessage(null);

    try {
      const revResult = await reviseSummaryApi({
        summary_text: multiResult.condition_B.summary,
        source_text: sourceText,
        language,
      });

      // Update Condition C
      setMultiResult({
        ...multiResult,
        condition_C: {
          ...multiResult.condition_C,
          summary: revResult.revised_summary,
          word_count: revResult.revised_summary.split(/\s+/).length,
          support_rate: revResult.final_support,
          contradiction_rate: revResult.final_contradiction,
          status: revResult.status,
          accepted: revResult.final_support >= 90 && revResult.final_contradiction <= 5,
          claims: revResult.revised_claims,
          revised_from_B: true,
          revised_count: 1,
        },
      });
      setActiveCondition('C');
    } catch (err: any) {
      console.error('Revision error:', err);
      setErrorMessage(err.message || 'Revision failed on backend.');
    } finally {
      setLoadingRevise(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasSummary={multiResult !== null}
        hasVerification={multiResult !== null}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
              <div>
                <span className="font-semibold text-rose-200 block text-sm">Pipeline Error</span>
                <span className="text-xs text-rose-300">{errorMessage}</span>
              </div>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="p-1.5 rounded-lg hover:bg-rose-500/20 text-rose-400 hover:text-rose-200 transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {activeTab === 1 && (
          <Page1Input
            language={language}
            setLanguage={setLanguage}
            sourceText={sourceText}
            setSourceText={handleSourceTextChange}
            summaryLength={summaryLength}
            setSummaryLength={setSummaryLength}
            method={method}
            setMethod={setMethod}
            sampleDocs={sampleDocs}
            onSelectSample={handleSelectSample}
            selectedSampleId={selectedSampleId}
            onGenerate={handleGenerateAll}
            loading={loadingGenerate}
          />
        )}

        {activeTab === 2 && (
          <Page2Results
            sourceText={sourceText}
            multiResult={multiResult}
            language={language}
            onSelectConditionForReport={handleSelectConditionForReport}
            onBackToInput={() => setActiveTab(1)}
          />
        )}

        {activeTab === 3 && (
          <Page3Factuality
            sourceText={sourceText}
            multiResult={multiResult}
            language={language}
            activeCondition={activeCondition}
            setActiveCondition={setActiveCondition}
            onRevise={handleRevise}
            loadingRevise={loadingRevise}
            onBackToResults={() => setActiveTab(2)}
          />
        )}

        {activeTab === 4 && (
          <Page4Compare
            sourceText={sourceText}
            language={language}
            multiResult={multiResult}
            onBackToInput={() => setActiveTab(1)}
          />
        )}

        {activeTab === 5 && (
          <Page5Dashboard
            multiResult={multiResult}
            sourceText={sourceText}
            onBackToInput={() => setActiveTab(1)}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>FactIndic v2.0 · CSET 346 NLP Project · Bennett University</span>
          <span>Models: Qwen2.5-1.5B · MiniLM-L12-v2 · mDeBERTa-v3 · 3-Condition Generator</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
