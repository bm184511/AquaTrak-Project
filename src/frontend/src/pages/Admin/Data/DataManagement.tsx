import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Alert,
  Pagination,
  Tooltip,
  Skeleton,
  Tabs,
  Tab,
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
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Storage as StorageIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { adminApi } from '@/services/api';
import toast from 'react-hot-toast';

interface DataSource {
  id: string;
  name: string;
  type: string;
  url: string;
  status: string;
  last_updated: string;
}

interface FileUpload {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_status: string;
  user: string;
  created_at: string;
}

const DataManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [uploadPage, setUploadPage] = useState(1);
  const [uploadLimit] = useState(20);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadUserId, setUploadUserId] = useState('');

  const queryClient = useQueryClient();

  // Data sources query
  const {
    data: dataSources,
    isLoading: sourcesLoading,
    error: sourcesError,
    refetch: refetchSources,
  } = useQuery<{ status: string; data: DataSource[] }>(
    'dataSources',
    () => adminApi.getDataSources(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // File uploads query
  const {
    data: uploadsData,
    isLoading: uploadsLoading,
    error: uploadsError,
    refetch: refetchUploads,
  } = useQuery(
    ['fileUploads', uploadPage, uploadLimit, uploadStatus, uploadUserId],
    () => adminApi.getFileUploads({
      page: uploadPage,
      limit: uploadLimit,
      status: uploadStatus || undefined,
      user_id: uploadUserId || undefined,
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
      case 'active':
        return 'success';
      case 'inactive':
        return 'default';
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircleIcon color="success" />;
      case 'inactive':
        return <ErrorIcon color="disabled" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <PendingIcon color="warning" />;
      default:
        return <ErrorIcon color="disabled" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileTypeColor = (type: string) => {
    if (type.includes('csv')) return 'success';
    if (type.includes('json')) return 'info';
    if (type.includes('xml')) return 'warning';
    if (type.includes('zip')) return 'error';
    return 'default';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Data Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={() => {
              refetchSources();
              refetchUploads();
            }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Data Sources" />
          <Tab label="File Uploads" />
        </Tabs>
      </Box>

      {/* Data Sources Tab */}
      {tabValue === 0 && (
        <Box>
          {/* Data Sources Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StorageIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Total Sources
                    </Typography>
                  </Box>
                  {sourcesLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {dataSources?.data.length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Active Sources
                    </Typography>
                  </Box>
                  {sourcesLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {dataSources?.data.filter(s => s.status === 'active').length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <ErrorIcon color="error" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Inactive Sources
                    </Typography>
                  </Box>
                  {sourcesLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {dataSources?.data.filter(s => s.status !== 'active').length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Data Sources Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Sources
              </Typography>
              {sourcesError ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Failed to load data sources. Please try again.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>URL</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Last Updated</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sourcesLoading ? (
                        [...Array(5)].map((_, i) => (
                          <TableRow key={i}>
                            <TableCell colSpan={6}>
                              <Skeleton variant="text" />
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        dataSources?.data.map((source) => (
                          <TableRow key={source.id}>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {source.name}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={source.type}
                                size="small"
                                color="primary"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 200 }}>
                                {source.url}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={source.status}
                                size="small"
                                color={getStatusColor(source.status) as any}
                                icon={getStatusIcon(source.status)}
                              />
                            </TableCell>
                            <TableCell>
                              {source.last_updated ? 
                                new Date(source.last_updated).toLocaleString() : 
                                'Never'
                              }
                            </TableCell>
                            <TableCell align="right">
                              <IconButton size="small">
                                <EditIcon />
                              </IconButton>
                              <IconButton size="small" color="error">
                                <DeleteIcon />
                              </IconButton>
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
        </Box>
      )}

      {/* File Uploads Tab */}
      {tabValue === 1 && (
        <Box>
          {/* File Uploads Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CloudUploadIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Total Uploads
                    </Typography>
                  </Box>
                  {uploadsLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {uploadsData?.data.pagination.total || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Completed
                    </Typography>
                  </Box>
                  {uploadsLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {uploadsData?.data.uploads.filter(u => u.upload_status === 'completed').length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PendingIcon color="warning" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Pending
                    </Typography>
                  </Box>
                  {uploadsLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {uploadsData?.data.uploads.filter(u => u.upload_status === 'pending').length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <ErrorIcon color="error" sx={{ mr: 1 }} />
                    <Typography variant="h6" component="div">
                      Failed
                    </Typography>
                  </Box>
                  {uploadsLoading ? (
                    <Skeleton variant="text" width="60%" />
                  ) : (
                    <Typography variant="h4" component="div">
                      {uploadsData?.data.uploads.filter(u => u.upload_status === 'failed').length || 0}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* File Uploads Filters */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={uploadStatus}
                    label="Status"
                    onChange={(e) => setUploadStatus(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="failed">Failed</MenuItem>
                    <MenuItem value="uploading">Uploading</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  label="User ID"
                  variant="outlined"
                  size="small"
                  value={uploadUserId}
                  onChange={(e) => setUploadUserId(e.target.value)}
                  sx={{ minWidth: 150 }}
                />

                <IconButton onClick={() => refetchUploads()}>
                  <RefreshIcon />
                </IconButton>
              </Box>
            </CardContent>
          </Card>

          {/* File Uploads Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                File Uploads
              </Typography>
              {uploadsError ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Failed to load file uploads. Please try again.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Filename</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Size</TableCell>
                        <TableCell>User</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Uploaded</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {uploadsLoading ? (
                        [...Array(5)].map((_, i) => (
                          <TableRow key={i}>
                            <TableCell colSpan={7}>
                              <Skeleton variant="text" />
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        uploadsData?.data.uploads.map((upload) => (
                          <TableRow key={upload.id}>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                {upload.filename}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={upload.file_type}
                                size="small"
                                color={getFileTypeColor(upload.file_type) as any}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {formatBytes(upload.file_size)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {upload.user}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={upload.upload_status}
                                size="small"
                                color={getStatusColor(upload.upload_status) as any}
                                icon={getStatusIcon(upload.upload_status)}
                              />
                            </TableCell>
                            <TableCell>
                              {new Date(upload.created_at).toLocaleString()}
                            </TableCell>
                            <TableCell align="right">
                              <IconButton size="small">
                                <EditIcon />
                              </IconButton>
                              <IconButton size="small" color="error">
                                <DeleteIcon />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {/* Uploads Pagination */}
              {uploadsData?.data.pagination && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={uploadsData.data.pagination.pages}
                    page={uploadPage}
                    onChange={(_, value) => setUploadPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default DataManagement; 