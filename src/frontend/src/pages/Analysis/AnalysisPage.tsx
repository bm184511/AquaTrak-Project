import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
} from '@mui/material';
import {
  Analytics,
  PlayArrow,
  Stop,
  Refresh,
} from '@mui/icons-material';

const AnalysisPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Run and monitor water risk analysis across different modules.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Analyses
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No analyses have been run yet. Start by selecting a module and running an analysis.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  fullWidth
                >
                  New Analysis
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  fullWidth
                >
                  Refresh Data
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisPage; 