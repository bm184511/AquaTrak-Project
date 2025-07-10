import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Configure your account and system preferences.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profile Settings
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    defaultValue="John Doe"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    defaultValue="john.doe@example.com"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Username"
                    defaultValue="johndoe"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Language</InputLabel>
                    <Select defaultValue="en" label="Language">
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Button variant="contained" color="primary">
                    Save Changes
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notification Settings
              </Typography>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Email Notifications"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Push Notifications"
              />
              <FormControlLabel
                control={<Switch />}
                label="SMS Alerts"
              />
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Alert Preferences
              </Typography>
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Critical Alerts"
              />
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Warning Alerts"
              />
              <FormControlLabel
                control={<Switch />}
                label="Info Alerts"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SettingsPage; 