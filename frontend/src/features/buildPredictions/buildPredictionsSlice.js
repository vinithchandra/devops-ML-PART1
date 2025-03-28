import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching build predictions
export const fetchBuildPredictions = createAsyncThunk(
  'buildPredictions/fetchBuildPredictions',
  async () => {
    const response = await fetch('http://localhost:3001/dashboard');
    const data = await response.json();
    return data.buildPredictions || [];
  }
);

// Async thunk for predicting build success
export const predictBuildSuccess = createAsyncThunk(
  'buildPredictions/predictBuildSuccess',
  async (buildData) => {
    // In a real implementation, this would call the backend API
    // For now, we'll simulate a response
    return {
      buildId: buildData.id || Math.floor(Math.random() * 1000),
      successProbability: Math.random() * 100,
      estimatedBuildTime: Math.floor(Math.random() * 300) + 60, // 1-5 minutes in seconds
      riskFactors: [
        { name: 'Code Complexity', value: Math.random() * 10 },
        { name: 'Test Coverage', value: Math.random() * 100 },
        { name: 'Recent Failures', value: Math.floor(Math.random() * 5) },
      ],
      recommendations: [
        'Add more unit tests to improve coverage',
        'Refactor complex methods to reduce complexity',
        'Update dependencies to latest versions',
      ],
    };
  }
);

const buildPredictionsSlice = createSlice({
  name: 'buildPredictions',
  initialState: {
    predictions: [],
    history: [],
    loading: false,
    error: null,
    currentPrediction: null,
  },
  reducers: {
    clearCurrentPrediction: (state) => {
      state.currentPrediction = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBuildPredictions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBuildPredictions.fulfilled, (state, action) => {
        state.loading = false;
        state.predictions = action.payload;
      })
      .addCase(fetchBuildPredictions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(predictBuildSuccess.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(predictBuildSuccess.fulfilled, (state, action) => {
        state.loading = false;
        state.currentPrediction = action.payload;
        state.history = [action.payload, ...state.history.slice(0, 9)]; // Keep last 10 predictions
      })
      .addCase(predictBuildSuccess.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearCurrentPrediction } = buildPredictionsSlice.actions;

export default buildPredictionsSlice.reducer;
