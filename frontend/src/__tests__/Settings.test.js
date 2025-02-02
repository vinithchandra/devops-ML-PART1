import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Settings from '../pages/Settings';

// Mock fetch
global.fetch = jest.fn();

describe('Settings', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders settings form with default values', () => {
    render(<Settings />);

    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Jenkins URL/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Jenkins Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Jenkins API Token/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Enable Notifications/i)).toBeInTheDocument();
  });

  it('updates form values on input change', () => {
    render(<Settings />);

    const jenkinsUrlInput = screen.getByLabelText(/Jenkins URL/i);
    fireEvent.change(jenkinsUrlInput, {
      target: { value: 'https://jenkins.example.com' },
    });

    expect(jenkinsUrlInput.value).toBe('https://jenkins.example.com');
  });

  it('saves settings successfully', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
      })
    );

    render(<Settings />);

    // Fill in form fields
    fireEvent.change(screen.getByLabelText(/Jenkins URL/i), {
      target: { value: 'https://jenkins.example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Jenkins Username/i), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByLabelText(/Jenkins API Token/i), {
      target: { value: 'secret-token' },
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Save Settings/i }));

    // Check success message
    await waitFor(() => {
      expect(screen.getByText(/Settings saved successfully/i)).toBeInTheDocument();
    });

    // Verify API call
    expect(fetch).toHaveBeenCalledWith('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: expect.any(String),
    });
  });

  it('displays error message on save failure', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('API Error'))
    );

    render(<Settings />);

    fireEvent.click(screen.getByRole('button', { name: /Save Settings/i }));

    await waitFor(() => {
      expect(screen.getByText(/Failed to save settings/i)).toBeInTheDocument();
    });
  });

  it('validates numeric inputs', () => {
    render(<Settings />);

    const modelUpdateInput = screen.getByLabelText(/Model Update Interval/i);
    const metricsCollectionInput = screen.getByLabelText(/Metrics Collection Interval/i);

    // Test invalid values
    fireEvent.change(modelUpdateInput, {
      target: { value: '-1' },
    });
    fireEvent.change(metricsCollectionInput, {
      target: { value: '61' },
    });

    expect(modelUpdateInput.value).toBe('1'); // Should be clamped to min
    expect(metricsCollectionInput.value).toBe('60'); // Should be clamped to max
  });

  it('toggles notification settings', () => {
    render(<Settings />);

    const notificationToggle = screen.getByRole('checkbox', {
      name: /Enable Notifications/i,
    });

    expect(notificationToggle).toBeChecked(); // Default value
    fireEvent.click(notificationToggle);
    expect(notificationToggle).not.toBeChecked();
  });
});
