import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch user stats (if endpoint exists)
        // For now, we'll use mock data or basic user info
        setStats({
        totalLogins: 42,
        lastLogin: new Date().toISOString(),
        accountAge: calculateAccountAge(user?.created_at),
        securityScore: 85
      });

      // Mock recent activity
      setRecentActivity([
        { id: 1, action: 'Login', timestamp: new Date().toISOString(), status: 'success' },
        { id: 2, action: 'Profile Updated', timestamp: new Date(Date.now() - 86400000).toISOString(), status: 'success' },
        { id: 3, action: 'Password Changed', timestamp: new Date(Date.now() - 172800000).toISOString(), status: 'success' },
      ]);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  fetchDashboardData();
}, [user]);

  const calculateAccountAge = (createdAt) => {
    if (!createdAt) return '0 days';
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now - created);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return `${diffDays} days`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem',
                mr: 3
              }}
            >
              {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom>
                Welcome back, {user?.full_name || user?.username || 'User'}!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Here's your account overview and recent activity
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* User Info Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Username"
                    secondary={user?.username || 'Not set'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <EmailIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email"
                    secondary={user?.email}
                  />
                  {user?.is_verified && (
                    <Chip
                      icon={<CheckCircleIcon />}
                      label="Verified"
                      color="success"
                      size="small"
                    />
                  )}
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CalendarIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Member Since"
                    secondary={user?.created_at ? formatDate(user.created_at) : 'Unknown'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Account Type"
                    secondary={user?.is_superuser ? 'Administrator' : 'Regular User'}
                  />
                  {user?.is_superuser && (
                    <Chip
                      label="Admin"
                      color="error"
                      size="small"
                    />
                  )}
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Stats Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Statistics
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h3" color="primary">
                      {stats?.totalLogins || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Logins
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="h3" color="primary">
                      {stats?.securityScore || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Security Score
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box textAlign="center" p={2}>
                    <Typography variant="body1">
                      Account Age
                    </Typography>
                    <Typography variant="h5" color="primary">
                      {stats?.accountAge || '0 days'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List>
              {recentActivity.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem>
                    <ListItemIcon>
                      {activity.status === 'success' ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <CancelIcon color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.action}
                      secondary={formatDate(activity.timestamp)}
                    />
                  </ListItem>
                  {index < recentActivity.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  href="/settings"
                >
                  Account Settings
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<SecurityIcon />}
                  href="/security"
                >
                  Security Settings
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<PersonIcon />}
                  href="/profile"
                >
                  Edit Profile
                </Button>
              </Grid>
              {user?.is_superuser && (
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="contained"
                    color="error"
                    href="/admin"
                  >
                    Admin Panel
                  </Button>
                </Grid>
              )}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;