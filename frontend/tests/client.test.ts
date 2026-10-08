import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ApiClient, generatePKCECodes, savePKCESession, verifyAndConsumePKCESession } from '../src/api/client';

describe('ApiClient Integration & Envelope Matching', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('http://127.0.0.1:8000');
    vi.restoreAllMocks();
  });

  it('manages demo login and propagates bearer token to subsequent requests', async () => {
    const mockToken = 'mocked-jwt-token-xyz';
    const mockUser = {
      user_id: 'alice-1',
      username: 'alice',
      email: 'alice@example.com',
      roles: ['operator'],
      is_demo: true,
    };

    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      if (url.endsWith('/api/auth/demo-login')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              access_token: mockToken,
              token_type: 'Bearer',
              expires_in: 43200,
              user_id: 'alice-1',
              username: 'alice',
              roles: ['operator'],
            }),
        });
      }
      if (url.endsWith('/api/auth/me')) {
        // Assert Authorization header is correctly attached
        const authHeader = (init?.headers as Record<string, string>)?.['Authorization'];
        expect(authHeader).toBe(`Bearer ${mockToken}`);
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUser),
        });
      }
      return Promise.reject(new Error('Unexpected URL: ' + url));
    });

    globalThis.fetch = fetchMock;

    const loginRes = await client.demoLogin('alice', 'operator');
    expect(loginRes.access_token).toBe(mockToken);
    expect(client.getToken()).toBe(mockToken);

    const userProfile = await client.getMe();
    expect(userProfile.username).toBe('alice');
    expect(userProfile.roles).toContain('operator');
  });

  it('correctly dispatches evaluate request and receives envelope', async () => {
    const mockEvalResponse = {
      id: 101,
      prompt: 'Check code for vulnerabilities',
      overall_score: 0.82,
      grade: 'B',
      clarity_score: 0.8,
      specificity_score: 0.85,
      structure_score: 0.8,
      constraints_score: 0.8,
      output_spec_score: 0.8,
      role_score: 0.8,
      examples_score: 0.8,
      safety_score: 0.9,
      dimensions: [
        { dimension: 'clarity', score: 0.8, rating: 'good', notes: 'Clear statement' },
      ],
      weak_areas: [],
      recommendations: ['Add examples'],
      created_at: new Date().toISOString(),
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockEvalResponse),
    });

    const res = await client.evaluate({ prompt: 'Check code for vulnerabilities', domain: 'cybersecurity' });
    expect(res.id).toBe(101);
    expect(res.overall_score).toBe(0.82);
    expect(res.grade).toBe('B');
    expect(res.dimensions.length).toBe(1);
  });

  it('generates PKCE code challenge and strictly verifies state preservation in sessionStorage', async () => {
    const { verifier, challenge, state } = await generatePKCECodes();
    expect(verifier).toBeDefined();
    expect(challenge).toBeDefined();
    expect(state).toBeDefined();
    expect(verifier.length).toBeGreaterThan(10);
    expect(challenge.length).toBeGreaterThan(10);

    // Save into session storage
    savePKCESession(state, verifier);

    // Rejection on state mismatch
    const badVerifier = verifyAndConsumePKCESession('tampered-state-token');
    expect(badVerifier).toBeNull();

    // Re-save and test valid state consumption
    savePKCESession(state, verifier);
    const validVerifier = verifyAndConsumePKCESession(state);
    expect(validVerifier).toBe(verifier);

    // Verify it was consumed (single-use)
    const secondAttempt = verifyAndConsumePKCESession(state);
    expect(secondAttempt).toBeNull();
  });
});
