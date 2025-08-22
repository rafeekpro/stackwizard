import React from 'react';
import { Container, Typography, Button, Box, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

function UnauthorizedPage() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <LockOutlinedIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
          <Typography component="h1" variant="h4" gutterBottom>
            401 - Unauthorized
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            You don't have permission to access this resource. Please log in with appropriate credentials.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              onClick={() => navigate('/login')}
            >
              Go to Login
            </Button>
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
            >
              Go to Home
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default UnauthorizedPage;