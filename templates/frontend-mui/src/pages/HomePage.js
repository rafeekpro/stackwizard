import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import StorageIcon from '@mui/icons-material/Storage';
import ApiIcon from '@mui/icons-material/Api';
import { checkHealth } from '../services/api';

function HomePage() {
  const [healthStatus, setHealthStatus] = useState({
    api: 'checking',
    database: 'checking',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const apiHealth = await checkHealth();
        const dbHealth = await checkHealth('/db');
        
        setHealthStatus({
          api: apiHealth.status === 'healthy' ? 'healthy' : 'error',
          database: dbHealth.database === 'connected' ? 'healthy' : 'error',
        });
      } catch (error) {
        setHealthStatus({
          api: 'error',
          database: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  const getStatusIcon = (status) => {
    if (status === 'checking') return <CircularProgress size={20} />;
    if (status === 'healthy') return <CheckCircleIcon color="success" />;
    return <ErrorIcon color="error" />;
  };

  const getStatusColor = (status) => {
    if (status === 'checking') return 'default';
    if (status === 'healthy') return 'success';
    return 'error';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Full-Stack Application
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          Built with React, Material UI, FastAPI, and PostgreSQL
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ApiIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">API Status</Typography>
                </Box>
                <Chip
                  icon={getStatusIcon(healthStatus.api)}
                  label={healthStatus.api === 'healthy' ? 'Connected' : 'Disconnected'}
                  color={getStatusColor(healthStatus.api)}
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <StorageIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Database Status</Typography>
                </Box>
                <Chip
                  icon={getStatusIcon(healthStatus.database)}
                  label={healthStatus.database === 'healthy' ? 'Connected' : 'Disconnected'}
                  color={getStatusColor(healthStatus.database)}
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Getting Started
              </Typography>
              <Typography paragraph>
                This is a full-stack application template with the following features:
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <li>
                  <Typography>React frontend with Material UI components</Typography>
                </li>
                <li>
                  <Typography>FastAPI backend with automatic API documentation</Typography>
                </li>
                <li>
                  <Typography>PostgreSQL database with SQLAlchemy ORM</Typography>
                </li>
                <li>
                  <Typography>Docker Compose for easy development</Typography>
                </li>
                <li>
                  <Typography>User and Item management examples</Typography>
                </li>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Alert severity="info">
              Visit <strong>/api/docs</strong> to see the interactive API documentation (Swagger UI)
            </Alert>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}

export default HomePage;