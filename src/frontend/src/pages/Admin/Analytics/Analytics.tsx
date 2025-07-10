import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  Science as ScienceIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { adminApi } from '@/services/api';

interface UsageAnalytics {
  period: string;
  start_date: string;
  end_date: string;
  user_registrations: string[];
  analysis_completions: string[];
  alert_generations: string[];
}

interface ModuleAnalytics {
  module_name: string;
  total_analyses: number;
  completed_analyses: number;
  success_rate: number;
  avg_processing_time: number;
}

const Analytics: React.FC = () => {
  const [usagePeriod, setUsagePeriod] = useState('7d');
  const [modulePeriod, setModulePeriod] = useState('30d');

  // Usage analytics query
  const {
    data: usageData,
    isLoading: usageLoading,
    error: usageError,
  } = useQuery<{ status: string; data: UsageAnalytics }>(
    ['usageAnalytics', usagePeriod],
    () => adminApi.getUsageAnalytics({ period: usagePeriod }),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  // Module analytics query
  const {
    data: moduleData,
    isLoading: moduleLoading,
    error: moduleError,
  } = useQuery<{ status: string; data: ModuleAnalytics[] }>(
    ['moduleAnalytics', modulePeriod],
    () => adminApi.getModuleAnalytics({ period: modulePeriod }),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(2)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(2)}m`;
    return `${(seconds / 3600).toFixed(2)}h`;
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 90) return 'success';
    if (rate >= 70) return 'warning';
    return 'error';
  };

  const getProcessingTimeColor = (time: number) => {
    if (time < 5) return 'success';
    if (time < 30) return 'warning';
    return 'error';
  };

  const periods = [
    { value: '1d', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: '1y', label: 'Last Year' },
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          System Analytics
        </Typography>
      </Box>

      {/* Usage Analytics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Usage Analytics
                </Typography>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Period</InputLabel>
                  <Select
                    value={usagePeriod}
                    label="Period"
                    onChange={(e) => setUsagePeriod(e.target.value)}
                  >
                    {periods.map((period) => (
                      <MenuItem key={period.value} value={period.value}>
                        {period.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              {usageError ? (
                <Alert severity="error">
                  Failed to load usage analytics. Please try again.
                </Alert>
              ) : (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <PeopleIcon color="primary" sx={{ mr: 1 }} />
                          <Typography variant="h6" component="div">
                            User Registrations
                          </Typography>
                        </Box>
                        {usageLoading ? (
                          <Skeleton variant="text" width="60%" />
                        ) : (
                          <Typography variant="h4" component="div">
                            {usageData?.data.user_registrations.length || 0}
                          </Typography>
                        )}
                        <Typography variant="body2" color="text.secondary">
                          New registrations in selected period
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <ScienceIcon color="primary" sx={{ mr: 1 }} />
                          <Typography variant="h6" component="div">
                            Analysis Completions
                          </Typography>
                        </Box>
                        {usageLoading ? (
                          <Skeleton variant="text" width="60%" />
                        ) : (
                          <Typography variant="h4" component="div">
                            {usageData?.data.analysis_completions.length || 0}
                          </Typography>
                        )}
                        <Typography variant="body2" color="text.secondary">
                          Completed analyses in selected period
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                          <Typography variant="h6" component="div">
                            Alert Generations
                          </Typography>
                        </Box>
                        {usageLoading ? (
                          <Skeleton variant="text" width="60%" />
                        ) : (
                          <Typography variant="h4" component="div">
                            {usageData?.data.alert_generations.length || 0}
                          </Typography>
                        )}
                        <Typography variant="body2" color="text.secondary">
                          Generated alerts in selected period
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Module Analytics */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Module Performance Analytics
                </Typography>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Period</InputLabel>
                  <Select
                    value={modulePeriod}
                    label="Period"
                    onChange={(e) => setModulePeriod(e.target.value)}
                  >
                    {periods.map((period) => (
                      <MenuItem key={period.value} value={period.value}>
                        {period.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              {moduleError ? (
                <Alert severity="error">
                  Failed to load module analytics. Please try again.
                </Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Module</TableCell>
                        <TableCell>Total Analyses</TableCell>
                        <TableCell>Completed</TableCell>
                        <TableCell>Success Rate</TableCell>
                        <TableCell>Avg Processing Time</TableCell>
                        <TableCell>Performance</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {moduleLoading ? (
                        [...Array(5)].map((_, i) => (
                          <TableRow key={i}>
                            <TableCell colSpan={6}>
                              <Skeleton variant="text" />
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        moduleData?.data.map((module) => (
                          <TableRow key={module.module_name}>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                                {module.module_name.replace(/_/g, ' ')}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {module.total_analyses.toLocaleString()}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {module.completed_analyses.toLocaleString()}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={formatPercentage(module.success_rate)}
                                size="small"
                                color={getSuccessRateColor(module.success_rate) as any}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={formatTime(module.avg_processing_time)}
                                size="small"
                                color={getProcessingTimeColor(module.avg_processing_time) as any}
                              />
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={module.success_rate}
                                  color={getSuccessRateColor(module.success_rate) as any}
                                  sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                                />
                                <Typography variant="body2" color="text.secondary" sx={{ minWidth: 40 }}>
                                  {formatPercentage(module.success_rate)}
                                </Typography>
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Summary Statistics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performing Modules
              </Typography>
              {moduleLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} variant="rectangular" height={20} />
                  ))}
                </Box>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {moduleData?.data
                    .sort((a, b) => b.success_rate - a.success_rate)
                    .slice(0, 3)
                    .map((module) => (
                      <Box key={module.module_name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {module.module_name.replace(/_/g, ' ')}
                        </Typography>
                        <Chip
                          label={formatPercentage(module.success_rate)}
                          size="small"
                          color={getSuccessRateColor(module.success_rate) as any}
                        />
                      </Box>
                    ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Fastest Processing Modules
              </Typography>
              {moduleLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} variant="rectangular" height={20} />
                  ))}
                </Box>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {moduleData?.data
                    .sort((a, b) => a.avg_processing_time - b.avg_processing_time)
                    .slice(0, 3)
                    .map((module) => (
                      <Box key={module.module_name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {module.module_name.replace(/_/g, ' ')}
                        </Typography>
                        <Chip
                          label={formatTime(module.avg_processing_time)}
                          size="small"
                          color={getProcessingTimeColor(module.avg_processing_time) as any}
                        />
                      </Box>
                    ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics; 