import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LibraryView } from '../src/components/LibraryView';
import { api } from '../src/api/client';
import { AuthProvider } from '../src/context/AuthContext';

describe('LibraryView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(api, 'getOIDCConfig').mockResolvedValue({
      issuer_url: 'http://127.0.0.1:8080/realms/prompt-optimizer',
      client_id: 'test-client',
      audience: 'test-aud',
      demo_mode: true,
      environment: 'development',
    });
    vi.spyOn(api, 'demoLogin').mockResolvedValue({
      access_token: 'test-tok',
      token_type: 'Bearer',
      expires_in: 3600,
      user_id: 'user-1',
      username: 'tester',
      roles: ['operator'],
    });
    vi.spyOn(api, 'getMe').mockResolvedValue({
      user_id: 'user-1',
      username: 'tester',
      email: 'test@example.com',
      roles: ['operator'],
      is_demo: true,
    });
  });

  it('renders prompt library templates and opens creation modal', async () => {
    const mockPrompts = [
      {
        id: 1,
        name: 'Threat Modeler',
        prompt: 'Analyze architecture for STRIDE threats',
        domain: 'cybersecurity',
        tags: 'security,stride',
        version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    vi.spyOn(api, 'listPrompts').mockResolvedValue({
      items: mockPrompts,
      total: 1,
      page: 1,
      page_size: 50,
    });

    render(
      <AuthProvider>
        <LibraryView />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Threat Modeler')).toBeInTheDocument();
      expect(screen.getByText('#security')).toBeInTheDocument();
      expect(screen.getByText('v1')).toBeInTheDocument();
    });

    // Click "+ New Template"
    const newBtn = screen.getByRole('button', { name: /\+ New Template/i });
    fireEvent.click(newBtn);

    expect(screen.getByText('Create New Prompt Template')).toBeInTheDocument();
    expect(screen.getByLabelText(/Template Name:/i)).toBeInTheDocument();
  });
});
