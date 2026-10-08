import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { AuditLogResponse } from '../types';
import { useAuth } from '../context/AuthContext';

export const AuditView: React.FC = () => {
  const { role } = useAuth();
  const [logs, setLogs] = useState<AuditLogResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (role === 'admin') loadLogs();
  }, [page, role]);

  const loadLogs = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await api.getAuditLogs(page, pageSize);
      setLogs(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs.');
    } finally {
      setIsLoading(false);
    }
  };

  if (role !== 'admin') {
    return (
      <div className="workflow-container">
        <div className="card alert-error">
          <h3>Access Denied</h3>
          <p>The audit log requires the <strong>admin</strong> role. Select admin from the role menu above.</p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Operational Audit Log</h2>
        <p className="workflow-desc">Tamper-evident audit trail recording mutations and security events with automated credential redaction.</p>
      </div>

      <div className="card">
        <div className="card-header-flex">
          <h3>System Audit Events ({total})</h3>
          <button className="btn-secondary btn-sm" onClick={loadLogs} disabled={isLoading}>Refresh</button>
        </div>
        {error && <div className="alert-error">{error}</div>}
        {isLoading ? <div className="loading-state">Loading...</div> : logs.length === 0 ? <p>No logs recorded.</p> : (
          <div>
            <table className="data-table">
              <thead><tr><th>Time (UTC)</th><th>User</th><th>Action</th><th>Resource</th><th>ID</th><th>Details</th></tr></thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.id}>
                    <td>{l.created_at.slice(0, 19).replace('T', ' ')}</td>
                    <td><strong>{l.username}</strong></td>
                    <td><span className="badge-action">{l.action}</span></td>
                    <td>{l.resource}</td>
                    <td><code>{l.resource_id}</code></td>
                    <td><pre style={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>{l.details}</pre></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
              <button className="btn-secondary btn-sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>Previous</button>
              <span style={{ fontSize: '0.85rem' }}>Page {page} of {totalPages}</span>
              <button className="btn-secondary btn-sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
