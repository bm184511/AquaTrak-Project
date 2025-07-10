import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
} from '@mui/material';
import {
  MoreVert,
  TrendingUp,
  TrendingDown,
  WaterDrop,
  HealthAndSafety,
  Park,
  Storage,
  Notifications,
  Warning,
  CheckCircle,
  Error,
  Info,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { format } from 'date-fns';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { modulesAPI, alertsAPI, analysisAPI } from '@/services/api';
import { Module, Alert, AnalysisResult } from '@/types/api';

const DashboardPage: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Fetch data
  const { data: modules = [] } = useQuery<Module[]>('modules', modulesAPI.getAll);
  const { data: alerts = { data: [], pagination: { total: 0 } } } = useQuery(
    ['alerts', selectedTimeRange],
    () => alertsAPI.getAll({ date_range: { start: getDateRange(selectedTimeRange).start, end: getDateRange(selectedTimeRange).end } })
  );
  const { data: recentAnalysis = { data: [], pagination: { total: 0 } } } = useQuery(
    ['recent-analysis'],
    () => analysisAPI.getAll({ limit: 5 })
  );

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleTimeRangeChange = (range: string) => {
    setSelectedTimeRange(range);
    handleMenuClose();
  };

  // Mock data for charts
  const consumptionData = [
    { date: '2024-01-01', consumption: 120, target: 100 },
    { date: '2024-01-02', consumption: 95, target: 100 },
    { date: '2024-01-03', consumption: 110, target: 100 },
    { date: '2024-01-04', consumption: 85, target: 100 },
    { date: '2024-01-05', consumption: 130, target: 100 },
    { date: '2024-01-06', consumption: 105, target: 100 },
    { date: '2024-01-07', consumption: 115, target: 100 },
  ];

  const moduleStatusData = [
    { name: 'Active', value: 8, color: '#4caf50' },
    { name: 'Inactive', value: 3, color: '#ff9800' },
    { name: 'Error', value: 2, color: '#f44336' },
  ];

  const alertSeverityData = [
    { name: 'Critical', value: 2, color: '#f44336' },
    { name: 'High', value: 5, color: '#ff9800' },
    { name: 'Medium', value: 8, color: '#2196f3' },
    { name: 'Low', value: 12, color: '#4caf50' },
  ];

  const activeModules = modules.filter(m => m.status === 'active').length;
  const totalModules = modules.length;
  const criticalAlerts = alerts.data?.filter((a: Alert) => a.severity === 'critical').length || 0;
  const pendingAnalysis = recentAnalysis.data?.filter((a: AnalysisResult) => a.status === 'pending' || a.status === 'running').length || 0;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back! Here's an overview of your water monitoring system.
        </Typography>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Active Modules
                  </Typography>
                  <Typography variant="h4" component="div">
                    {activeModules}/{totalModules}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(activeModules / totalModules) * 100}
                    sx={{ mt: 1 }}
                  />
                </Box>
                <WaterDrop sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Critical Alerts
                  </Typography>
                  <Typography variant="h4" component="div" color="error.main">
                    {criticalAlerts}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Requires attention
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 40, color: 'error.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Pending Analysis
                  </Typography>
                  <Typography variant="h4" component="div" color="warning.main">
                    {pendingAnalysis}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    In progress
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    System Health
                  </Typography>
                  <Typography variant="h4" component="div" color="success.main">
                    98%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    All systems operational
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Water Consumption Trend */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Water Consumption Trend</Typography>
                <Box>
                  <IconButton onClick={handleMenuClick}>
                    <MoreVert />
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                  >
                    <MenuItem onClick={() => handleTimeRangeChange('7d')}>Last 7 days</MenuItem>
                    <MenuItem onClick={() => handleTimeRangeChange('30d')}>Last 30 days</MenuItem>
                    <MenuItem onClick={() => handleTimeRangeChange('90d')}>Last 90 days</MenuItem>
                  </Menu>
                </Box>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={consumptionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="consumption" stroke="#1976d2" strokeWidth={2} />
                  <Line type="monotone" dataKey="target" stroke="#ff9800" strokeWidth={2} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Module Status */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Module Status
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={moduleStatusData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {moduleStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity and Alerts */}
      <Grid container spacing={3}>
        {/* Recent Analysis */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Analysis
              </Typography>
              <List>
                {recentAnalysis.data?.slice(0, 5).map((analysis: AnalysisResult) => (
                  <React.Fragment key={analysis.id}>
                    <ListItem>
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: getStatusColor(analysis.status) }}>
                          {getStatusIcon(analysis.status)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={analysis.module_name}
                        secondary={`${analysis.analysis_type} - ${format(new Date(analysis.created_at), 'MMM dd, yyyy HH:mm')}`}
                      />
                      <Chip
                        label={analysis.status}
                        size="small"
                        color={getStatusChipColor(analysis.status)}
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Alerts
              </Typography>
              <List>
                {alerts.data?.slice(0, 5).map((alert: Alert) => (
                  <React.Fragment key={alert.id}>
                    <ListItem>
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: getSeverityColor(alert.severity) }}>
                          {getSeverityIcon(alert.severity)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.title}
                        secondary={`${alert.message} - ${format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}`}
                      />
                      <Chip
                        label={alert.severity}
                        size="small"
                        color={getSeverityChipColor(alert.severity)}
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// Helper functions
function getDateRange(range: string) {
  const now = new Date();
  const start = new Date();
  
  switch (range) {
    case '7d':
      start.setDate(now.getDate() - 7);
      break;
    case '30d':
      start.setDate(now.getDate() - 30);
      break;
    case '90d':
      start.setDate(now.getDate() - 90);
      break;
    default:
      start.setDate(now.getDate() - 7);
  }
  
  return {
    start: start.toISOString(),
    end: now.toISOString(),
  };
}

function getStatusColor(status: string) {
  switch (status) {
    case 'completed':
      return 'success.main';
    case 'running':
      return 'warning.main';
    case 'failed':
      return 'error.main';
    default:
      return 'grey.500';
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed':
      return <CheckCircle />;
    case 'running':
      return <TrendingUp />;
    case 'failed':
      return <Error />;
    default:
      return <Info />;
  }
}

function getStatusChipColor(status: string) {
  switch (status) {
    case 'completed':
      return 'success';
    case 'running':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical':
      return 'error.main';
    case 'high':
      return 'warning.main';
    case 'medium':
      return 'info.main';
    case 'low':
      return 'success.main';
    default:
      return 'grey.500';
  }
}

function getSeverityIcon(severity: string) {
  switch (severity) {
    case 'critical':
      return <Error />;
    case 'high':
      return <Warning />;
    case 'medium':
      return <Info />;
    case 'low':
      return <CheckCircle />;
    default:
      return <Info />;
  }
}

function getSeverityChipColor(severity: string) {
  switch (severity) {
    case 'critical':
      return 'error';
    case 'high':
      return 'warning';
    case 'medium':
      return 'info';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
}

export default DashboardPage; 