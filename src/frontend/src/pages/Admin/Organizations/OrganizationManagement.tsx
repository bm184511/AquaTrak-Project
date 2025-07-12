import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Pagination,
  Tooltip,
  Avatar,
  Menu,
  MenuItem as MenuItemComponent,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { adminAPI } from '../../../services/api';
import toast from 'react-hot-toast';

interface Organization {
  id: string;
  name: string;
  type: string;
  country_code: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  subscription_plan: string;
  is_active: boolean;
  created_at: string;
  user_count: number;
}

interface OrganizationFormData {
  name: string;
  type: string;
  country_code: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  subscription_plan: string;
  is_active: boolean;
}

const OrganizationManagement: React.FC = () => {
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [formData, setFormData] = useState<OrganizationFormData>({
    name: '',
    type: 'private',
    country_code: '',
    address: '',
    contact_email: '',
    contact_phone: '',
    subscription_plan: 'basic',
    is_active: true,
  });

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);

  const queryClient = useQueryClient();

  // Fetch organizations
  const {
    data: orgsData,
    isLoading,
    error,
    refetch,
  } = useQuery(
    ['organizations', page, limit, search, typeFilter, countryFilter],
    () => adminAPI.getOrganizations({
      page,
      limit,
      search: search || undefined,
      type: typeFilter || undefined,
      country: countryFilter || undefined,
    }),
    {
      keepPreviousData: true,
    }
  );

  const handleOpenDialog = (org?: Organization) => {
    if (org) {
      setEditingOrg(org);
      setFormData({
        name: org.name,
        type: org.type,
        country_code: org.country_code,
        address: org.address,
        contact_email: org.contact_email,
        contact_phone: org.contact_phone,
        subscription_plan: org.subscription_plan,
        is_active: org.is_active,
      });
    } else {
      setEditingOrg(null);
      setFormData({
        name: '',
        type: 'private',
        country_code: '',
        address: '',
        contact_email: '',
        contact_phone: '',
        subscription_plan: 'basic',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingOrg(null);
    setFormData({
      name: '',
      type: 'private',
      country_code: '',
      address: '',
      contact_email: '',
      contact_phone: '',
      subscription_plan: 'basic',
      is_active: true,
    });
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, org: Organization) => {
    setAnchorEl(event.currentTarget);
    setSelectedOrg(org);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedOrg(null);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'government':
        return 'primary';
      case 'private':
        return 'success';
      case 'academic':
        return 'info';
      case 'nonprofit':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'premium':
        return 'error';
      case 'professional':
        return 'warning';
      case 'basic':
        return 'success';
      default:
        return 'default';
    }
  };

  const countries = [
    { code: 'IR', name: 'Iran' },
    { code: 'US', name: 'United States' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'DE', name: 'Germany' },
    { code: 'FR', name: 'France' },
    { code: 'CA', name: 'Canada' },
    { code: 'AU', name: 'Australia' },
    { code: 'JP', name: 'Japan' },
    { code: 'CN', name: 'China' },
    { code: 'IN', name: 'India' },
  ];

  const organizationTypes = [
    { value: 'government', label: 'Government' },
    { value: 'private', label: 'Private Company' },
    { value: 'academic', label: 'Academic' },
    { value: 'nonprofit', label: 'Non-Profit' },
    { value: 'research', label: 'Research Institute' },
  ];

  const subscriptionPlans = [
    { value: 'basic', label: 'Basic' },
    { value: 'professional', label: 'Professional' },
    { value: 'premium', label: 'Premium' },
    { value: 'enterprise', label: 'Enterprise' },
  ];

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Failed to load organizations. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Organization Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Organization
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <TextField
              label="Search"
              variant="outlined"
              size="small"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ minWidth: 200 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={typeFilter}
                label="Type"
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {organizationTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Country</InputLabel>
              <Select
                value={countryFilter}
                label="Country"
                onChange={(e) => setCountryFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                {countries.map((country) => (
                  <MenuItem key={country.code} value={country.code}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <IconButton onClick={() => refetch()}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </CardContent>
      </Card>

      {/* Organizations Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Organization</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Users</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              [...Array(5)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={9}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ width: 32, height: 32 }}>
                        <BusinessIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          Loading...
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          loading@example.com
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              orgsData?.data.organizations.map((org: Organization) => (
                <TableRow key={org.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ width: 32, height: 32 }}>
                        {org.name.charAt(0).toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {org.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {org.address}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={organizationTypes.find(t => t.value === org.type)?.label || org.type}
                      size="small"
                      color={getTypeColor(org.type) as any}
                    />
                  </TableCell>
                  <TableCell>
                    {countries.find(c => c.code === org.country_code)?.name || org.country_code}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={subscriptionPlans.find(p => p.value === org.subscription_plan)?.label || org.subscription_plan}
                      size="small"
                      color={getPlanColor(org.subscription_plan) as any}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {org.user_count} users
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={org.is_active ? 'Active' : 'Inactive'}
                      size="small"
                      color={org.is_active ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {org.contact_email}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {org.contact_phone}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {new Date(org.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, org)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {orgsData?.data.pagination && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={orgsData.data.pagination.pages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Box>
      )}

      {/* Organization Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingOrg ? 'Edit Organization' : 'Add New Organization'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Organization Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />

            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <FormControl>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.type}
                  label="Type"
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  {organizationTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <InputLabel>Country</InputLabel>
                <Select
                  value={formData.country_code}
                  label="Country"
                  onChange={(e) => setFormData({ ...formData, country_code: e.target.value })}
                >
                  {countries.map((country) => (
                    <MenuItem key={country.code} value={country.code}>
                      {country.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <TextField
              label="Address"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              multiline
              rows={2}
            />

            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                label="Contact Email"
                type="email"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                required
              />
              <TextField
                label="Contact Phone"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
              />
            </Box>

            <FormControl>
              <InputLabel>Subscription Plan</InputLabel>
              <Select
                value={formData.subscription_plan}
                label="Subscription Plan"
                onChange={(e) => setFormData({ ...formData, subscription_plan: e.target.value })}
              >
                {subscriptionPlans.map((plan) => (
                  <MenuItem key={plan.value} value={plan.value}>
                    {plan.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleCloseDialog}
            variant="contained"
          >
            {editingOrg ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Organization Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItemComponent onClick={() => {
          if (selectedOrg) handleOpenDialog(selectedOrg);
          handleMenuClose();
        }}>
          <EditIcon sx={{ mr: 1 }} />
          Edit
        </MenuItemComponent>
        <MenuItemComponent
          onClick={() => {
            handleMenuClose();
          }}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Delete
        </MenuItemComponent>
      </Menu>
    </Box>
  );
};

export default OrganizationManagement; 