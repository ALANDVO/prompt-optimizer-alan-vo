import React from 'react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (t: string) => void;
  appVersion: string;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, appVersion }) => {
  const { user, role, demoMode, loginDemo, logout, initiateOIDCLogin } = useAuth();

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="brand" onClick={() => setActiveTab('evaluate')}>
          <span className="brand-icon">⚡</span>
          <div>
            <div className="brand-title">Prompt Optimizer</div>
            <div className="brand-subtitle">Alan Vo | AI & ML Engineering v{appVersion}</div>
          </div>
        </div>

        <nav className="nav-tabs" aria-label="Workflows">
          {['evaluate', 'optimize', 'abtest', 'library'].map((tab) => (
            <button key={tab} className={`nav-tab ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>
              {tab === 'abtest' ? 'A/B & Benchmark' : tab === 'library' ? 'Prompt Library' : tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
          {role === 'admin' && (
            <button className={`nav-tab ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>
              Audit Log
            </button>
          )}
        </nav>

        <div className="auth-panel">
          {user ? (
            <div className="user-info">
              <span className="user-badge">{user.username}</span>
              <select className="role-select" value={role} onChange={(e) => loginDemo(user.username, e.target.value as UserRole)}>
                <option value="viewer">Viewer</option>
                <option value="operator">Operator</option>
                <option value="admin">Admin</option>
              </select>
              <button className="btn-secondary btn-sm" onClick={logout}>Sign Out</button>
            </div>
          ) : (
            demoMode ? (
              <button className="btn-primary btn-sm" onClick={() => loginDemo('analyst', 'operator')}>Demo Login</button>
            ) : (
              <button className="btn-primary btn-sm" onClick={initiateOIDCLogin}>SSO Sign In</button>
            )
          )}
        </div>
      </div>
    </header>
  );
};
