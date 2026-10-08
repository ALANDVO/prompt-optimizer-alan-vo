import React, { useState } from 'react';
import { api } from '../api/client';
import { ABTestResponse, BenchmarkResponse, TestCaseSchema } from '../types';

export const ABTestView: React.FC = () => {
  const [subTab, setSubTab] = useState<'abtest' | 'benchmark'>('abtest');

  const [promptA, setPromptA] = useState('Analyze system log and return JSON with status and summary.');
  const [promptB, setPromptB] = useState('Analyze system log and explain what went wrong in plain text.');
  const [cases, setCases] = useState<TestCaseSchema[]>([
    { input: 'ERROR: Database timeout on 5432', expected: 'status', assertion_type: 'contains' },
    { input: 'WARN: High CPU 92% on worker-3', expected: 'summary', assertion_type: 'contains' },
  ]);
  const [abResult, setAbResult] = useState<ABTestResponse | null>(null);
  const [isAbLoading, setIsAbLoading] = useState(false);
  const [abError, setAbError] = useState<string | null>(null);

  const [benchmarkPrompt, setBenchmarkPrompt] = useState('Outline 3 mitigations against prompt injection vulnerabilities.');
  const [selectedModels, setSelectedModels] = useState(['gpt-4o-mini', 'claude-3-5-sonnet', 'gemini-1.5-pro', 'ollama-llama3']);
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkResponse | null>(null);
  const [isBmLoading, setIsBmLoading] = useState(false);
  const [bmError, setBmError] = useState<string | null>(null);

  const handleUpdateCase = (idx: number, field: keyof TestCaseSchema, val: string) => {
    const updated = [...cases];
    (updated[idx] as any)[field] = val;
    setCases(updated);
  };

  const handleRunABTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptA.trim() || !promptB.trim()) return setAbError('Both prompts are required.');
    const validCases = cases.filter((c) => c.input.trim());
    if (!validCases.length) return setAbError('At least one test case is required.');

    try {
      setIsAbLoading(true);
      setAbError(null);
      const res = await api.runABTest({ prompt_a: promptA, prompt_b: promptB, cases: validCases });
      setAbResult(res);
    } catch (err: any) {
      setAbError(err.message || 'A/B Test failed.');
    } finally {
      setIsAbLoading(false);
    }
  };

  const handleToggleModel = (m: string) => {
    setSelectedModels((prev) => (prev.includes(m) ? (prev.length > 1 ? prev.filter((x) => x !== m) : prev) : [...prev, m]));
  };

  const handleRunBenchmark = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!benchmarkPrompt.trim()) return setBmError('Prompt is required.');
    try {
      setIsBmLoading(true);
      setBmError(null);
      const res = await api.runBenchmark({ prompt: benchmarkPrompt, models: selectedModels });
      setBenchmarkResult(res);
    } catch (err: any) {
      setBmError(err.message || 'Benchmark failed.');
    } finally {
      setIsBmLoading(false);
    }
  };

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>A/B Testing & Multi-Model Benchmarking</h2>
        <p className="workflow-desc">Compare candidate prompt versions with assertion suites or benchmark latency across foundation models.</p>
        <div className="subtab-buttons">
          <button className={`subtab-btn ${subTab === 'abtest' ? 'active' : ''}`} onClick={() => setSubTab('abtest')}>
            A/B Test Suite
          </button>
          <button className={`subtab-btn ${subTab === 'benchmark' ? 'active' : ''}`} onClick={() => setSubTab('benchmark')}>
            Multi-Model Benchmark
          </button>
        </div>
      </div>

      {subTab === 'abtest' && (
        <form onSubmit={handleRunABTest}>
          <div className="grid-layout-2col">
            <div className="card">
              <h3>Prompt Candidate A</h3>
              <textarea className="code-textarea" rows={4} value={promptA} onChange={(e) => setPromptA(e.target.value)} />
            </div>
            <div className="card">
              <h3>Prompt Candidate B</h3>
              <textarea className="code-textarea" rows={4} value={promptB} onChange={(e) => setPromptB(e.target.value)} />
            </div>
          </div>

          <div className="card" style={{ marginTop: '1rem' }}>
            <div className="card-header-flex">
              <h3>Assertion Cases ({cases.length})</h3>
              <button type="button" className="btn-secondary btn-sm" onClick={() => setCases([...cases, { input: '', expected: '', assertion_type: 'contains' }])}>
                + Add Case
              </button>
            </div>
            <table className="data-table">
              <thead>
                <tr><th>Input Scenario</th><th>Expected Match</th><th>Type</th><th>Action</th></tr>
              </thead>
              <tbody>
                {cases.map((c, idx) => (
                  <tr key={idx}>
                    <td><input className="form-control" value={c.input} onChange={(e) => handleUpdateCase(idx, 'input', e.target.value)} /></td>
                    <td><input className="form-control" value={c.expected || ''} onChange={(e) => handleUpdateCase(idx, 'expected', e.target.value)} /></td>
                    <td>
                      <select className="form-control" value={c.assertion_type} onChange={(e) => handleUpdateCase(idx, 'assertion_type', e.target.value)}>
                        <option value="contains">Contains</option>
                        <option value="exact">Exact</option>
                        <option value="regex">Regex</option>
                        <option value="json_validity">Valid JSON</option>
                      </select>
                    </td>
                    <td>
                      <button type="button" className="btn-danger-outline btn-sm" onClick={() => setCases(cases.filter((_, i) => i !== idx))} disabled={cases.length <= 1}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="form-actions" style={{ marginTop: '1rem' }}>
              <button type="submit" className="btn-primary" disabled={isAbLoading}>
                {isAbLoading ? 'Running...' : 'Execute A/B Test'}
              </button>
            </div>
            {abError && <div className="alert-error">{abError}</div>}
          </div>

          {abResult && (
            <div className="card" style={{ marginTop: '1rem' }}>
              <div className="score-summary-banner">
                <div className="score-box"><div className="score-val">{abResult.wins_a}</div><div className="score-lbl">A Wins</div></div>
                <div className="score-box"><div className="score-val">{abResult.wins_b}</div><div className="score-lbl">B Wins</div></div>
                <div className="score-box"><div className="score-val">{abResult.ties}</div><div className="score-lbl">Ties</div></div>
                <div className="score-box"><div className="score-val" style={{ color: '#38bdf8' }}>Winner: {abResult.winner}</div><div className="score-lbl">Confidence: {(abResult.confidence * 100).toFixed(0)}%</div></div>
              </div>
              <table className="data-table">
                <thead><tr><th>#</th><th>Preview</th><th>Winner</th><th>Reason</th><th>A</th><th>B</th></tr></thead>
                <tbody>
                  {abResult.details.map((d) => (
                    <tr key={d.case_index}>
                      <td>#{d.case_index}</td>
                      <td><code>{d.input_preview}</code></td>
                      <td><span className={`badge-winner ${d.winner === 'A' ? 'winner-a' : d.winner === 'B' ? 'winner-b' : 'winner-tie'}`}>{d.winner}</span></td>
                      <td>{d.reason}</td>
                      <td>{d.prompt_a_passed ? '✅' : '❌'}</td>
                      <td>{d.prompt_b_passed ? '✅' : '❌'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </form>
      )}

      {subTab === 'benchmark' && (
        <form onSubmit={handleRunBenchmark} className="card">
          <div className="form-group">
            <label>Benchmark Prompt:</label>
            <textarea className="code-textarea" rows={3} value={benchmarkPrompt} onChange={(e) => setBenchmarkPrompt(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Target Models:</label>
            <div className="checkbox-row">
              {['gpt-4o-mini', 'claude-3-5-sonnet', 'gemini-1.5-pro', 'ollama-llama3'].map((m) => (
                <label key={m} className="checkbox-pill">
                  <input type="checkbox" checked={selectedModels.includes(m)} onChange={() => handleToggleModel(m)} />
                  <span>{m}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={isBmLoading}>{isBmLoading ? 'Benchmarking...' : 'Run Benchmark'}</button>
          </div>
          {bmError && <div className="alert-error">{bmError}</div>}

          {benchmarkResult && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className="card-header-flex">
                <h3>Results</h3>
                <span className="best-model-badge">Best Model: {benchmarkResult.best_model}</span>
              </div>
              <table className="data-table">
                <thead><tr><th>Model</th><th>Latency</th><th>Tokens</th><th>Clarity</th><th>Compliance</th><th>Quality</th></tr></thead>
                <tbody>
                  {benchmarkResult.results.map((r) => (
                    <tr key={r.model} className={r.model === benchmarkResult.best_model ? 'row-highlight' : ''}>
                      <td><strong>{r.model}</strong></td>
                      <td>{r.latency_seconds.toFixed(2)}s</td>
                      <td>{r.estimated_tokens}</td>
                      <td>{(r.clarity_index * 100).toFixed(0)}%</td>
                      <td>{(r.compliance_score * 100).toFixed(0)}%</td>
                      <td>{(r.overall_quality * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </form>
      )}
    </div>
  );
};
