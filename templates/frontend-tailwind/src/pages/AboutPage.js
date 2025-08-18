import React from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

function AboutPage() {
  const technologies = [
    {
      category: 'Frontend',
      items: [
        'React 18',
        'Tailwind CSS v3',
        'Headless UI',
        'Heroicons',
        'React Router v6',
        'Axios for API calls',
      ],
    },
    {
      category: 'Backend',
      items: [
        'FastAPI',
        'SQLAlchemy ORM',
        'Pydantic for validation',
        'Uvicorn ASGI server',
        'PostgreSQL driver',
      ],
    },
    {
      category: 'Database',
      items: [
        'PostgreSQL 15',
        'Database migrations with Alembic',
        'Connection pooling',
      ],
    },
    {
      category: 'DevOps',
      items: [
        'Docker & Docker Compose',
        'Environment configuration',
        'Hot reload in development',
      ],
    },
  ];

  const features = [
    {
      title: 'RESTful API',
      description: 'Well-structured REST APIs with FastAPI\'s automatic OpenAPI documentation',
    },
    {
      title: 'Modern UI Components',
      description: 'Beautiful Tailwind CSS styling with Headless UI components for accessibility',
    },
    {
      title: 'Database ORM',
      description: 'SQLAlchemy ORM for easy database operations and migrations',
    },
    {
      title: 'Docker Support',
      description: 'Complete Docker Compose setup for easy development and deployment',
    },
    {
      title: 'CRUD Examples',
      description: 'Complete examples for Create, Read, Update, and Delete operations',
    },
    {
      title: 'Responsive Design',
      description: 'Mobile-first responsive design using Tailwind CSS utilities',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          About This Application
        </h1>
      </div>

      <div className="card p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Full-Stack Application Template
        </h2>
        <div className="prose max-w-none text-gray-600">
          <p className="mb-4">
            This is a modern full-stack application template designed to help you quickly
            start building web applications. It includes all the essential components and
            best practices for developing scalable and maintainable applications.
          </p>
          <p>
            The template features a React frontend with Tailwind CSS for beautiful, responsive
            styling, a FastAPI backend that provides high-performance REST APIs with automatic
            documentation, and a PostgreSQL database for reliable data storage.
          </p>
        </div>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Technology Stack</h2>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {technologies.map((tech) => (
          <div key={tech.category} className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {tech.category}
            </h3>
            <ul className="space-y-2">
              {tech.items.map((item) => (
                <li key={item} className="flex items-center space-x-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="text-gray-600">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="card p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature) => (
            <div key={feature.title} className="flex items-start space-x-3">
              <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AboutPage;