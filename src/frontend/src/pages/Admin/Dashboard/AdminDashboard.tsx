import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  People as PeopleIcon,
  Business as BusinessIcon,
  Analytics as AnalyticsIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { adminAPI } from '../../../services/api';

interface DashboardStats {
  users: {
    total: number;
    active: number;
    new_today: number;
    growth_rate: number;
  };
  organizations: {
    total: number;
    active: number;
  };
  analyses: {
    total: number;
    pending: number;
    completed: number;
    success_rate: number;
  };
  alerts: {
    total: number;
    unread: number;
    critical: number;
  };
  system: {
    status: string;
    uptime: string;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
  };
  modules: Record<string, number>;
  recent_activities: Array<{
    id: string;
    action: string;
    user: string;
    resource: string;
    timestamp: string;
    details: any;
  }>;
}

const AdminDashboard: React.FC = () => {
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const {
    data: dashboardData,
    isLoading,
    error,
    refetch,
  } = useQuery<{ status: string; data: DashboardStats }>(
    'adminDashboard',
    () => adminAPI.getDashboard(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      staleTime: 10000,
    }
  );

  const handleRefresh = () => {
    refetch();
    setLastRefresh(new Date());
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <CheckCircleIcon color="disabled" />;
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Failed to load dashboard data. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          System Overview
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* System Status */}
      {dashboardData && (
        <Alert
          severity={getStatusColor(dashboardData.data.system.status) as any}
          icon={getStatusIcon(dashboardData.data.system.status)}
          sx={{ mb: 3 }}
        >
          System Status: {dashboardData.data.system.status.toUpperCase()} | 
          Uptime: {dashboardData.data.system.uptime}
        </Alert>
      )}

      {/* Main Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Users Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PeopleIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" component="div">
                  Users
                </Typography>
              </Box>
              {isLoading ? (
                <Skeleton variant="text" width="60%" />
              ) : (
                <>
                  <Typography variant="h4" component="div" gutterBottom>
                    {formatNumber(dashboardData?.data.users.total || 0)}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Active: {formatNumber(dashboardData?.data.users.active || 0)}
                    </Typography>
                    <Chip
                      label={`+${dashboardData?.data.users.new_today || 0} today`}
                      size="small"
                      color="success"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {dashboardData?.data.users.growth_rate && (
                      <>
                        {dashboardData.data.users.growth_rate > 0 ? (
                          <TrendingUpIcon color="success" fontSize="small" />
                        ) : (
                          <TrendingDownIcon color="error" fontSize="small" />
                        )}
                        <Typography variant="body2" color="text.secondary">
                          {formatPercentage(Math.abs(dashboardData.data.users.growth_rate))} growth
                        </Typography>
                      </>
                    )}
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Organizations Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BusinessIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" component="div">
                  Organizations
                </Typography>
              </Box>
              {isLoading ? (
                <Skeleton variant="text" width="60%" />
              ) : (
                <>
                  <Typography variant="h4" component="div" gutterBottom>
                    {formatNumber(dashboardData?.data.organizations.total || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active: {formatNumber(dashboardData?.data.organizations.active || 0)}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Analyses Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnalyticsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" component="div">
                  Analyses
                </Typography>
              </Box>
              {isLoading ? (
                <Skeleton variant="text" width="60%" />
              ) : (
                <>
                  <Typography variant="h4" component="div" gutterBottom>
                    {formatNumber(dashboardData?.data.analyses.total || 0)}
                  </Typography>
                  <Box sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Success Rate
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={dashboardData?.data.analyses.success_rate || 0}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {formatPercentage(dashboardData?.data.analyses.success_rate || 0)}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Pending: {formatNumber(dashboardData?.data.analyses.pending || 0)}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts Card */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" component="div">
                  Alerts
                </Typography>
              </Box>
              {isLoading ? (
                <Skeleton variant="text" width="60%" />
              ) : (
                <>
                  <Typography variant="h4" component="div" gutterBottom>
                    {formatNumber(dashboardData?.data.alerts.total || 0)}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                      Unread: {formatNumber(dashboardData?.data.alerts.unread || 0)}
                    </Typography>
                    <Typography variant="body2" color="error">
                      Critical: {formatNumber(dashboardData?.data.alerts.critical || 0)}
                    </Typography>
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Resources */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Resources
              </Typography>
              {isLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Skeleton variant="rectangular" height={20} />
                  <Skeleton variant="rectangular" height={20} />
                  <Skeleton variant="rectangular" height={20} />
                </Box>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">CPU Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(dashboardData?.data.system.cpu_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={dashboardData?.data.system.cpu_usage || 0}
                      color={(dashboardData?.data.system.cpu_usage || 0) > 80 ? 'error' : 'primary'}
                    />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Memory Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(dashboardData?.data.system.memory_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={dashboardData?.data.system.memory_usage || 0}
                      color={(dashboardData?.data.system.memory_usage || 0) > 80 ? 'error' : 'primary'}
                    />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Disk Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(dashboardData?.data.system.disk_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={dashboardData?.data.system.disk_usage || 0}
                      color={(dashboardData?.data.system.disk_usage || 0) > 80 ? 'error' : 'primary'}
                    />
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Module Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Module Data
              </Typography>
              {isLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} variant="rectangular" height={20} />
                  ))}
                </Box>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {Object.entries(dashboardData?.data.modules || {}).slice(0, 5).map(([module, count]) => (
                    <Box key={module} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {module.replace(/_/g, ' ')}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatNumber(count)}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activities
          </Typography>
          {isLoading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {[...Array(5)].map((_, i) => (
                <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Skeleton variant="text" width="40%" />
                  <Skeleton variant="text" width="20%" />
                  <Skeleton variant="text" width="15%" />
                </Box>
              ))}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {dashboardData?.data.recent_activities.slice(0, 10).map((activity) => (
                <Box
                  key={activity.id}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1,
                    px: 2,
                    borderRadius: 1,
                    bgcolor: 'background.default',
                  }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {activity.user}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {activity.action} {activity.resource}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(activity.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AdminDashboard; 