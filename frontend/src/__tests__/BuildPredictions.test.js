import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import BuildPredictions from '../pages/BuildPredictions';

// Mock the fetch function
global.fetch = jest.fn();

const mockResponse = {
  success_probability: 0.85,
  estimated_duration: 420,
  risk_factors: ['recent_failures', 'complex_changes'],
  recommendations: [
    'Consider breaking down the changes into smaller commits',
    'Add more unit tests for modified components'
  ]
};

describe('BuildPredictions', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders the build predictions form', () => {
    render(
      <BrowserRouter>
        <BuildPredictions />
      </BrowserRouter>
    );

    expect(screen.getByText(/Build Success Prediction/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Repository URL/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Branch Name/i)).toBeInTheDocument();
  });

  it('handles form submission and displays predictions', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      })
    );

    render(
      <BrowserRouter>
        <BuildPredictions />
      </BrowserRouter>
    );

    // Fill in form fields
    fireEvent.change(screen.getByLabelText(/Repository URL/i), {
      target: { value: 'https://github.com/test/repo' },
    });
    fireEvent.change(screen.getByLabelText(/Branch Name/i), {
      target: { value: 'main' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Predict/i }));

    // Wait for predictions to be displayed
    await waitFor(() => {
      expect(screen.getByText(/85%/)).toBeInTheDocument();
      expect(screen.getByText(/7 minutes/)).toBeInTheDocument();
    });
  });

  it('displays error message on API failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('API Error'))
    );

    render(
      <BrowserRouter>
        <BuildPredictions />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/Repository URL/i), {
      target: { value: 'https://github.com/test/repo' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Predict/i }));

    await waitFor(() => {
      expect(screen.getByText(/Error getting predictions/i)).toBeInTheDocument();
    });
  });

  it('validates required fields', async () => {
    render(
      <BrowserRouter>
        <BuildPredictions />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /Predict/i }));

    await waitFor(() => {
      expect(screen.getByText(/Repository URL is required/i)).toBeInTheDocument();
    });
  });
});
