import { configureStore } from '@reduxjs/toolkit';
import buildPredictionsReducer from './features/buildPredictions/buildPredictionsSlice';
import systemMetricsReducer from './features/systemMetrics/systemMetricsSlice';
import dashboardReducer from './features/dashboard/dashboardSlice';
import settingsReducer from './features/settings/settingsSlice';

const store = configureStore({
  reducer: {
    buildPredictions: buildPredictionsReducer,
    systemMetrics: systemMetricsReducer,
    dashboard: dashboardReducer,
    settings: settingsReducer,
  },
});

export default store;
