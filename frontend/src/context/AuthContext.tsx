import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, generatePKCECodes, savePKCESession, verifyAndConsumePKCESession } from '../api/client';
import { UserProfileResponse, UserRole } from '../types';

interface AuthContextType {
  user: UserProfileResponse | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  demoMode: boolean;
  loginDemo: (username: string, role: UserRole) => Promise<void>;
  initiateOIDCLogin: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState(true);

  useEffect(() => {
    async function initAuth() {
      try {
        setIsLoading(true);
        const config = await api.getOIDCConfig();
        setDemoMode(config.demo_mode);
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');

        if (code && state) {
          const verifier = verifyAndConsumePKCESession(state);
          if (!verifier) setError('OIDC verification failed: state mismatch.');
          else setError('OIDC callback verified.');
          window.history.replaceState({}, document.title, window.location.pathname);
        } else if (config.demo_mode) {
          try { await loginDemo('demo-operator', 'operator'); } catch {}
        }
      } catch (err: any) {
        setError(err.message || 'Auth init failed');
      } finally {
        setIsLoading(false);
      }
    }
    initAuth();
  }, []);

  const loginDemo = async (username: string, r: UserRole) => {
    try {
      setIsLoading(true);
      setError(null);
      await api.demoLogin(username, r);
      setUser(await api.getMe());
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const initiateOIDCLogin = async () => {
    try {
      setError(null);
      const config = await api.getOIDCConfig();
      const { verifier, challenge, state } = await generatePKCECodes();
      savePKCESession(state, verifier);
      const redirectUri = encodeURIComponent(`${window.location.origin}/`);
      window.location.href = `${config.issuer_url}/protocol/openid-connect/auth?client_id=${encodeURIComponent(config.client_id)}&response_type=code&scope=openid%20profile%20email&redirect_uri=${redirectUri}&code_challenge=${challenge}&code_challenge_method=S256&state=${state}`;
    } catch (err: any) {
      setError(`OIDC failed: ${err.message}`);
    }
  };

  const logout = async () => {
    try { setIsLoading(true); await api.logout(); setUser(null); }
    finally { setIsLoading(false); }
  };

  let derivedRole: UserRole = 'viewer';
  if (user?.roles?.includes('admin')) derivedRole = 'admin';
  else if (user?.roles?.includes('operator')) derivedRole = 'operator';

  return (
    <AuthContext.Provider value={{ user, role: derivedRole, isAuthenticated: !!user, isLoading, error, demoMode, loginDemo, initiateOIDCLogin, logout, clearError: () => setError(null) }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
