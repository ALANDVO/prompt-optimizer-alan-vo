import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';
import { PromptResponse } from '../types';
import { useAuth } from '../context/AuthContext';

export const LibraryView: React.FC = () => {
  const { role } = useAuth();
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<PromptResponse | null>(null);
  const [formName, setFormName] = useState('');
  const [formPrompt, setFormPrompt] = useState('');
  const [formDomain, setFormDomain] = useState('software_engineering');
  const [formTags, setFormTags] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { loadPrompts(); }, [domainFilter, search]);

  const loadPrompts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await api.listPrompts(1, 50, domainFilter || undefined, search || undefined);
      setPrompts(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load prompts.');
    } finally {
      setIsLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingPrompt(null);
    setFormName('');
    setFormPrompt('');
    setFormDomain('software_engineering');
    setFormTags('');
    setIsModalOpen(true);
  };

  const openEditModal = (p: PromptResponse) => {
    setEditingPrompt(p);
    setFormName(p.name);
    setFormPrompt(p.prompt);
    setFormDomain(p.domain);
    setFormTags(p.tags);
    setIsModalOpen(true);
  };

  const handleSavePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formPrompt.trim() || (!editingPrompt && !formName.trim())) return setError('Name and prompt required.');

    try {
      setIsSubmitting(true);
      setError(null);
      if (editingPrompt) {
        await api.updatePrompt(editingPrompt.id, { prompt: formPrompt.trim(), domain: formDomain, tags: formTags.trim() });
        setSuccessMsg(`Prompt "${editingPrompt.name}" updated.`);
      } else {
        await api.createPrompt({ name: formName.trim(), prompt: formPrompt.trim(), domain: formDomain, tags: formTags.trim() });
        setSuccessMsg(`Prompt "${formName}" created.`);
      }
      setIsModalOpen(false);
      loadPrompts();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Save failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      await api.deletePrompt(id);
      setSuccessMsg(`Prompt "${name}" deleted.`);
      loadPrompts();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Delete failed.');
    }
  };

  const handleExportJSON = () => {
    const data = prompts.map((p) => ({ name: p.name, prompt: p.prompt, domain: p.domain, tags: p.tags, version: p.version }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'prompt_library.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setIsLoading(true);
      const text = await file.text();
      const parsed = JSON.parse(text);
      const items = Array.isArray(parsed) ? parsed : [parsed];
      let count = 0;
      for (const item of items) {
        if (item.name && item.prompt) {
          await api.createPrompt({ name: item.name, prompt: item.prompt, domain: item.domain || 'general', tags: item.tags || '' });
          count++;
        }
      }
      setSuccessMsg(`Imported ${count} templates.`);
      loadPrompts();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(`Import failed: ${err.message}`);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Prompt Template Library</h2>
        <p className="workflow-desc">Catalog, version, and manage standardized prompt assets with SQLite persistence and JSON import/export.</p>
      </div>

      <div className="library-toolbar">
        <div className="toolbar-search">
          <input type="search" placeholder="Search templates..." className="form-control" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="toolbar-filter">
          <select className="form-control" value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)}>
            <option value="">All Domains</option>
            <option value="software_engineering">Software Engineering</option>
            <option value="cybersecurity">Cybersecurity</option>
            <option value="ml_engineering">ML Engineering</option>
            <option value="data_analysis">Data Analysis</option>
            <option value="general">General</option>
          </select>
        </div>
        <div className="toolbar-actions">
          <button className="btn-secondary btn-sm" onClick={handleExportJSON}>Export JSON</button>
          <label className="btn-secondary btn-sm" style={{ cursor: 'pointer', margin: 0 }}>
            Import JSON
            <input type="file" ref={fileInputRef} accept=".json" style={{ display: 'none' }} onChange={handleImportFile} />
          </label>
          <button className="btn-primary btn-sm" onClick={openCreateModal}>+ New Template</button>
        </div>
      </div>

      {successMsg && <div className="alert-success">{successMsg}</div>}
      {error && <div className="alert-error">{error}</div>}

      {isLoading ? (
        <div className="loading-state">Loading library...</div>
      ) : prompts.length === 0 ? (
        <div className="empty-state card"><h3>No Templates Found</h3></div>
      ) : (
        <div className="prompt-cards-grid">
          {prompts.map((p) => (
            <div key={p.id} className="card prompt-card">
              <div className="prompt-card-header">
                <div>
                  <h3 className="prompt-name">{p.name}</h3>
                  <div className="prompt-badges">
                    <span className="badge-domain">{p.domain}</span>
                    <span className="badge-version">v{p.version}</span>
                    {p.tags && p.tags.split(',').map((t) => <span key={t} className="badge-tag">#{t.trim()}</span>)}
                  </div>
                </div>
                <div className="card-actions">
                  <button className="btn-secondary btn-sm" onClick={() => openEditModal(p)}>Edit</button>
                  {role === 'admin' && (
                    <button className="btn-danger-outline btn-sm" onClick={() => handleDelete(p.id, p.name)}>Delete</button>
                  )}
                </div>
              </div>
              <pre className="prompt-content-snippet">{p.prompt}</pre>
            </div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-content card">
            <div className="modal-header">
              <h3>{editingPrompt ? `Edit: ${editingPrompt.name}` : 'Create New Prompt Template'}</h3>
              <button className="btn-close" onClick={() => setIsModalOpen(false)}>×</button>
            </div>
            <form onSubmit={handleSavePrompt}>
              {!editingPrompt && (
                <div className="form-group">
                  <label htmlFor="modal-name">Template Name:</label>
                  <input id="modal-name" required className="form-control" value={formName} onChange={(e) => setFormName(e.target.value)} />
                </div>
              )}
              <div className="form-group">
                <label htmlFor="modal-prompt">Prompt Text:</label>
                <textarea id="modal-prompt" required rows={6} className="code-textarea" value={formPrompt} onChange={(e) => setFormPrompt(e.target.value)} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="modal-domain">Domain:</label>
                  <select id="modal-domain" className="form-control" value={formDomain} onChange={(e) => setFormDomain(e.target.value)}>
                    <option value="software_engineering">Software Engineering</option>
                    <option value="cybersecurity">Cybersecurity</option>
                    <option value="ml_engineering">ML Engineering</option>
                    <option value="data_analysis">Data Analysis</option>
                    <option value="general">General</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="modal-tags">Tags:</label>
                  <input id="modal-tags" className="form-control" value={formTags} onChange={(e) => setFormTags(e.target.value)} />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>{isSubmitting ? 'Saving...' : 'Save'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
