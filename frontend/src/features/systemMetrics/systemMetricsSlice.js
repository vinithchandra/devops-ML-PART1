import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching system metrics
export const fetchSystemMetrics = createAsyncThunk(
  'systemMetrics/fetchSystemMetrics',
  async () => {
    const response = await fetch('http://localhost:3001/dashboard');
    const data = await response.json();
    return data.systemMetrics || {
      cpu: [],
      memory: [],
      disk: [],
      network: [],
    };
  }
);

// Async thunk for detecting anomalies
export const detectAnomalies = createAsyncThunk(
  'systemMetrics/detectAnomalies',
  async () => {
    // In a real implementation, this would call the backend API
    // For now, we'll simulate a response
    return {
      anomalies: [
        {
          id: Math.floor(Math.random() * 1000),
          metric: 'CPU Usage',
          value: 95 + Math.random() * 5,
          threshold: 90,
          timestamp: new Date().toISOString(),
          severity: 'high',
        },
        {
          id: Math.floor(Math.random() * 1000),
          metric: 'Memory Usage',
          value: 85 + Math.random() * 10,
          threshold: 80,
          timestamp: new Date().toISOString(),
          severity: 'medium',
        },
      ],
    };
  }
);

const systemMetricsSlice = createSlice({
  name: 'systemMetrics',
  initialState: {
    metrics: {
      cpu: [],
      memory: [],
      disk: [],
      network: [],
    },
    anomalies: [],
    loading: false,
    error: null,
    timeRange: '1h', // Default time range
  },
  reducers: {
    setTimeRange: (state, action) => {
      state.timeRange = action.payload;
    },
    clearAnomalies: (state) => {
      state.anomalies = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSystemMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload;
      })
      .addCase(fetchSystemMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(detectAnomalies.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(detectAnomalies.fulfilled, (state, action) => {
        state.loading = false;
        state.anomalies = action.payload.anomalies;
      })
      .addCase(detectAnomalies.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { setTimeRange, clearAnomalies } = systemMetricsSlice.actions;

export default systemMetricsSlice.reducer;
