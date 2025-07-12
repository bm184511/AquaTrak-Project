import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Button,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Settings,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Error,
  Warning,
  Pause,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { modulesAPI } from '../../services/api';
import { Module } from '../../types/api';

const ModulesPage: React.FC = () => {
  const { data: modules = [], isLoading } = useQuery<Module[]>('modules', modulesAPI.getAll);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle color="success" />;
      case 'inactive':
        return <Pause color="warning" />;
      case 'error':
        return <Error color="error" />;
      case 'maintenance':
        return <Warning color="warning" />;
      default:
        return <Pause color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'warning';
      case 'error':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getModuleIcon = (category: string) => {
    switch (category) {
      case 'iot_monitoring':
        return '📊';
      case 'water_quality':
        return '💧';
      case 'flood_modeling':
        return '🌊';
      case 'groundwater':
        return '🏔️';
      case 'drought_prediction':
        return '🌵';
      case 'urban_planning':
        return '🏙️';
      case 'environmental_health':
        return '🏥';
      case 'data_center':
        return '🖥️';
      case 'agricultural':
        return '🌾';
      case 'transboundary':
        return '🌍';
      case 'dust_storm':
        return '🌪️';
      case 'subsidence':
        return '📉';
      case 'green_space':
        return '🌳';
      default:
        return '🔧';
    }
  };

  if (isLoading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Modules
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Modules
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage and monitor your water risk analysis modules.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {modules.map((module) => (
          <Grid item xs={12} sm={6} md={4} key={module.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h3" sx={{ mr: 1 }}>
                      {getModuleIcon(module.category)}
                    </Typography>
                    <Box>
                      <Typography variant="h6" component="div">
                        {module.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        v{module.version}
                      </Typography>
                    </Box>
                  </Box>
                  {getStatusIcon(module.status)}
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {module.description}
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Chip
                    label={module.status}
                    color={getStatusColor(module.status)}
                    size="small"
                  />
                  <Typography variant="caption" color="text.secondary">
                    Last updated: {new Date(module.last_updated).toLocaleDateString()}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Settings />}
                    fullWidth
                  >
                    Configure
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<TrendingUp />}
                    fullWidth
                  >
                    Monitor
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ModulesPage; 