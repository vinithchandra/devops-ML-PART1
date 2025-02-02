import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'id', headerName: 'Build ID', width: 130 },
  { field: 'probability', headerName: 'Success Probability', width: 180 },
  { field: 'estimatedTime', headerName: 'Estimated Time (min)', width: 180 },
  { field: 'riskLevel', headerName: 'Risk Level', width: 130 },
  { field: 'timestamp', headerName: 'Prediction Time', width: 180 },
];

function BuildPredictions() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [formData, setFormData] = useState({
    repositoryUrl: '',
    branch: '',
    commitHash: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // TODO: Make API call to get predictions
      const response = await fetch('/api/predict/build', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to get predictions');
      }

      const data = await response.json();
      setPredictions([
        ...predictions,
        {
          id: data.buildId,
          probability: `${(data.successProbability * 100).toFixed(1)}%`,
          estimatedTime: data.estimatedTime,
          riskLevel: getRiskLevel(data.successProbability),
          timestamp: new Date().toLocaleString(),
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (probability) => {
    if (probability >= 0.8) return 'Low';
    if (probability >= 0.6) return 'Medium';
    return 'High';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Build Predictions
      </Typography>

      <Grid container spacing={3}>
        {/* Prediction Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Get Build Prediction
            </Typography>
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Repository URL"
                variant="outlined"
                margin="normal"
                value={formData.repositoryUrl}
                onChange={(e) =>
                  setFormData({ ...formData, repositoryUrl: e.target.value })
                }
                required
              />
              <TextField
                fullWidth
                label="Branch"
                variant="outlined"
                margin="normal"
                value={formData.branch}
                onChange={(e) =>
                  setFormData({ ...formData, branch: e.target.value })
                }
                required
              />
              <TextField
                fullWidth
                label="Commit Hash"
                variant="outlined"
                margin="normal"
                value={formData.commitHash}
                onChange={(e) =>
                  setFormData({ ...formData, commitHash: e.target.value })
                }
                required
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Get Prediction'}
              </Button>
            </form>
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Prediction History */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Prediction History
            </Typography>
            <div style={{ height: 400, width: '100%' }}>
              <DataGrid
                rows={predictions}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                disableSelectionOnClick
              />
            </div>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default BuildPredictions;
