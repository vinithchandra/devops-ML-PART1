import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  Alert,
  Button,
  ButtonGroup,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import { fetchSystemMetrics, detectAnomalies, setTimeRange } from '../features/systemMetrics/systemMetricsSlice';

function SystemMetrics() {
  const dispatch = useDispatch();
  const { metrics, anomalies, loading, error, timeRange } = useSelector(
    (state) => state.systemMetrics
  );

  // Create chart data for the metrics
  const createChartData = (label, data, color) => ({
    labels: data.map((_, index) => `${index}m ago`),
    datasets: [
      {
        label,
        data,
        borderColor: color,
        tension: 0.1,
        fill: false,
      },
    ],
  });

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
    animation: {
      duration: 0,
    },
  };

  useEffect(() => {
    // Fetch system metrics on component mount
    dispatch(fetchSystemMetrics());
    
    // Set up polling based on the selected time range
    const interval = setInterval(() => {
      dispatch(fetchSystemMetrics());
    }, 60000); // Poll every minute
    
    return () => clearInterval(interval);
  }, [dispatch]);

  // Handle time range change
  const handleTimeRangeChange = (range) => {
    dispatch(setTimeRange(range));
    dispatch(fetchSystemMetrics());
  };

  // Handle anomaly detection
  const handleDetectAnomalies = () => {
    dispatch(detectAnomalies());
  };

  // Sample data (replace with actual data from API)
  const sampleData = {
    cpu: metrics.cpu.length > 0 ? metrics.cpu : Array.from({ length: 30 }, () => Math.random() * 100),
    memory: metrics.memory.length > 0 ? metrics.memory : Array.from({ length: 30 }, () => Math.random() * 100),
    disk: metrics.disk.length > 0 ? metrics.disk : Array.from({ length: 30 }, () => Math.random() * 100),
  };

  if (loading && Object.keys(metrics).every(key => metrics[key].length === 0)) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Metrics
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <ButtonGroup variant="outlined" aria-label="time range">
          <Button 
            onClick={() => handleTimeRangeChange('1h')}
            variant={timeRange === '1h' ? 'contained' : 'outlined'}
          >
            1 Hour
          </Button>
          <Button 
            onClick={() => handleTimeRangeChange('6h')}
            variant={timeRange === '6h' ? 'contained' : 'outlined'}
          >
            6 Hours
          </Button>
          <Button 
            onClick={() => handleTimeRangeChange('24h')}
            variant={timeRange === '24h' ? 'contained' : 'outlined'}
          >
            24 Hours
          </Button>
        </ButtonGroup>
        
        <Button 
          variant="contained" 
          color="secondary" 
          onClick={handleDetectAnomalies}
          disabled={loading}
        >
          Detect Anomalies
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* CPU Usage */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              CPU Usage
            </Typography>
            <Line
              data={createChartData('CPU %', sampleData.cpu, 'rgb(75, 192, 192)')}
              options={chartOptions}
            />
          </Paper>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Memory Usage
            </Typography>
            <Line
              data={createChartData('Memory %', sampleData.memory, 'rgb(255, 99, 132)')}
              options={chartOptions}
            />
          </Paper>
        </Grid>

        {/* Disk Usage */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Disk Usage
            </Typography>
            <Line
              data={createChartData('Disk %', sampleData.disk, 'rgb(153, 102, 255)')}
              options={chartOptions}
            />
          </Paper>
        </Grid>

        {/* Anomaly Detection */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Anomaly Detection
            </Typography>
            <Box sx={{ mt: 2 }}>
              {anomalies.length === 0 ? (
                <Alert severity="success">No anomalies detected</Alert>
              ) : (
                anomalies.map((anomaly, index) => (
                  <Alert key={index} severity={anomaly.severity === 'high' ? 'error' : 'warning'} sx={{ mb: 1 }}>
                    {anomaly.metric}: {anomaly.value.toFixed(1)}% (Threshold: {anomaly.threshold}%)
                  </Alert>
                ))
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default SystemMetrics;
