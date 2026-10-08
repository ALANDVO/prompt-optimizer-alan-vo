import React, { useState } from 'react';
import { api } from '../api/client';
import { OptimizationResponse } from '../types';

interface OptimizeViewProps {
  onSavedToLibrary?: () => void;
}

export const OptimizeView: React.FC<OptimizeViewProps> = ({ onSavedToLibrary }) => {
  const [prompt, setPrompt] = useState('');
  const [targetDomain, setTargetDomain] = useState('software_engineering');
  const [strategy, setStrategy] = useState('structured');
  const [useAdvisoryLlm, setUseAdvisoryLlm] = useState(false);
  const [result, setResult] = useState<OptimizationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || prompt.length < 3) return setError('Prompt must be at least 3 characters.');
    try {
      setIsLoading(true);
      setError(null);
      setStatusMsg(null);
      const res = await api.optimize({ prompt: prompt.trim(), target_domain: targetDomain, strategy, use_advisory_llm: useAdvisoryLlm });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Optimization failed.');
    } finally {
      setIsLoading(false);
    }
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
    } catch (err: any) {
      setStatusMsg(`Save error: ${err.message}`);
    }
  };

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Prompt Mutation & Optimization Engine</h2>
        <p className="workflow-desc">Transform raw prompts into structured instructions using deterministic mutation heuristics and optional advisory LLM synthesis.</p>
      </div>

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
      </div>

      {result && (
        <div style={{ marginTop: '1rem' }}>
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
  );
};
