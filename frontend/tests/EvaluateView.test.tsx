import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EvaluateView } from '../src/components/EvaluateView';
import { api } from '../src/api/client';

describe('EvaluateView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders input form and triggers evaluation on submit', async () => {
    const mockEval = {
      id: 1,
      prompt: 'Write clean code for payment processing',
      overall_score: 0.88,
      grade: 'B',
      clarity_score: 0.9,
      specificity_score: 0.85,
      structure_score: 0.85,
      constraints_score: 0.8,
      output_spec_score: 0.9,
      role_score: 0.9,
      examples_score: 0.8,
      safety_score: 0.95,
      dimensions: [
        { dimension: 'clarity', score: 0.9, rating: 'strong', notes: 'Clear goals' },
        { dimension: 'safety', score: 0.95, rating: 'strong', notes: 'Guarded' },
      ],
      weak_areas: ['examples'],
      recommendations: ['Add few-shot demonstrations'],
      created_at: new Date().toISOString(),
    };

    vi.spyOn(api, 'getEvaluations').mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    vi.spyOn(api, 'evaluate').mockResolvedValue(mockEval);

    render(<EvaluateView />);

    expect(screen.getByText('Multi-Dimensional Prompt Evaluation')).toBeInTheDocument();
    const textarea = screen.getByPlaceholderText(/Enter prompt to evaluate/i);
    const scoreButton = screen.getByRole('button', { name: /Score Prompt/i });

    // Submit with short prompt should be disabled or alert
    fireEvent.change(textarea, { target: { value: 'Write clean code for payment processing' } });
    fireEvent.click(scoreButton);

    await waitFor(() => {
      expect(screen.getByText('88%')).toBeInTheDocument();
      expect(screen.getByText('B')).toBeInTheDocument();
      expect(screen.getByText('Rubric Grade')).toBeInTheDocument();
      expect(screen.getByText('Clear goals')).toBeInTheDocument();
    });
  });
});
