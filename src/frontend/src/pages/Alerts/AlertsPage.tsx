import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Avatar,
} from '@mui/material';
import {
  Notifications,
  Warning,
  Error,
  Info,
  CheckCircle,
  MoreVert,
  Visibility,
  Archive,
  Delete,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { format } from 'date-fns';
import { alertsAPI } from '../../services/api';
import { Alert } from '../../types/api';

const AlertsPage: React.FC = () => {
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const queryClient = useQueryClient();

  const { data: alerts = { data: [], pagination: { total: 0 } }, isLoading } = useQuery(
    ['alerts', filterSeverity, filterStatus],
    () => alertsAPI.getAll({
      severity: filterSeverity !== 'all' ? [filterSeverity] : undefined,
      status: filterStatus !== 'all' ? [filterStatus] : undefined,
    })
  );

  const acknowledgeMutation = useMutation(
    (alertId: string) => alertsAPI.acknowledge(alertId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts');
      },
    }
  );

  const resolveMutation = useMutation(
    (alertId: string) => alertsAPI.resolve(alertId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts');
      },
    }
  );

  const dismissMutation = useMutation(
    (alertId: string) => alertsAPI.dismiss(alertId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('alerts');
      },
    }
  );

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error color="error" />;
      case 'error':
        return <Error color="error" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'info':
        return <Info color="info" />;
      default:
        return <Info color="action" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'error';
      case 'acknowledged':
        return 'warning';
      case 'resolved':
        return 'success';
      case 'dismissed':
        return 'default';
      default:
        return 'default';
    }
  };

  const handleAcknowledge = (alertId: string) => {
    acknowledgeMutation.mutate(alertId);
  };

  const handleResolve = (alertId: string) => {
    resolveMutation.mutate(alertId);
  };

  const handleDismiss = (alertId: string) => {
    dismissMutation.mutate(alertId);
  };

  const filteredAlerts = alerts.data?.filter((alert: Alert) => {
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false;
    if (filterStatus !== 'all' && alert.status !== filterStatus) return false;
    return true;
  }) || [];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Alerts
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor and manage system alerts and notifications.
        </Typography>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={filterSeverity}
                  label="Severity"
                  onChange={(e) => setFilterSeverity(e.target.value)}
                >
                  <MenuItem value="all">All Severities</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="info">Info</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="acknowledged">Acknowledged</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="dismissed">Dismissed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Alerts List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Alerts ({filteredAlerts.length})
          </Typography>
          
          {filteredAlerts.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Notifications sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                No alerts found
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredAlerts.map((alert: Alert) => (
                <ListItem
                  key={alert.id}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: `${getSeverityColor(alert.severity)}.main` }}>
                      {getSeverityIcon(alert.severity)}
                    </Avatar>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {alert.title}
                        </Typography>
                        <Chip
                          label={alert.severity}
                          size="small"
                          color={getSeverityColor(alert.severity)}
                        />
                        <Chip
                          label={alert.status}
                          size="small"
                          color={getStatusColor(alert.status)}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {alert.message}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}
                        </Typography>
                      </Box>
                    }
                  />
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {alert.status === 'active' && (
                      <>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleAcknowledge(alert.id)}
                          disabled={acknowledgeMutation.isLoading}
                        >
                          Acknowledge
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="success"
                          onClick={() => handleResolve(alert.id)}
                          disabled={resolveMutation.isLoading}
                        >
                          Resolve
                        </Button>
                      </>
                    )}
                    <Button
                      size="small"
                      variant="outlined"
                      color="error"
                      onClick={() => handleDismiss(alert.id)}
                      disabled={dismissMutation.isLoading}
                    >
                      Dismiss
                    </Button>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Alert Details Dialog */}
      <Dialog
        open={!!selectedAlert}
        onClose={() => setSelectedAlert(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedAlert && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getSeverityIcon(selectedAlert.severity)}
                {selectedAlert.title}
              </Box>
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedAlert.message}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Created: {format(new Date(selectedAlert.created_at), 'PPP p')}
              </Typography>
              {selectedAlert.acknowledged_at && (
                <Typography variant="body2" color="text.secondary">
                  Acknowledged: {format(new Date(selectedAlert.acknowledged_at), 'PPP p')}
                </Typography>
              )}
              {selectedAlert.resolved_at && (
                <Typography variant="body2" color="text.secondary">
                  Resolved: {format(new Date(selectedAlert.resolved_at), 'PPP p')}
                </Typography>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedAlert(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AlertsPage; 