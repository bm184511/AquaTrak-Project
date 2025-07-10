import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Tooltip,
  Skeleton,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { adminApi } from '@/services/api';

interface SystemStatus {
  status: string;
  uptime: string;
  cpu_usage: number;
  memory_usage: number;
  memory_available: number;
  memory_total: number;
  disk_usage: number;
  disk_free: number;
  disk_total: number;
  network_bytes_sent: number;
  network_bytes_recv: number;
  active_connections: number;
}

interface PerformanceStats {
  database: {
    connection_pool_size: number;
    active_connections: number;
    query_count: number;
    avg_query_time: number;
  };
  api: {
    requests_per_hour: number;
    avg_response_time: number;
    error_rate: number;
  };
  modules: Record<string, {
    avg_processing_time: number;
    total_analyses: number;
  }>;
}

interface AuditLog {
  id: string;
  action: string;
  user: string;
  resource: string;
  resource_id: string;
  details: any;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

const SystemMonitoring: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [logPage, setLogPage] = useState(1);
  const [logLimit] = useState(50);
  const [logLevel, setLogLevel] = useState('');
  const [logUserId, setLogUserId] = useState('');
  const [logAction, setLogAction] = useState('');

  // System status query
  const {
    data: systemStatus,
    isLoading: statusLoading,
    error: statusError,
    refetch: refetchStatus,
  } = useQuery<{ status: string; data: SystemStatus }>(
    'systemStatus',
    () => adminApi.getSystemStatus(),
    {
      refetchInterval: 10000, // Refresh every 10 seconds
    }
  );

