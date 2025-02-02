import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SystemMetrics from '../pages/SystemMetrics';

// Mock Chart.js
jest.mock('react-chartjs-2', () => ({
  Line: () => null,
}));

// Mock fetch
global.fetch = jest.fn();

const mockMetricsData = {
  cpu: Array.from({ length: 30 }, () => Math.random() * 100),
  memory: Array.from({ length: 30 }, () => Math.random() * 100),
  disk: Array.from({ length: 30 }, () => Math.random() * 100),
  anomalies: [
    {
      timestamp: '2025-02-02T12:00:00',
      message: 'High CPU usage detected',
      severity: 'warning'
    }
  ]
};

describe('SystemMetrics', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders system metrics dashboard', () => {
    render(<SystemMetrics />);
    
    expect(screen.getByText(/System Metrics/i)).toBeInTheDocument();
    expect(screen.getByText(/CPU Usage/i)).toBeInTheDocument();
    expect(screen.getByText(/Memory Usage/i)).toBeInTheDocument();
    expect(screen.getByText(/Disk Usage/i)).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<SystemMetrics />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('fetches and displays metrics data', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockMetricsData),
      })
    );

    render(<SystemMetrics />);

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    expect(fetch).toHaveBeenCalledWith('/api/metrics/system');
  });

  it('displays error message when API fails', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('API Error'))
    );

    render(<SystemMetrics />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch system metrics/i)).toBeInTheDocument();
    });
  });

  it('displays anomaly alerts when present', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockMetricsData),
      })
    );

    render(<SystemMetrics />);

    await waitFor(() => {
      expect(screen.getByText(/High CPU usage detected/i)).toBeInTheDocument();
    });
  });

  it('updates metrics periodically', async () => {
    jest.useFakeTimers();

    const firstData = { ...mockMetricsData };
    const secondData = {
      ...mockMetricsData,
      anomalies: [
        {
          timestamp: '2025-02-02T12:01:00',
          message: 'Memory usage spike detected',
          severity: 'warning'
        }
      ]
    };

    fetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(firstData),
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(secondData),
        })
      );

    render(<SystemMetrics />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText(/High CPU usage detected/i)).toBeInTheDocument();
    });

    // Fast-forward 60 seconds
    jest.advanceTimersByTime(60000);

    // Wait for update
    await waitFor(() => {
      expect(screen.getByText(/Memory usage spike detected/i)).toBeInTheDocument();
    });

    jest.useRealTimers();
  });
});
