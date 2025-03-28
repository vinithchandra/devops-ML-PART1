import { createSlice } from '@reduxjs/toolkit';

const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    theme: 'light',
    notifications: {
      email: true,
      slack: false,
      inApp: true,
    },
    refreshInterval: 60, // in seconds
    apiEndpoints: {
      backend: 'http://localhost:8000',
      mockApi: 'http://localhost:3001',
    },
    thresholds: {
      buildSuccess: 80, // Minimum probability to consider a build likely to succeed
      codeComplexity: 20, // Maximum acceptable code complexity
      testCoverage: 70, // Minimum acceptable test coverage
      memoryUsage: 80, // Maximum acceptable memory usage percentage
      cpuUsage: 90, // Maximum acceptable CPU usage percentage
    },
  },
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    updateNotificationSettings: (state, action) => {
      state.notifications = { ...state.notifications, ...action.payload };
    },
    setRefreshInterval: (state, action) => {
      state.refreshInterval = action.payload;
    },
    updateApiEndpoint: (state, action) => {
      state.apiEndpoints = { ...state.apiEndpoints, ...action.payload };
    },
    updateThresholds: (state, action) => {
      state.thresholds = { ...state.thresholds, ...action.payload };
    },
  },
});

export const {
  toggleTheme,
  updateNotificationSettings,
  setRefreshInterval,
  updateApiEndpoint,
  updateThresholds,
} = settingsSlice.actions;

export default settingsSlice.reducer;
