import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { OptimizeView } from '../src/components/OptimizeView';
import { api } from '../src/api/client';
import type { OptimizationResponse } from '../src/types';

describe('OptimizeView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders input form and triggers optimization on submit', async () => {
    const mockOpt: OptimizationResponse = {
      id: 1,
      original_prompt: 'Summarize this email',
      optimized_prompt: '## Role & Persona\nYou are an authoritative subject matter expert and senior technical advisor.\n\n## Task\nSummarize this email\n\n## Output Specification\nConcise summary in 3-5 bullet points',
      score_before: 0.26,
      score_after: 0.71,
      improvement_delta: 0.45,
      strategy: 'structured',
      target_domain: 'general',
      llm_used: false,
      diff_summary: 'Added role, structured task, output specification',
      advisory_notes: null,
      created_at: '2024-01-01T00:00:00Z',
    };

    vi.spyOn(api, 'getOptimizations').mockResolvedValue({ items: [], total: 0, page: 1, page_size: 10 });
    vi.spyOn(api, 'optimize').mockResolvedValue(mockOpt);

    render(<OptimizeView />);

    expect(screen.getByText('Prompt Mutation & Optimization Engine')).toBeInTheDocument();
    const textarea = screen.getByPlaceholderText(/Enter prompt to optimize/i);
    const runButton = screen.getByRole('button', { name: /Run Optimization/i });

    fireEvent.change(textarea, { target: { value: 'Summarize this email' } });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText('Optimization Result')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText(/Score Before/i)).toBeInTheDocument();
      expect(screen.getByText(/Score After/i)).toBeInTheDocument();
    });
  });

  it('reruns optimization from history item', async () => {
    const historyItem: OptimizationResponse = {
      id: 1,
      original_prompt: 'Write a Python function',
      optimized_prompt: '## Role & Persona\nYou are a Staff Software Architect...\n\n## Task\nWrite a Python function\n\n## Output Specification\nType-hinted function with docstring',
      score_before: 0.35,
      score_after: 0.78,
      improvement_delta: 0.43,
      strategy: 'structured',
      target_domain: 'software_engineering',
      llm_used: false,
      diff_summary: 'Added role, structured task, output specification, type hints',
      advisory_notes: null,
      created_at: '2024-01-01T00:00:00Z',
    };

    const rerunResult: OptimizationResponse = {
      id: 2,
      original_prompt: 'Write a Python function',
      optimized_prompt: '## Role & Persona\nYou are a Staff Software Architect...\n\n## Task\nWrite a Python function\n\n## Output Specification\nType-hinted function with docstring',
      score_before: 0.35,
      score_after: 0.82,
      improvement_delta: 0.47,
      strategy: 'structured',
      target_domain: 'software_engineering',
      llm_used: false,
      diff_summary: 'Added role, structured task, output specification, type hints',
      advisory_notes: null,
      created_at: '2024-01-02T00:00:00Z',
    };

    vi.spyOn(api, 'getOptimizations').mockResolvedValue({ items: [historyItem], total: 1, page: 1, page_size: 10 });
    const optSpy = vi.spyOn(api, 'optimize').mockResolvedValue(rerunResult);

    render(<OptimizeView />);

    // Wait for history to load - check for history section elements
    await waitFor(() => {
      expect(screen.getByText('Recent Optimizations')).toBeInTheDocument();
      expect(screen.getByText('35% → 78% (+43%)')).toBeInTheDocument();
    });

    // Click rerun button (↻) on the history item
    const rerunButton = screen.getByTitle('Rerun optimization');
    fireEvent.click(rerunButton);

    // Verify form was populated and optimization triggered
    await waitFor(() => {
      expect(optSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          prompt: 'Write a Python function',
          strategy: 'structured',
          target_domain: 'software_engineering',
          use_advisory_llm: false,
        })
      );
    });

    // Verify new result is displayed
    await waitFor(() => {
      expect(screen.getByText('Optimization Result')).toBeInTheDocument();
    });
  });

  it('shows loading state during optimization', async () => {
    let resolveOptimize: (value: OptimizationResponse) => void;
    const optimizePromise = new Promise<OptimizationResponse>((resolve) => {
      resolveOptimize = resolve;
    });

    vi.spyOn(api, 'getOptimizations').mockResolvedValue({ items: [], total: 0, page: 1, page_size: 10 });
    vi.spyOn(api, 'optimize').mockImplementation(() => optimizePromise);

    render(<OptimizeView />);

    const textarea = screen.getByPlaceholderText(/Enter prompt to optimize/i);
    const runButton = screen.getByRole('button', { name: /Run Optimization/i });

    fireEvent.change(textarea, { target: { value: 'Test prompt for optimization' } });
    fireEvent.click(runButton);

    // Button should show loading state
    expect(screen.getByRole('button', { name: /Optimizing.../i })).toBeInTheDocument();

    // Resolve the promise
    resolveOptimize!({
      id: 3,
      original_prompt: 'Test prompt for optimization',
      optimized_prompt: 'Optimized result',
      score_before: 0.3,
      score_after: 0.7,
      improvement_delta: 0.4,
      strategy: 'structured',
      target_domain: 'general',
      llm_used: false,
      diff_summary: 'Test diff',
      advisory_notes: null,
      created_at: '2024-01-01T00:00:00Z',
    });

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Run Optimization/i })).toBeInTheDocument();
    });
  });
});
