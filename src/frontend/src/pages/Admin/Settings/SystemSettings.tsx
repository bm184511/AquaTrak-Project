import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Notifications as NotificationsIcon,
  Language as LanguageIcon,
  Backup as BackupIcon,
  Restore as RestoreIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';

interface SystemSettings {
  general: {
    site_name: string;
    site_description: string;
    admin_email: string;
    timezone: string;
    date_format: string;
    time_format: string;
  };
  security: {
    session_timeout: number;
    max_login_attempts: number;
    password_min_length: number;
    require_2fa: boolean;
    enable_audit_log: boolean;
    ip_whitelist: string[];
  };
  storage: {
    max_file_size: number;
    allowed_file_types: string[];
    storage_path: string;
    enable_compression: boolean;
    retention_days: number;
  };
  notifications: {
    email_notifications: boolean;
    sms_notifications: boolean;
    webhook_url: string;
    alert_threshold: number;
  };
  integrations: {
    enable_api: boolean;
    api_rate_limit: number;
    webhook_enabled: boolean;
    webhook_url: string;
  };
}

const SystemSettings: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    general: {
      site_name: 'AquaTrak',
      site_description: 'AI-GIS Water Risk Monitoring Platform',
      admin_email: 'admin@aquatrak.com',
      timezone: 'UTC',
      date_format: 'YYYY-MM-DD',
      time_format: 'HH:mm:ss',
    },
    security: {
      session_timeout: 3600,
      max_login_attempts: 5,
      password_min_length: 8,
      require_2fa: false,
      enable_audit_log: true,
      ip_whitelist: [],
    },
    storage: {
      max_file_size: 100,
      allowed_file_types: ['csv', 'json', 'xml', 'zip'],
      storage_path: '/data/uploads',
      enable_compression: true,
      retention_days: 90,
    },
    notifications: {
      email_notifications: true,
      sms_notifications: false,
      webhook_url: '',
      alert_threshold: 10,
    },
    integrations: {
      enable_api: true,
      api_rate_limit: 1000,
      webhook_enabled: false,
      webhook_url: '',
    },
  });

  const [openBackupDialog, setOpenBackupDialog] = useState(false);
  const [openRestoreDialog, setOpenRestoreDialog] = useState(false);
  const [openResetDialog, setOpenResetDialog] = useState(false);

  // Save settings mutation
  const saveSettingsMutation = useMutation(
    (newSettings: SystemSettings) => {
      // In a real implementation, this would call the API
      return Promise.resolve({ status: 'success' });
    },
    {
      onSuccess: () => {
        toast.success('Settings saved successfully');
      },
      onError: () => {
        toast.error('Failed to save settings');
      },
    }
  );

  const handleSaveSettings = () => {
    saveSettingsMutation.mutate(settings);
  };

  const handleResetSettings = () => {
    // Reset to default settings
    setSettings({
      general: {
        site_name: 'AquaTrak',
        site_description: 'AI-GIS Water Risk Monitoring Platform',
        admin_email: 'admin@aquatrak.com',
        timezone: 'UTC',
        date_format: 'YYYY-MM-DD',
        time_format: 'HH:mm:ss',
      },
      security: {
        session_timeout: 3600,
        max_login_attempts: 5,
        password_min_length: 8,
        require_2fa: false,
        enable_audit_log: true,
        ip_whitelist: [],
      },
      storage: {
        max_file_size: 100,
        allowed_file_types: ['csv', 'json', 'xml', 'zip'],
        storage_path: '/data/uploads',
        enable_compression: true,
        retention_days: 90,
      },
      notifications: {
        email_notifications: true,
        sms_notifications: false,
        webhook_url: '',
        alert_threshold: 10,
      },
      integrations: {
        enable_api: true,
        api_rate_limit: 1000,
        webhook_enabled: false,
        webhook_url: '',
      },
    });
    toast.success('Settings reset to defaults');
  };

  const timezones = [
    'UTC',
    'America/New_York',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Australia/Sydney',
  ];

  const dateFormats = [
    'YYYY-MM-DD',
    'MM/DD/YYYY',
    'DD/MM/YYYY',
    'YYYY/MM/DD',
  ];

  const timeFormats = [
    'HH:mm:ss',
    'HH:mm',
    'hh:mm:ss A',
    'hh:mm A',
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          System Settings
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<BackupIcon />}
            onClick={() => setOpenBackupDialog(true)}
          >
            Backup
          </Button>
          <Button
            variant="outlined"
            startIcon={<RestoreIcon />}
            onClick={() => setOpenRestoreDialog(true)}
          >
            Restore
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            disabled={saveSettingsMutation.isLoading}
          >
            Save Settings
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SettingsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  General Settings
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Site Name"
                  value={settings.general.site_name}
                  onChange={(e) => setSettings({
                    ...settings,
                    general: { ...settings.general, site_name: e.target.value }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Site Description"
                  value={settings.general.site_description}
                  onChange={(e) => setSettings({
                    ...settings,
                    general: { ...settings.general, site_description: e.target.value }
                  })}
                  multiline
                  rows={2}
                  fullWidth
                />
                
                <TextField
                  label="Admin Email"
                  type="email"
                  value={settings.general.admin_email}
                  onChange={(e) => setSettings({
                    ...settings,
                    general: { ...settings.general, admin_email: e.target.value }
                  })}
                  fullWidth
                />
                
                <FormControl fullWidth>
                  <InputLabel>Timezone</InputLabel>
                  <Select
                    value={settings.general.timezone}
                    label="Timezone"
                    onChange={(e) => setSettings({
                      ...settings,
                      general: { ...settings.general, timezone: e.target.value }
                    })}
                  >
                    {timezones.map((tz) => (
                      <MenuItem key={tz} value={tz}>
                        {tz}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                  <FormControl>
                    <InputLabel>Date Format</InputLabel>
                    <Select
                      value={settings.general.date_format}
                      label="Date Format"
                      onChange={(e) => setSettings({
                        ...settings,
                        general: { ...settings.general, date_format: e.target.value }
                      })}
                    >
                      {dateFormats.map((format) => (
                        <MenuItem key={format} value={format}>
                          {format}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <FormControl>
                    <InputLabel>Time Format</InputLabel>
                    <Select
                      value={settings.general.time_format}
                      label="Time Format"
                      onChange={(e) => setSettings({
                        ...settings,
                        general: { ...settings.general, time_format: e.target.value }
                      })}
                    >
                      {timeFormats.map((format) => (
                        <MenuItem key={format} value={format}>
                          {format}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Security Settings
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Session Timeout (seconds)"
                  type="number"
                  value={settings.security.session_timeout}
                  onChange={(e) => setSettings({
                    ...settings,
                    security: { ...settings.security, session_timeout: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Max Login Attempts"
                  type="number"
                  value={settings.security.max_login_attempts}
                  onChange={(e) => setSettings({
                    ...settings,
                    security: { ...settings.security, max_login_attempts: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Password Min Length"
                  type="number"
                  value={settings.security.password_min_length}
                  onChange={(e) => setSettings({
                    ...settings,
                    security: { ...settings.security, password_min_length: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.security.require_2fa}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: { ...settings.security, require_2fa: e.target.checked }
                      })}
                    />
                  }
                  label="Require Two-Factor Authentication"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.security.enable_audit_log}
                      onChange={(e) => setSettings({
                        ...settings,
                        security: { ...settings.security, enable_audit_log: e.target.checked }
                      })}
                    />
                  }
                  label="Enable Audit Logging"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Storage Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Storage Settings
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Max File Size (MB)"
                  type="number"
                  value={settings.storage.max_file_size}
                  onChange={(e) => setSettings({
                    ...settings,
                    storage: { ...settings.storage, max_file_size: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Storage Path"
                  value={settings.storage.storage_path}
                  onChange={(e) => setSettings({
                    ...settings,
                    storage: { ...settings.storage, storage_path: e.target.value }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Retention Days"
                  type="number"
                  value={settings.storage.retention_days}
                  onChange={(e) => setSettings({
                    ...settings,
                    storage: { ...settings.storage, retention_days: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.storage.enable_compression}
                      onChange={(e) => setSettings({
                        ...settings,
                        storage: { ...settings.storage, enable_compression: e.target.checked }
                      })}
                    />
                  }
                  label="Enable File Compression"
                />
                
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Allowed File Types
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {settings.storage.allowed_file_types.map((type) => (
                      <Chip key={type} label={type} size="small" />
                    ))}
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Notification Settings
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.email_notifications}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, email_notifications: e.target.checked }
                      })}
                    />
                  }
                  label="Email Notifications"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications.sms_notifications}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, sms_notifications: e.target.checked }
                      })}
                    />
                  }
                  label="SMS Notifications"
                />
                
                <TextField
                  label="Webhook URL"
                  value={settings.notifications.webhook_url}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, webhook_url: e.target.value }
                  })}
                  fullWidth
                />
                
                <TextField
                  label="Alert Threshold"
                  type="number"
                  value={settings.notifications.alert_threshold}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: { ...settings.notifications, alert_threshold: parseInt(e.target.value) }
                  })}
                  fullWidth
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Integration Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <LanguageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Integration Settings
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.integrations.enable_api}
                          onChange={(e) => setSettings({
                            ...settings,
                            integrations: { ...settings.integrations, enable_api: e.target.checked }
                          })}
                        />
                      }
                      label="Enable API Access"
                    />
                    
                    <TextField
                      label="API Rate Limit (requests/hour)"
                      type="number"
                      value={settings.integrations.api_rate_limit}
                      onChange={(e) => setSettings({
                        ...settings,
                        integrations: { ...settings.integrations, api_rate_limit: parseInt(e.target.value) }
                      })}
                      fullWidth
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.integrations.webhook_enabled}
                          onChange={(e) => setSettings({
                            ...settings,
                            integrations: { ...settings.integrations, webhook_enabled: e.target.checked }
                          })}
                        />
                      }
                      label="Enable Webhooks"
                    />
                    
                    <TextField
                      label="Webhook URL"
                      value={settings.integrations.webhook_url}
                      onChange={(e) => setSettings({
                        ...settings,
                        integrations: { ...settings.integrations, webhook_url: e.target.value }
                      })}
                      fullWidth
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Danger Zone */}
      <Card sx={{ mt: 3, border: '1px solid #f44336' }}>
        <CardContent>
          <Typography variant="h6" color="error" gutterBottom>
            Danger Zone
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            These actions are irreversible. Please proceed with caution.
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setOpenResetDialog(true)}
            >
              Reset to Defaults
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Backup Dialog */}
      <Dialog open={openBackupDialog} onClose={() => setOpenBackupDialog(false)}>
        <DialogTitle>Backup Settings</DialogTitle>
        <DialogContent>
          <Typography>
            This will create a backup of all current system settings. The backup file will be downloaded automatically.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBackupDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => {
            // In a real implementation, this would trigger a backup
            toast.success('Settings backup created successfully');
            setOpenBackupDialog(false);
          }}>
            Create Backup
          </Button>
        </DialogActions>
      </Dialog>

      {/* Restore Dialog */}
      <Dialog open={openRestoreDialog} onClose={() => setOpenRestoreDialog(false)}>
        <DialogTitle>Restore Settings</DialogTitle>
        <DialogContent>
          <Typography>
            This will restore system settings from a backup file. Current settings will be overwritten.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenRestoreDialog(false)}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={() => {
            // In a real implementation, this would trigger a restore
            toast.success('Settings restored successfully');
            setOpenRestoreDialog(false);
          }}>
            Restore
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Dialog */}
      <Dialog open={openResetDialog} onClose={() => setOpenResetDialog(false)}>
        <DialogTitle>Reset to Defaults</DialogTitle>
        <DialogContent>
          <Typography>
            This will reset all system settings to their default values. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenResetDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => {
              handleResetSettings();
              setOpenResetDialog(false);
            }}
          >
            Reset Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemSettings; 