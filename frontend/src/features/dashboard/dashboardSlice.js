import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching dashboard data
export const fetchDashboardData = createAsyncThunk(
  'dashboard/fetchDashboardData',
  async () => {
    const response = await fetch('http://localhost:3001/dashboard');
    return await response.json();
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    data: {
      buildStats: {
        totalBuilds: 0,
        successfulBuilds: 0,
        failedBuilds: 0,
        averageBuildTime: 0,
      },
      recentBuilds: [],
      qualityMetrics: {
        codeComplexity: 0,
        testCoverage: 0,
        securityIssues: 0,
      },
      systemHealth: {
        cpu: 0,
        memory: 0,
        disk: 0,
      },
    },
    loading: false,
    error: null,
    lastUpdated: null,
  },
  reducers: {
    refreshDashboard: (state) => {
      state.loading = true;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchDashboardData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { refreshDashboard } = dashboardSlice.actions;

export default dashboardSlice.reducer;