  // Performance stats query
  const {
    data: performanceStats,
    isLoading: performanceLoading,
    error: performanceError,
    refetch: refetchPerformance,
  } = useQuery<{ status: string; data: PerformanceStats }>(
    'systemPerformance',
    () => adminApi.getSystemPerformance(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // System logs query
  const {
    data: logsData,
    isLoading: logsLoading,
    error: logsError,
    refetch: refetchLogs,
  } = useQuery(
    ['systemLogs', logPage, logLimit, logLevel, logUserId, logAction],
    () => adminApi.getSystemLogs({
      page: logPage,
      limit: logLimit,
      level: logLevel || undefined,
      user_id: logUserId || undefined,
      action: logAction || undefined,
    }),
    {
      keepPreviousData: true,
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
        return <InfoIcon color="disabled" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getActionColor = (action: string) => {
    if (action.includes('error') || action.includes('delete')) return 'error';
    if (action.includes('warning') || action.includes('update')) return 'warning';
    if (action.includes('create') || action.includes('login')) return 'success';
    return 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          System Monitoring
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Status">
            <IconButton onClick={() => refetchStatus()}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* System Status Alert */}
      {systemStatus && (
        <Alert
          severity={getStatusColor(systemStatus.data.status) as any}
          icon={getStatusIcon(systemStatus.data.status)}
          sx={{ mb: 3 }}
        >
          System Status: {systemStatus.data.status.toUpperCase()} | 
          Uptime: {systemStatus.data.uptime}
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="System Resources" />
          <Tab label="Performance" />
          <Tab label="System Logs" />
        </Tabs>
      </Box>

      {/* System Resources Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* CPU Usage */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  CPU Usage
                </Typography>
                {statusLoading ? (
                  <Skeleton variant="rectangular" height={20} />
                ) : (
                  <>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Current Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(systemStatus?.data.cpu_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={systemStatus?.data.cpu_usage || 0}
                      color={systemStatus?.data.cpu_usage > 80 ? 'error' : 'primary'}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Memory Usage */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Memory Usage
                </Typography>
                {statusLoading ? (
                  <Skeleton variant="rectangular" height={20} />
                ) : (
                  <>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Current Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(systemStatus?.data.memory_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={systemStatus?.data.memory_usage || 0}
                      color={systemStatus?.data.memory_usage > 80 ? 'error' : 'primary'}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Available: {formatBytes(systemStatus?.data.memory_available || 0)} / 
                        Total: {formatBytes(systemStatus?.data.memory_total || 0)}
                      </Typography>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Disk Usage */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Disk Usage
                </Typography>
                {statusLoading ? (
                  <Skeleton variant="rectangular" height={20} />
                ) : (
                  <>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Current Usage</Typography>
                      <Typography variant="body2">
                        {formatPercentage(systemStatus?.data.disk_usage || 0)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={systemStatus?.data.disk_usage || 0}
                      color={systemStatus?.data.disk_usage > 80 ? 'error' : 'primary'}
                      sx={{ height: 10, borderRadius: 5 }}
                    />
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Free: {formatBytes(systemStatus?.data.disk_free || 0)} / 
                        Total: {formatBytes(systemStatus?.data.disk_total || 0)}
                      </Typography>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Network Usage */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Network Usage
                </Typography>
                {statusLoading ? (
                  <Skeleton variant="rectangular" height={20} />
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Bytes Sent
                      </Typography>
                      <Typography variant="body1">
                        {formatBytes(systemStatus?.data.network_bytes_sent || 0)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Bytes Received
                      </Typography>
                      <Typography variant="body1">
                        {formatBytes(systemStatus?.data.network_bytes_recv || 0)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Active Connections
                      </Typography>
                      <Typography variant="body1">
                        {systemStatus?.data.active_connections || 0}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Performance Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {/* Database Performance */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Performance
                </Typography>
                {performanceLoading ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Skeleton variant="rectangular" height={20} />
                    <Skeleton variant="rectangular" height={20} />
                    <Skeleton variant="rectangular" height={20} />
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Connection Pool Size
                      </Typography>
                      <Typography variant="body1">
                        {performanceStats?.data.database.connection_pool_size || 0}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Active Connections
                      </Typography>
                      <Typography variant="body1">
                        {performanceStats?.data.database.active_connections || 0}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Query Count
                      </Typography>
                      <Typography variant="body1">
                        {performanceStats?.data.database.query_count || 0}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Average Query Time
                      </Typography>
                      <Typography variant="body1">
                        {(performanceStats?.data.database.avg_query_time || 0).toFixed(3)}s
                      </Typography>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* API Performance */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  API Performance
                </Typography>
                {performanceLoading ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Skeleton variant="rectangular" height={20} />
                    <Skeleton variant="rectangular" height={20} />
                    <Skeleton variant="rectangular" height={20} />
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Requests per Hour
                      </Typography>
                      <Typography variant="body1">
                        {performanceStats?.data.api.requests_per_hour || 0}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Average Response Time
                      </Typography>
                      <Typography variant="body1">
                        {(performanceStats?.data.api.avg_response_time || 0).toFixed(3)}s
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Error Rate
                      </Typography>
                      <Typography variant="body1">
                        {formatPercentage((performanceStats?.data.api.error_rate || 0) * 100)}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Module Performance */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Module Performance
                </Typography>
                {performanceLoading ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {[...Array(5)].map((_, i) => (
                      <Skeleton key={i} variant="rectangular" height={20} />
                    ))}
                  </Box>
                ) : (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Module</TableCell>
                          <TableCell>Average Processing Time</TableCell>
                          <TableCell>Total Analyses</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(performanceStats?.data.modules || {}).map(([module, stats]) => (
                          <TableRow key={module}>
                            <TableCell sx={{ textTransform: 'capitalize' }}>
                              {module.replace(/_/g, ' ')}
                            </TableCell>
                            <TableCell>
                              {stats.avg_processing_time.toFixed(3)}s
                            </TableCell>
                            <TableCell>
                              {stats.total_analyses}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* System Logs Tab */}
      {tabValue === 2 && (
        <Box>
          {/* Log Filters */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <TextField
                  label="Search"
                  variant="outlined"
                  size="small"
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                  sx={{ minWidth: 200 }}
                />
                
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Level</InputLabel>
                  <Select
                    value={logLevel}
                    label="Level"
                    onChange={(e) => setLogLevel(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="error">Error</MenuItem>
                    <MenuItem value="warning">Warning</MenuItem>
                    <MenuItem value="info">Info</MenuItem>
                    <MenuItem value="debug">Debug</MenuItem>
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Action</InputLabel>
                  <Select
                    value={logAction}
                    label="Action"
                    onChange={(e) => setLogAction(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="login">Login</MenuItem>
                    <MenuItem value="create">Create</MenuItem>
                    <MenuItem value="update">Update</MenuItem>
                    <MenuItem value="delete">Delete</MenuItem>
                  </Select>
                </FormControl>

                <IconButton onClick={() => refetchLogs()}>
                  <RefreshIcon />
                </IconButton>
              </Box>
            </CardContent>
          </Card>

          {/* Logs Table */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logsLoading ? (
                  [...Array(5)].map((_, i) => (
                    <TableRow key={i}>
                      <TableCell colSpan={6}>
                        <Skeleton variant="text" />
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  logsData?.data.logs.map((log: AuditLog) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        {new Date(log.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {log.user}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={log.action}
                          size="small"
                          color={getActionColor(log.action) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {log.resource}
                          {log.resource_id && ` (${log.resource_id})`}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {log.ip_address || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 200 }}>
                          {JSON.stringify(log.details)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Logs Pagination */}
          {logsData?.data.pagination && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={logsData.data.pagination.pages}
                page={logPage}
                onChange={(_, value) => setLogPage(value)}
                color="primary"
              />
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default SystemMonitoring; 