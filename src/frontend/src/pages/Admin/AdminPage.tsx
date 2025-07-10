import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  Monitor as MonitorIcon,
  Storage as StorageIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

// Admin Components
import AdminDashboard from './Dashboard/AdminDashboard';
import UserManagement from './Users/UserManagement';
import OrganizationManagement from './Organizations/OrganizationManagement';
import SystemMonitoring from './Monitoring/SystemMonitoring';
import DataManagement from './Data/DataManagement';
import Analytics from './Analytics/Analytics';
import SystemSettings from './Settings/SystemSettings';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `admin-tab-${index}`,
    'aria-controls': `admin-tabpanel-${index}`,
  };
}

const AdminPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const adminTabs = [
    {
      label: 'Dashboard',
      icon: <DashboardIcon />,
      component: <AdminDashboard />,
    },
    {
      label: 'Users',
      icon: <PeopleIcon />,
      component: <UserManagement />,
    },
    {
      label: 'Organizations',
      icon: <BusinessIcon />,
      component: <OrganizationManagement />,
    },
    {
      label: 'System Monitoring',
      icon: <MonitorIcon />,
      component: <SystemMonitoring />,
    },
    {
      label: 'Data Management',
      icon: <StorageIcon />,
      component: <DataManagement />,
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <Analytics />,
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <SystemSettings />,
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Admin Panel
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive system administration and management
        </Typography>
      </Box>

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="admin tabs"
            variant={isMobile ? 'scrollable' : 'fullWidth'}
            scrollButtons={isMobile ? 'auto' : false}
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                textTransform: 'none',
                fontSize: '0.875rem',
                fontWeight: 500,
              },
            }}
          >
            {adminTabs.map((tab, index) => (
              <Tab
                key={index}
                label={tab.label}
                icon={tab.icon}
                iconPosition="start"
                {...a11yProps(index)}
              />
            ))}
          </Tabs>
        </Box>

        {adminTabs.map((tab, index) => (
          <TabPanel key={index} value={tabValue} index={index}>
            {tab.component}
          </TabPanel>
        ))}
      </Paper>
    </Container>
  );
};

export default AdminPage; 