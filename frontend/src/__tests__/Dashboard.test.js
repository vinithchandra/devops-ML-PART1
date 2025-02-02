import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

// Mock Chart.js
jest.mock('react-chartjs-2', () => ({
  Line: () => null,
}));

// Mock fetch
global.fetch = jest.fn();

const mockDashboardData = {
  buildHistory: [
    {
      name: 'main-build',
      status: 'success',
      branch: 'main',
      timestamp: '2025-02-02T12:00:00',
      duration: '5m 30s',
    },
    {
      name: 'feature-build',
      status: 'failure',
      branch: 'feature/new-api',
      timestamp: '2025-02-02T11:30:00',
      duration: '4m 45s',
    },
  ],
  recentAnomalies: [
    {
      message: 'High CPU usage detected',
      severity: 'warning',
      timestamp: '2025-02-02T12:00:00',
    },
  ],
  performanceTrends: {
    dates: ['2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02'],
    successRates: [85, 88, 92, 90],
    buildDurations: [12, 10, 11, 9],
    currentSuccessRate: 90,
    successRateTrend: 1,
    averageDuration: 10,
    totalBuilds: 45,
    activeBuilds: 3,
  },
};

describe('Dashboard', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders dashboard with data', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockDashboardData),
      })
    );

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    // Check main sections
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Build Success Rate')).toBeInTheDocument();
    expect(screen.getByText('Average Build Duration')).toBeInTheDocument();
    expect(screen.getByText('Recent Builds')).toBeInTheDocument();
    expect(screen.getByText('Recent Anomalies')).toBeInTheDocument();

    // Check build history
    expect(screen.getByText('main-build')).toBeInTheDocument();
    expect(screen.getByText('feature-build')).toBeInTheDocument();

    // Check anomalies
    expect(screen.getByText('High CPU usage detected')).toBeInTheDocument();

    // Check performance indicators
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('10m')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('handles API error', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('API Error'))
    );

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch dashboard data')).toBeInTheDocument();
    });
  });

  it('updates data periodically', async () => {
    jest.useFakeTimers();

    const firstData = { ...mockDashboardData };
    const secondData = {
      ...mockDashboardData,
      performanceTrends: {
        ...mockDashboardData.performanceTrends,
        currentSuccessRate: 95,
      },
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

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('90%')).toBeInTheDocument();
    });

    // Fast-forward 60 seconds
    jest.advanceTimersByTime(60000);

    // Wait for update
    await waitFor(() => {
      expect(screen.getByText('95%')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });
});
