import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Science,
  Analytics,
  Notifications,
  Settings,
  AccountCircle,
  Logout,
  WaterDrop,
  Waves,
  HealthAndSafety,
  Park,
  Storage,
  Agriculture,
  Public,
  Cloud,
  Terrain,
  Home,
  AdminPanelSettings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser, useAuthStore } from '../../store/authStore';

const drawerWidth = 280;

const menuItems = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
  },
  {
    text: 'Modules',
    icon: <Science />,
    path: '/modules',
  },
  {
    text: 'Analysis',
    icon: <Analytics />,
    path: '/analysis',
  },
  {
    text: 'Alerts',
    icon: <Notifications />,
    path: '/alerts',
  },
  {
    text: 'Settings',
    icon: <Settings />,
    path: '/settings',
  },
];

// Admin menu items (only shown to admin users)
const adminMenuItems = [
  {
    text: 'Admin Panel',
    icon: <AdminPanelSettings />,
    path: '/admin',
  },
];

const moduleItems = [
  { text: 'IoT Water Consumption', icon: <WaterDrop />, path: '/modules/iot' },
  { text: 'Environmental Health', icon: <HealthAndSafety />, path: '/modules/environmental-health' },
  { text: 'Urban Green Space', icon: <Park />, path: '/modules/green-space' },
  { text: 'Urban Water Network', icon: <Storage />, path: '/modules/water-network' },
  { text: 'Agricultural Reservoir', icon: <Agriculture />, path: '/modules/agricultural' },
  { text: 'Transboundary Water', icon: <Public />, path: '/modules/transboundary' },
  { text: 'Data Center Water', icon: <Cloud />, path: '/modules/data-center' },
  { text: 'Dust Storm Analysis', icon: <Terrain />, path: '/modules/dust-storm' },
  { text: 'Urban Flood Modeling', icon: <Waves />, path: '/modules/flood-modeling' },
  { text: 'Groundwater Pollution', icon: <WaterDrop />, path: '/modules/groundwater' },
  { text: 'Drinking Water Quality', icon: <HealthAndSafety />, path: '/modules/water-quality' },
  { text: 'Drought Prediction', icon: <Terrain />, path: '/modules/drought' },
  { text: 'InSAR Subsidence', icon: <Science />, path: '/modules/subsidence' },
];

const Layout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  const navigate = useNavigate();
  const location = useLocation();
  const user = useUser();
  const { logout } = useAuthStore();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleProfileMenuClose();
    await logout();
    navigate('/login');
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const drawer = (
    <Box>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <WaterDrop sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6" color="primary.main" fontWeight="bold">
          AquaTrak
        </Typography>
      </Box>

      <List sx={{ pt: 1 }}>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => handleNavigation(item.path)}
            sx={{
              backgroundColor: isActive(item.path) ? 'primary.light' : 'transparent',
              color: isActive(item.path) ? 'primary.contrastText' : 'inherit',
              '&:hover': {
                backgroundColor: isActive(item.path) ? 'primary.main' : 'action.hover',
              },
              borderRadius: 1,
              mx: 1,
              mb: 0.5,
            }}
          >
            <ListItemIcon
              sx={{
                color: isActive(item.path) ? 'primary.contrastText' : 'inherit',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
        
        {/* Admin menu items */}
        {user?.role === 'admin' && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" sx={{ px: 3, py: 1, color: 'text.secondary' }}>
              Administration
            </Typography>
            {adminMenuItems.map((item) => (
              <ListItem
                key={item.text}
                button
                onClick={() => handleNavigation(item.path)}
                sx={{
                  backgroundColor: isActive(item.path) ? 'error.light' : 'transparent',
                  color: isActive(item.path) ? 'error.contrastText' : 'inherit',
                  '&:hover': {
                    backgroundColor: isActive(item.path) ? 'error.main' : 'action.hover',
                  },
                  borderRadius: 1,
                  mx: 1,
                  mb: 0.5,
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive(item.path) ? 'error.contrastText' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </>
        )}
      </List>

      <Divider sx={{ my: 2 }} />

      <Typography variant="subtitle2" sx={{ px: 3, py: 1, color: 'text.secondary' }}>
        Modules
      </Typography>

      <List>
        {moduleItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => handleNavigation(item.path)}
            sx={{
              backgroundColor: isActive(item.path) ? 'primary.light' : 'transparent',
              color: isActive(item.path) ? 'primary.contrastText' : 'inherit',
              '&:hover': {
                backgroundColor: isActive(item.path) ? 'primary.main' : 'action.hover',
              },
              borderRadius: 1,
              mx: 1,
              mb: 0.5,
              pl: 3,
            }}
          >
            <ListItemIcon
              sx={{
                color: isActive(item.path) ? 'primary.contrastText' : 'inherit',
                minWidth: 36,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              primaryTypographyProps={{ variant: 'body2' }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => isActive(item.path))?.text || 'AquaTrak'}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <Notifications />
              </Badge>
            </IconButton>

            <IconButton
              onClick={handleProfileMenuOpen}
              color="inherit"
              sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        <Outlet />
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onClick={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={() => handleNavigation('/profile')}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => handleNavigation('/settings')}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout; 