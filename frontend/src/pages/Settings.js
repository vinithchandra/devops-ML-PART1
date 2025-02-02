import React, { useState } from 'react';
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
} from '@mui/material';

function Settings() {
  const [settings, setSettings] = useState({
    jenkinsUrl: '',
    jenkinsUser: '',
    jenkinsToken: '',
    enableNotifications: true,
    modelUpdateInterval: '24',
    metricsCollectionInterval: '5',
  });

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (event) => {
    const { name, value, checked } = event.target;
    setSettings(prev => ({
      ...prev,
      [name]: event.target.type === 'checkbox' ? checked : value,
    }));
    setSaved(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // TODO: Implement API call to save settings
      await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setError(null);
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
                value={settings.jenkinsUrl}
                onChange={handleChange}
                helperText="e.g., https://jenkins.example.com"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Jenkins Username"
                name="jenkinsUser"
                value={settings.jenkinsUser}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="password"
                label="Jenkins API Token"
                name="jenkinsToken"
                value={settings.jenkinsToken}
                onChange={handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                System Settings
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Model Update Interval (hours)"
                name="modelUpdateInterval"
                value={settings.modelUpdateInterval}
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
                value={settings.metricsCollectionInterval}
                onChange={handleChange}
                inputProps={{ min: 1, max: 60 }}
                helperText="How often to collect system metrics"
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableNotifications}
                    onChange={handleChange}
                    name="enableNotifications"
                  />
                }
                label="Enable Notifications"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
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
