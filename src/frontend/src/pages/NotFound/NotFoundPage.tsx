import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Home, ArrowBack } from '@mui/icons-material';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom color="primary.main">
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          The page you're looking for doesn't exist or has been moved.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBack />}
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
          <Button
            variant="contained"
            startIcon={<Home />}
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default NotFoundPage; 