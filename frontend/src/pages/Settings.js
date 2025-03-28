import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  toggleTheme,
  updateNotificationSettings,
  setRefreshInterval,
  updateApiEndpoint,
  updateThresholds,
} from '../features/settings/settingsSlice';

function Settings() {
  const dispatch = useDispatch();
  const settings = useSelector((state) => state.settings);
  const [localSettings, setLocalSettings] = React.useState({
    jenkinsUrl: '',
    jenkinsUser: '',
    jenkinsToken: '',
    modelUpdateInterval: '24',
    metricsCollectionInterval: '5',
  });
  const [saved, setSaved] = React.useState(false);
  const [error, setError] = React.useState(null);

  // Handle form input changes
  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    setLocalSettings(prev => ({
      ...prev,
      [name]: event.target.type === 'checkbox' ? checked : value,
    }));
    setSaved(false);
  };

  // Handle notification settings changes
  const handleNotificationChange = (event) => {
    const { name, checked } = event.target;
    dispatch(updateNotificationSettings({ [name]: checked }));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  // Handle theme toggle
  const handleThemeToggle = () => {
    dispatch(toggleTheme());
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  // Handle refresh interval change
  const handleRefreshIntervalChange = (event, newValue) => {
    dispatch(setRefreshInterval(newValue));
  };

  // Handle threshold changes
  const handleThresholdChange = (event) => {
    const { name, value } = event.target;
    dispatch(updateThresholds({ [name]: value }));
  };

  // Handle API endpoint changes
  const handleApiEndpointChange = (event) => {
    const { name, value } = event.target;
    dispatch(updateApiEndpoint({ [name]: value }));
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // TODO: Implement API call to save settings
      await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...localSettings,
          ...settings
        }),
      });
      setSaved(true);
      setError(null);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to save settings');
      setSaved(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Jenkins Configuration Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Jenkins Configuration
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Jenkins URL"
                name="jenkinsUrl"
                value={localSettings.jenkinsUrl}
                onChange={handleChange}
                helperText="e.g., https://jenkins.example.com"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Jenkins Username"
                name="jenkinsUser"
                value={localSettings.jenkinsUser}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="password"
                label="Jenkins API Token"
                name="jenkinsToken"
                value={localSettings.jenkinsToken}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                System Settings
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Model Update Interval (hours)"
                name="modelUpdateInterval"
                value={localSettings.modelUpdateInterval}
                onChange={handleChange}
                inputProps={{ min: 1, max: 168 }}
                helperText="How often to retrain ML models"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Metrics Collection Interval (minutes)"
                name="metricsCollectionInterval"
                value={localSettings.metricsCollectionInterval}
                onChange={handleChange}
                inputProps={{ min: 1, max: 60 }}
                helperText="How often to collect system metrics"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                UI Settings
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.theme === 'dark'}
                    onChange={handleThemeToggle}
                    name="theme"
                  />
                }
                label={`Theme: ${settings.theme === 'dark' ? 'Dark' : 'Light'}`}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography id="refresh-interval-slider" gutterBottom>
                Dashboard Refresh Interval: {settings.refreshInterval} seconds
              </Typography>
              <Slider
                value={settings.refreshInterval}
                onChange={handleRefreshIntervalChange}
                aria-labelledby="refresh-interval-slider"
                valueLabelDisplay="auto"
                step={10}
                marks
                min={10}
                max={120}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Notification Settings
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.email}
                    onChange={handleNotificationChange}
                    name="email"
                  />
                }
                label="Email Notifications"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.slack}
                    onChange={handleNotificationChange}
                    name="slack"
                  />
                }
                label="Slack Notifications"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications.inApp}
                    onChange={handleNotificationChange}
                    name="inApp"
                  />
                }
                label="In-App Notifications"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                API Endpoints
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Backend API URL"
                name="backend"
                value={settings.apiEndpoints.backend}
                onChange={handleApiEndpointChange}
                helperText="URL for the FastAPI backend"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Mock API URL"
                name="mockApi"
                value={settings.apiEndpoints.mockApi}
                onChange={handleApiEndpointChange}
                helperText="URL for the mock API (development only)"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Quality Thresholds
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Build Success Probability: {settings.thresholds.buildSuccess}%
              </Typography>
              <Slider
                value={settings.thresholds.buildSuccess}
                onChange={(e, value) => 
                  dispatch(updateThresholds({ buildSuccess: value }))
                }
                aria-labelledby="build-success-slider"
                valueLabelDisplay="auto"
                step={5}
                marks
                min={50}
                max={95}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Code Complexity Threshold: {settings.thresholds.codeComplexity}
              </Typography>
              <Slider
                value={settings.thresholds.codeComplexity}
                onChange={(e, value) => 
                  dispatch(updateThresholds({ codeComplexity: value }))
                }
                aria-labelledby="code-complexity-slider"
                valueLabelDisplay="auto"
                step={1}
                marks
                min={10}
                max={30}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Test Coverage Threshold: {settings.thresholds.testCoverage}%
              </Typography>
              <Slider
                value={settings.thresholds.testCoverage}
                onChange={(e, value) => 
                  dispatch(updateThresholds({ testCoverage: value }))
                }
                aria-labelledby="test-coverage-slider"
                valueLabelDisplay="auto"
                step={5}
                marks
                min={50}
                max={95}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Memory Usage Threshold: {settings.thresholds.memoryUsage}%
              </Typography>
              <Slider
                value={settings.thresholds.memoryUsage}
                onChange={(e, value) => 
                  dispatch(updateThresholds({ memoryUsage: value }))
                }
                aria-labelledby="memory-usage-slider"
                valueLabelDisplay="auto"
                step={5}
                marks
                min={50}
                max={95}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                sx={{ mt: 2 }}
              >
                Save Settings
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}

export default Settings;
