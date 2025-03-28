import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
} from '@mui/material';
import {
  Timeline,
  CheckCircle,
  Error,
  Warning,
  TrendingUp,
  TrendingDown,
  Schedule,
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { fetchDashboardData } from '../features/dashboard/dashboardSlice';
import { useNavigate } from 'react-router-dom';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function Dashboard() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { data, loading, error } = useSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardData());
    const interval = setInterval(() => {
      dispatch(fetchDashboardData());
    }, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [dispatch]);

  const getBuildStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'success':
        return 'success';
      case 'failure':
        return 'error';
      case 'in_progress':
        return 'info';
      default:
        return 'warning';
    }
  };

  const getAnomalySeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <Error color="error" />;
      case 'warning':
        return <Warning color="warning" />;
      default:
        return <Warning color="info" />;
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (loading && (!data || Object.keys(data).length === 0)) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Build Success Rate */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Build Success Rate
            </Typography>
            <Line
              data={{
                labels: data.performanceTrends?.dates || [],
                datasets: [
                  {
                    label: 'Success Rate (%)',
                    data: data.performanceTrends?.successRates || [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                  },
                ],
              }}
              options={chartOptions}
            />
          </Paper>
        </Grid>

        {/* Average Build Duration */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Average Build Duration
            </Typography>
            <Line
              data={{
                labels: data.performanceTrends?.dates || [],
                datasets: [
                  {
                    label: 'Duration (minutes)',
                    data: data.performanceTrends?.buildDurations || [],
                    borderColor: 'rgb(153, 102, 255)',
                    tension: 0.1,
                  },
                ],
              }}
              options={chartOptions}
            />
          </Paper>
        </Grid>

        {/* Recent Builds */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Builds
            </Typography>
            <List>
              {(data.buildHistory || []).slice(0, 5).map((build, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {build.status === 'success' ? (
                      <CheckCircle color="success" />
                    ) : build.status === 'failure' ? (
                      <Error color="error" />
                    ) : (
                      <Schedule color="info" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={build.name}
                    secondary={`${build.branch} - ${new Date(
                      build.timestamp
                    ).toLocaleString()}`}
                  />
                  <Chip
                    label={build.duration}
                    size="small"
                    icon={<Timeline />}
                    variant="outlined"
                  />
                </ListItem>
              ))}
            </List>
            <Button
              variant="outlined"
              fullWidth
              sx={{ mt: 2 }}
              onClick={() => navigate('/build-predictions')}
            >
              View All Builds
            </Button>
          </Paper>
        </Grid>

        {/* Recent Anomalies */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Anomalies
            </Typography>
            <List>
              {(data.recentAnomalies || []).length === 0 ? (
                <ListItem>
                  <ListItemText
                    primary="No anomalies detected"
                    secondary="System is running normally"
                  />
                </ListItem>
              ) : (
                (data.recentAnomalies || []).map((anomaly, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {getAnomalySeverityIcon(anomaly.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={anomaly.message}
                      secondary={new Date(anomaly.timestamp).toLocaleString()}
                    />
                    <Chip
                      label={anomaly.severity}
                      color={getBuildStatusColor(anomaly.severity)}
                      size="small"
                    />
                  </ListItem>
                ))
              )}
            </List>
            <Button
              variant="outlined"
              fullWidth
              sx={{ mt: 2 }}
              onClick={() => navigate('/system-metrics')}
            >
              View System Metrics
            </Button>
          </Paper>
        </Grid>

        {/* Performance Indicators */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance Indicators
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {data.performanceTrends?.currentSuccessRate || 0}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Current Success Rate
                  </Typography>
                  {data.performanceTrends?.successRateTrend > 0 ? (
                    <TrendingUp color="success" />
                  ) : (
                    <TrendingDown color="error" />
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {data.performanceTrends?.averageDuration || 0}m
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Average Build Time
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {data.performanceTrends?.totalBuilds || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Builds Today
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {data.performanceTrends?.activeBuilds || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active Builds
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
