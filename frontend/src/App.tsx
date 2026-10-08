import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { EvaluateView } from './components/EvaluateView';
import { OptimizeView } from './components/OptimizeView';
import { ABTestView } from './components/ABTestView';
import { LibraryView } from './components/LibraryView';
import { AuditView } from './components/AuditView';
import { api } from './api/client';

const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('evaluate');
  const [appVersion, setAppVersion] = useState<string>('1.0.0');
  const { error, clearError } = useAuth();

  useEffect(() => {
    async function fetchVersion() {
      try {
        const v = await api.getVersion();
        setAppVersion(v.version);
      } catch {
        // default fallback
      }
    }
    fetchVersion();
  }, []);

  return (
    <div className="app-shell">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} appVersion={appVersion} />

      {error && (
        <div className="global-banner-error">
          <div className="banner-content">
            <span>{error}</span>
            <button className="btn-close-sm" onClick={clearError}>×</button>
          </div>
        </div>
      )}

      <main className="main-content">
        {activeTab === 'evaluate' && <EvaluateView />}
        {activeTab === 'optimize' && <OptimizeView onSavedToLibrary={() => setActiveTab('library')} />}
        {activeTab === 'abtest' && <ABTestView />}
        {activeTab === 'library' && <LibraryView />}
        {activeTab === 'audit' && <AuditView />}
      </main>

      <footer className="app-footer">
        <div className="footer-container">
          <div className="footer-left">
            <strong>Prompt Optimizer</strong> — High-Performance Prompt Evaluation & Mutation Engine
          </div>
          <div className="footer-right">
            Built by <a href="https://github.com/ALANDVO" target="_blank" rel="noreferrer">Alan Vo</a> (alanvo@gmail.com)
            &nbsp;•&nbsp; MIT License
          </div>
        </div>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
