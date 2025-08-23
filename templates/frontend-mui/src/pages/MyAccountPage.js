import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  AccountCircle,
  Lock,
  Assessment,
  Download,
  Delete,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`account-tabpanel-${index}`}
      aria-labelledby={`account-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function MyAccountPage() {
  const { user, updateUser } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  // Profile form state
  const [profileData, setProfileData] = useState({
    email: '',
    full_name: '',
    username: '',
  });
  
  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  // Statistics state
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (user) {
      setProfileData({
        email: user.email || '',
        full_name: user.full_name || '',
        username: user.username || '',
      });
      fetchUserStats();
    }
  }, [user]);

  const fetchUserStats = async () => {
    try {
      const response = await api.get('/api/v1/users/me/statistics');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      // Set empty stats if request fails
      setStats({
        total_items: 0,
        login_count: 0,
        account_age_days: 0,
        email_verified: false
      });
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setMessage({ type: '', text: '' });
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await api.put('/api/v1/users/me', profileData);
      updateUser(response.data);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to update profile' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await api.post('/api/v1/users/me/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to change password' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportData = async () => {
    try {
      const response = await api.get('/api/v1/users/me/export', {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `user-data-${Date.now()}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setMessage({ type: 'success', text: 'Data exported successfully!' });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Failed to export data' 
      });
    }
  };

  const handleDeactivateAccount = async () => {
    if (!window.confirm('Are you sure you want to deactivate your account? This action cannot be undone.')) {
      return;
    }

    try {
      await api.post('/api/v1/users/me/deactivate');
      setMessage({ type: 'success', text: 'Account deactivated. You will be logged out.' });
      setTimeout(() => {
        window.location.href = '/logout';
      }, 2000);
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Failed to deactivate account' 
      });
    }
  };

  if (!user) {
    return (
      <Container>
        <Typography variant="h6">Please log in to access your account</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="account tabs">
            <Tab icon={<AccountCircle />} label="Profile" />
            <Tab icon={<Lock />} label="Password" />
            <Tab icon={<Assessment />} label="Statistics" />
          </Tabs>
        </Box>

        {message.text && (
          <Alert severity={message.type} sx={{ m: 2 }}>
            {message.text}
          </Alert>
        )}

        {/* Profile Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h5" gutterBottom>
            Profile Information
          </Typography>
          <Box component="form" onSubmit={handleProfileUpdate} sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                  disabled
                  helperText="Email cannot be changed"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={profileData.username}
                  onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={profileData.full_name}
                  onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  Save Changes
                </Button>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h6" gutterBottom>
            Data Management
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportData}
              sx={{ mr: 2 }}
            >
              Export My Data
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDeactivateAccount}
            >
              Deactivate Account
            </Button>
          </Box>
        </TabPanel>

        {/* Password Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h5" gutterBottom>
            Change Password
          </Typography>
          <Box component="form" onSubmit={handlePasswordChange} sx={{ mt: 3, maxWidth: 500 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Current Password"
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="New Password"
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                  required
                  helperText="At least 8 characters"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  startIcon={loading && <CircularProgress size={20} />}
                >
                  Change Password
                </Button>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        {/* Statistics Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h5" gutterBottom>
            Account Statistics
          </Typography>
          
          {stats ? (
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Total Items
                    </Typography>
                    <Typography variant="h4">
                      {stats.total_items || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Login Count
                    </Typography>
                    <Typography variant="h4">
                      {stats.login_count || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Last Login
                    </Typography>
                    <Typography variant="body1">
                      {stats.last_login ? new Date(stats.last_login).toLocaleString() : 'Never'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Account Age
                    </Typography>
                    <Typography variant="h4">
                      {stats.account_age_days || 0} days
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Email Status
                    </Typography>
                    <Typography variant="h6">
                      {stats.email_verified ? '✅ Verified' : '❌ Not Verified'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Account Type
                    </Typography>
                    <Typography variant="h6">
                      {stats.is_superuser ? '👑 Admin' : '👤 Regular User'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Account Created
                    </Typography>
                    <Typography variant="body1">
                      {stats.account_created ? new Date(stats.account_created).toLocaleDateString() : 'Unknown'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Account Status
                    </Typography>
                    <Typography variant="h6">
                      {stats.is_active ? '✅ Active' : '⚠️ Inactive'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              {stats.items_by_category && Object.keys(stats.items_by_category).length > 0 && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Items by Category
                      </Typography>
                      <List>
                        {Object.entries(stats.items_by_category).map(([category, count]) => (
                          <ListItem key={category}>
                            <ListItemText 
                              primary={category}
                              secondary={`${count} items`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              )}
              
              {stats.last_login && (
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">
                    Last login: {new Date(stats.last_login).toLocaleString()}
                  </Typography>
                </Grid>
              )}
            </Grid>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
}

export default MyAccountPage;