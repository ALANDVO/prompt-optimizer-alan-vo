import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { OptimizationResponse, PaginatedResponse } from '../types';

interface OptimizeViewProps {
  onSavedToLibrary?: () => void;
}

export const OptimizeView: React.FC<OptimizeViewProps> = ({ onSavedToLibrary }) => {
  const [prompt, setPrompt] = useState('');
  const [targetDomain, setTargetDomain] = useState('software_engineering');
  const [strategy, setStrategy] = useState('structured');
  const [useAdvisoryLlm, setUseAdvisoryLlm] = useState(false);
  const [result, setResult] = useState<OptimizationResponse | null>(null);
  const [history, setHistory] = useState<OptimizationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    api.getOptimizations(1, 10).then((r) => setHistory(r.items)).catch(() => {});
  }, []);

  const handleOptimize = async (e: React.FormEvent, overridePrompt?: string, overrideStrategy?: string, overrideDomain?: string, overrideUseLlm?: boolean) => {
    e.preventDefault();
    const effectivePrompt = (overridePrompt ?? prompt).trim();
    const effectiveStrategy = overrideStrategy ?? strategy;
    const effectiveDomain = overrideDomain ?? targetDomain;
    const effectiveUseLlm = overrideUseLlm ?? useAdvisoryLlm;
    if (!effectivePrompt || effectivePrompt.length < 3) return setError('Prompt must be at least 3 characters.');
    try {
      setIsLoading(true);
      setError(null);
      setStatusMsg(null);
      const res = await api.optimize({ prompt: effectivePrompt, target_domain: effectiveDomain, strategy: effectiveStrategy, use_advisory_llm: effectiveUseLlm });
      setResult(res);
      if (!overridePrompt) setPrompt(effectivePrompt);
      if (!overrideStrategy) setStrategy(effectiveStrategy);
      if (!overrideDomain) setTargetDomain(effectiveDomain);
      if (overrideUseLlm !== undefined) setUseAdvisoryLlm(effectiveUseLlm);
      api.getOptimizations(1, 10).then((r) => setHistory(r.items)).catch(() => {});
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Optimization failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRerun = async (item: OptimizationResponse) => {
    if (isLoading) return;
    await handleOptimize({ preventDefault: () => {} } as React.FormEvent, item.original_prompt, item.strategy, item.target_domain, item.llm_used);
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.optimized_prompt);
    setStatusMsg('Copied to clipboard!');
    setTimeout(() => setStatusMsg(null), 2500);
  };

  const handleSaveToLibrary = async () => {
    if (!result) return;
    try {
      await api.createPrompt({
        name: `Optimized: ${targetDomain} (${strategy})`,
        prompt: result.optimized_prompt,
        domain: targetDomain,
        tags: `optimized,${strategy}`,
      });
      setStatusMsg('Saved to template library!');
      if (onSavedToLibrary) onSavedToLibrary();
      setTimeout(() => setStatusMsg(null), 3000);
    } catch (err: unknown) {
      setStatusMsg(`Save error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const getStrategyLabel = (s: string) => {
    const labels: Record<string, string> = {
      structured: 'Structured Refactor',
      negative_constraints: 'Negative Constraints',
      xml_tagged: 'XML Semantic Enclosures',
      cot_guided: 'Chain-of-Thought Protocol',
      few_shot: 'Few-Shot Demonstrations',
    };
    return labels[s] || s;
  };

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Prompt Mutation & Optimization Engine</h2>
        <p className="workflow-desc">Transform raw prompts into structured instructions using deterministic mutation heuristics and optional advisory LLM synthesis.</p>
      </div>

      <div className="grid-layout-2col">
        <div className="card">
          <form onSubmit={handleOptimize}>
            <div className="form-group">
              <label htmlFor="opt-prompt">Original Prompt:</label>
              <textarea id="opt-prompt" className="code-textarea" rows={5} placeholder="Enter prompt to optimize..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            </div>

            <div className="form-row-3">
              <div className="form-group">
                <label htmlFor="opt-strategy">Strategy:</label>
                <select id="opt-strategy" className="form-control" value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                  <option value="structured">Structured Refactor</option>
                  <option value="negative_constraints">Negative Constraints</option>
                  <option value="xml_tagged">XML Semantic Enclosures</option>
                  <option value="cot_guided">Chain-of-Thought Protocol</option>
                  <option value="few_shot">Few-Shot Demonstrations</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="opt-domain">Target Domain:</label>
                <select id="opt-domain" className="form-control" value={targetDomain} onChange={(e) => setTargetDomain(e.target.value)}>
                  <option value="software_engineering">Software Engineering</option>
                  <option value="cybersecurity">Cybersecurity</option>
                  <option value="ml_engineering">ML Engineering</option>
                  <option value="data_analysis">Data Analysis</option>
                  <option value="general">General</option>
                </select>
              </div>

              <div className="form-group form-checkbox-group">
                <label className="checkbox-label">
                  <input type="checkbox" checked={useAdvisoryLlm} onChange={(e) => setUseAdvisoryLlm(e.target.checked)} />
                  <span>Advisory LLM (Opt-in)</span>
                </label>
                <span className="help-text">LLM explanations are opt-in and advisory.</span>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={isLoading || prompt.trim().length < 3}>
                {isLoading ? 'Optimizing...' : 'Run Optimization'}
              </button>
            </div>
            {error && <div className="alert-error">{error}</div>}
          </form>

          {history.length > 0 && (
            <div className="history-section">
              <h4>Recent Optimizations</h4>
              <ul className="history-list">
                {history.map((h) => (
                  <li key={h.id} className="history-item" onClick={() => { setResult(h); setPrompt(h.original_prompt); setStrategy(h.strategy); setTargetDomain(h.target_domain); setUseAdvisoryLlm(h.llm_used); }}>
                    <span className="history-strategy">{getStrategyLabel(h.strategy)}</span>
                    <span className="history-domain">{h.target_domain}</span>
                    <span className="history-score">{(h.score_before * 100).toFixed(0)}% → {(h.score_after * 100).toFixed(0)}% (+{(h.improvement_delta * 100).toFixed(0)}%)</span>
                    <button
                      className="btn-rerun"
                      onClick={(e) => { e.stopPropagation(); handleRerun(h); }}
                      disabled={isLoading}
                      title="Rerun optimization"
                    >
                      ↻
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header-flex">
            <h3>Optimization Result</h3>
            {result && <button className="btn-secondary btn-sm" onClick={handleCopy}>Copy Optimized</button>}
          </div>

          {!result ? (
            <div className="empty-state"><p>Run an optimization to see results.</p></div>
          ) : (
            <div>
              <div className="score-summary-banner">
                <div className="score-box"><div className="score-val">{(result.score_before * 100).toFixed(0)}%</div><div className="score-lbl">Score Before</div></div>
                <div className="score-box"><div className="score-val" style={{ color: '#22c55e' }}>{(result.score_after * 100).toFixed(0)}%</div><div className="score-lbl">Score After</div></div>
                <div className="score-box"><div className="score-val" style={{ color: '#38bdf8' }}>+{((result.improvement_delta) * 100).toFixed(0)}%</div><div className="score-lbl">Gain</div></div>
                <div className="score-box"><div className="score-val">{result.llm_used ? 'LLM' : 'Offline'}</div><div className="score-lbl">Engine</div></div>
              </div>

              <div className="grid-layout-2col">
                <div className="card">
                  <h3>Original</h3>
                  <pre className="code-display">{result.original_prompt}</pre>
                </div>
                <div className="card">
                  <div className="card-header-flex">
                    <h3>Optimized</h3>
                    <div className="btn-group">
                      <button className="btn-secondary btn-sm" onClick={handleCopy}>Copy</button>
                      <button className="btn-primary btn-sm" onClick={handleSaveToLibrary}>Save</button>
                    </div>
                  </div>
                  {statusMsg && <div className="alert-info">{statusMsg}</div>}
                  <pre className="code-display code-highlight">{result.optimized_prompt}</pre>
                </div>
              </div>

              <div className="card" style={{ marginTop: '1rem' }}>
                <h3>Mutation Summary</h3>
                <p className="diff-summary-text">{result.diff_summary}</p>
                {result.advisory_notes && <div className="advisory-box"><strong>Note:</strong> {result.advisory_notes}</div>}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
