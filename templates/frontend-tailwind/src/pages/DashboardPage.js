import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  UserIcon,
  EnvelopeIcon,
  CalendarIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
  XCircleIcon,
  Cog6ToothIcon,
  LockClosedIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline';

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
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 h-20 w-20 rounded-full bg-blue-600 flex items-center justify-center text-white text-3xl font-bold">
              {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
            <div className="ml-6">
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.full_name || user?.username || 'User'}!
              </h1>
              <p className="text-gray-600 mt-1">
                Here's your account overview and recent activity
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* User Info Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Account Information</h2>
            </div>
            <div className="p-6">
              <dl className="space-y-4">
                <div className="flex items-center">
                  <UserIcon className="h-5 w-5 text-blue-600 mr-3" />
                  <dt className="text-sm font-medium text-gray-500 w-24">Username</dt>
                  <dd className="text-sm text-gray-900 flex-1">
                    {user?.username || 'Not set'}
                  </dd>
                </div>
                
                <div className="flex items-center">
                  <EnvelopeIcon className="h-5 w-5 text-blue-600 mr-3" />
                  <dt className="text-sm font-medium text-gray-500 w-24">Email</dt>
                  <dd className="text-sm text-gray-900 flex-1 flex items-center">
                    {user?.email}
                    {user?.is_verified && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        Verified
                      </span>
                    )}
                  </dd>
                </div>
                
                <div className="flex items-center">
                  <CalendarIcon className="h-5 w-5 text-blue-600 mr-3" />
                  <dt className="text-sm font-medium text-gray-500 w-24">Member Since</dt>
                  <dd className="text-sm text-gray-900 flex-1">
                    {user?.created_at ? formatDate(user.created_at) : 'Unknown'}
                  </dd>
                </div>
                
                <div className="flex items-center">
                  <ShieldCheckIcon className="h-5 w-5 text-blue-600 mr-3" />
                  <dt className="text-sm font-medium text-gray-500 w-24">Account Type</dt>
                  <dd className="text-sm text-gray-900 flex-1 flex items-center">
                    {user?.is_superuser ? 'Administrator' : 'Regular User'}
                    {user?.is_superuser && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                        Admin
                      </span>
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Stats Card */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Account Statistics</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">{stats?.totalLogins || 0}</p>
                  <p className="text-sm text-gray-600 mt-1">Total Logins</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">{stats?.securityScore || 0}%</p>
                  <p className="text-sm text-gray-600 mt-1">Security Score</p>
                </div>
                <div className="col-span-2 text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Account Age</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">{stats?.accountAge || '0 days'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center py-3 border-b border-gray-100 last:border-0">
                  <div className="flex-shrink-0 mr-3">
                    {activity.status === 'success' ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircleIcon className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                    <p className="text-sm text-gray-500">{formatDate(activity.timestamp)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <a
                href="/settings"
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Cog6ToothIcon className="h-5 w-5 mr-2" />
                Account Settings
              </a>
              <a
                href="/security"
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <LockClosedIcon className="h-5 w-5 mr-2" />
                Security Settings
              </a>
              <a
                href="/profile"
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <UserCircleIcon className="h-5 w-5 mr-2" />
                Edit Profile
              </a>
              {user?.is_superuser && (
                <a
                  href="/admin"
                  className="flex items-center justify-center px-4 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Admin Panel
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;