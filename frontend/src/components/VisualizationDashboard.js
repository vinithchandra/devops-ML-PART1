import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, CircularProgress, Button } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';

const VisualizationDashboard = () => {
  const theme = useTheme();
  const [charts, setCharts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCharts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/visualization/dashboard-summary');
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setCharts(data);
    } catch (err) {
      console.error('Error fetching charts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharts();
  }, []);

  const handleRefresh = () => {
    fetchCharts();
  };

  if (loading && Object.keys(charts).length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && Object.keys(charts).length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          Error loading visualization data
        </Typography>
        <Typography variant="body1" paragraph>
          {error}
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          CI/CD Pipeline Visualization Dashboard
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {Object.entries(charts).map(([key, chartData]) => (
          <Grid item xs={12} md={6} key={key}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 400,
                bgcolor: theme.palette.background.paper,
                boxShadow: 3,
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                {chartData.title}
              </Typography>
              {chartData.chartType === 'image' ? (
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  flexGrow: 1,
                  overflow: 'hidden'
                }}>
                  <img 
                    src={`data:image/png;base64,${chartData.chart}`} 
                    alt={chartData.title}
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '100%',
                      objectFit: 'contain'
                    }}
                  />
                </Box>
              ) : (
                <Typography variant="body1">
                  Unsupported chart type: {chartData.chartType}
                </Typography>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default VisualizationDashboard;
