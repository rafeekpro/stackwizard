import React, { useEffect, useState } from 'react';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
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

  const StatusBadge = ({ status, label }) => {
    const isHealthy = status === 'healthy';
    const isChecking = status === 'checking';
    
    return (
      <div className="flex items-center space-x-2">
        {isChecking ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
        ) : isHealthy ? (
          <CheckCircleIcon className="h-5 w-5 text-green-500" />
        ) : (
          <XCircleIcon className="h-5 w-5 text-red-500" />
        )}
        <span className={`text-sm font-medium ${
          isHealthy ? 'text-green-700' : isChecking ? 'text-blue-700' : 'text-red-700'
        }`}>
          {label}: {isChecking ? 'Checking...' : isHealthy ? 'Connected' : 'Disconnected'}
        </span>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl mb-4">
          Welcome to Full-Stack Application
        </h1>
        <p className="text-xl text-gray-600">
          Built with React, Tailwind CSS, FastAPI, and PostgreSQL
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">API Status</h3>
          </div>
          <StatusBadge status={healthStatus.api} label="Backend API" />
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Database Status</h3>
          </div>
          <StatusBadge status={healthStatus.database} label="PostgreSQL" />
        </div>
      </div>

      <div className="card p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Getting Started</h2>
        <p className="text-gray-600 mb-6">
          This is a full-stack application template with the following features:
        </p>
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">React frontend with Tailwind CSS</span>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">FastAPI backend with auto docs</span>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">PostgreSQL with SQLAlchemy ORM</span>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">Docker Compose setup</span>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">User management examples</span>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mt-1" />
            <span className="text-gray-700">Item catalog with CRUD</span>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              Visit <strong>/api/docs</strong> to see the interactive API documentation (Swagger UI)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;