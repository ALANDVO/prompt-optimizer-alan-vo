import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { EvaluationResponse } from '../types';

export const EvaluateView: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [domain, setDomain] = useState('general');
  const [currentResult, setCurrentResult] = useState<EvaluationResponse | null>(null);
  const [history, setHistory] = useState<EvaluationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getEvaluations(1, 10).then((r) => setHistory(r.items)).catch(() => {});
  }, []);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || prompt.length < 3) return setError('Prompt must be at least 3 characters.');
    try {
      setIsLoading(true);
      setError(null);
      const res = await api.evaluate({ prompt: prompt.trim(), domain });
      setCurrentResult(res);
      api.getEvaluations(1, 10).then((r) => setHistory(r.items)).catch(() => {});
    } catch (err: any) {
      setError(err.message || 'Evaluation failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportJson = () => {
    if (!currentResult) return;
    const blob = new Blob([JSON.stringify(currentResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation-${currentResult.id || 'report'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getGradeClass = (g: string) => `grade-${g.toLowerCase()}`;

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Multi-Dimensional Prompt Evaluation</h2>
        <p className="workflow-desc">Deterministic scoring across 8 heuristic dimensions (Clarity, Specificity, Structure, Constraints, Output Spec, Role, Examples, Safety).</p>
      </div>

      <div className="grid-layout-2col">
        <div className="card">
          <h3>Prompt Input</h3>
          <form onSubmit={handleEvaluate}>
            <div className="form-group">
              <label htmlFor="eval-prompt">Prompt Text:</label>
              <textarea id="eval-prompt" className="code-textarea" rows={7} placeholder="Enter prompt to evaluate..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="eval-domain">Domain:</label>
                <select id="eval-domain" value={domain} onChange={(e) => setDomain(e.target.value)} className="form-control">
                  <option value="general">General</option>
                  <option value="software_engineering">Software Engineering</option>
                  <option value="cybersecurity">Cybersecurity</option>
                  <option value="ml_engineering">ML Engineering</option>
                  <option value="data_analysis">Data Analysis</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={isLoading || prompt.trim().length < 3}>
                  {isLoading ? 'Scoring...' : 'Score Prompt'}
                </button>
              </div>
            </div>
            {error && <div className="alert-error" role="alert">{error}</div>}
          </form>

          {history.length > 0 && (
            <div className="history-section">
              <h4>Recent Evaluations</h4>
              <ul className="history-list">
                {history.map((h) => (
                  <li key={h.id} className="history-item" onClick={() => { setCurrentResult(h); setPrompt(h.prompt); }}>
                    <span className={`badge-grade ${getGradeClass(h.grade)}`}>{h.grade}</span>
                    <span className="history-preview">{h.prompt.slice(0, 45)}...</span>
                    <span className="history-score">{(h.overall_score * 100).toFixed(0)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header-flex">
            <h3>Evaluation Rubric & Diagnostics</h3>
            {currentResult && <button className="btn-secondary btn-sm" onClick={handleExportJson}>Export JSON</button>}
          </div>

          {!currentResult ? (
            <div className="empty-state"><p>Enter a prompt on the left to view rubric scores.</p></div>
          ) : (
            <div>
              <div className="score-summary-banner">
                <div className="score-box">
                  <div className="score-val">{(currentResult.overall_score * 100).toFixed(0)}%</div>
                  <div className="score-lbl">Overall Score</div>
                </div>
                <div className="grade-box">
                  <div className={`grade-display ${getGradeClass(currentResult.grade)}`}>{currentResult.grade}</div>
                  <div className="score-lbl">Rubric Grade</div>
                </div>
              </div>

              <div className="dimensions-grid">
                {currentResult.dimensions.map((d) => (
                  <div key={d.dimension} className="dimension-row">
                    <div className="dim-meta">
                      <span className="dim-name">{d.dimension}</span>
                      <span className="dim-score">{(d.score * 100).toFixed(0)}% ({d.rating})</span>
                    </div>
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: `${d.score * 100}%`, background: d.score >= 0.7 ? '#22c55e' : d.score >= 0.4 ? '#eab308' : '#ef4444' }} />
                    </div>
                    <div className="dim-notes">{d.notes}</div>
                  </div>
                ))}
              </div>

              {currentResult.weak_areas.length > 0 && (
                <div className="weak-areas-card">
                  <h4>Identified Weaknesses</h4>
                  <ul>{currentResult.weak_areas.map((w, i) => <li key={i}>{w}</li>)}</ul>
                </div>
              )}

              {currentResult.recommendations.length > 0 && (
                <div className="recommendations-card">
                  <h4>Recommendations</h4>
                  <ul>{currentResult.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
