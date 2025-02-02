import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  Alert,
} from '@mui/material';
import { Line } from 'react-chartjs-2';

function SystemMetrics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState({
    cpu: [],
    memory: [],
    disk: [],
    anomalies: [],
  });

  // Sample data for the charts
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
    const fetchMetrics = async () => {
      try {
        // TODO: Replace with actual API call
        const response = await fetch('/api/metrics/system');
        const data = await response.json();
        setMetrics(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch system metrics');
        setLoading(false);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up polling every 60 seconds
    const interval = setInterval(fetchMetrics, 60000);

    return () => clearInterval(interval);
  }, []);

  // Sample data (replace with actual data from API)
  const sampleData = {
    cpu: Array.from({ length: 30 }, () => Math.random() * 100),
    memory: Array.from({ length: 30 }, () => Math.random() * 100),
    disk: Array.from({ length: 30 }, () => Math.random() * 100),
  };

  if (loading) {
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
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Anomaly Detection
            </Typography>
            <Box sx={{ mt: 2 }}>
              {metrics.anomalies.length === 0 ? (
                <Alert severity="success">No anomalies detected</Alert>
              ) : (
                metrics.anomalies.map((anomaly, index) => (
                  <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                    {anomaly.message}
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
