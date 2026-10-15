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
      domain: 'general',
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

  it('reruns evaluation from history item', async () => {
    const historyItem = {
      id: 1,
      prompt: 'Original prompt for testing',
      domain: 'software_engineering',
      overall_score: 0.75,
      grade: 'C',
      clarity_score: 0.8,
      specificity_score: 0.7,
      structure_score: 0.75,
      constraints_score: 0.7,
      output_spec_score: 0.8,
      role_score: 0.75,
      examples_score: 0.7,
      safety_score: 0.85,
      dimensions: [
        { dimension: 'clarity', score: 0.8, rating: 'strong', notes: 'Good' },
        { dimension: 'safety', score: 0.85, rating: 'strong', notes: 'Safe' },
      ],
      weak_areas: ['specificity'],
      recommendations: ['Be more specific'],
      created_at: new Date().toISOString(),
    };

    const rerunResult = {
      id: 2,
      prompt: 'Original prompt for testing',
      domain: 'software_engineering',
      overall_score: 0.82,
      grade: 'B',
      clarity_score: 0.85,
      specificity_score: 0.78,
      structure_score: 0.82,
      constraints_score: 0.78,
      output_spec_score: 0.85,
      role_score: 0.82,
      examples_score: 0.78,
      safety_score: 0.9,
      dimensions: [
        { dimension: 'clarity', score: 0.85, rating: 'strong', notes: 'Good' },
        { dimension: 'safety', score: 0.9, rating: 'strong', notes: 'Safe' },
      ],
      weak_areas: ['specificity'],
      recommendations: ['Be more specific'],
      created_at: new Date().toISOString(),
    };

    vi.spyOn(api, 'getEvaluations').mockResolvedValue({
      items: [historyItem],
      total: 1,
      page: 1,
      page_size: 10,
    });

    const evalSpy = vi.spyOn(api, 'evaluate').mockResolvedValue(rerunResult);

    render(<EvaluateView />);

    await waitFor(() => {
      expect(screen.getByText(/Original prompt for testing/i)).toBeInTheDocument();
    });

    // Click rerun button (↻) on the history item
    const rerunButton = screen.getByTitle('Rerun evaluation');
    fireEvent.click(rerunButton);

    // Verify form was populated and evaluation triggered
    await waitFor(() => {
      expect(evalSpy).toHaveBeenCalledWith({
        prompt: 'Original prompt for testing',
        domain: 'software_engineering',
      });
    });

    // Verify new result is displayed
    await waitFor(() => {
      expect(screen.getByText('82%')).toBeInTheDocument();
      expect(screen.getByText('B')).toBeInTheDocument();
    });
  });
});
