import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CodeIcon from '@mui/icons-material/Code';
import StorageIcon from '@mui/icons-material/Storage';
import BrushIcon from '@mui/icons-material/Brush';
import BuildIcon from '@mui/icons-material/Build';

function AboutPage() {
  const technologies = [
    {
      category: 'Frontend',
      icon: <BrushIcon />,
      items: [
        'React 18',
        'Material UI v5',
        'React Router v6',
        'Axios for API calls',
      ],
    },
    {
      category: 'Backend',
      icon: <CodeIcon />,
      items: [
        'FastAPI',
        'SQLAlchemy ORM',
        'Pydantic for validation',
        'Uvicorn ASGI server',
      ],
    },
    {
      category: 'Database',
      icon: <StorageIcon />,
      items: [
        'PostgreSQL 15',
        'Database migrations with Alembic',
        'Connection pooling',
      ],
    },
    {
      category: 'DevOps',
      icon: <BuildIcon />,
      items: [
        'Docker & Docker Compose',
        'Environment configuration',
        'Hot reload in development',
      ],
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          About This Application
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Full-Stack Application Template
          </Typography>
          <Typography paragraph>
            This is a modern full-stack application template designed to help you quickly
            start building web applications. It includes all the essential components and
            best practices for developing scalable and maintainable applications.
          </Typography>
          <Typography paragraph>
            The template features a React frontend with Material UI components for a
            professional and responsive user interface, a FastAPI backend that provides
            high-performance REST APIs with automatic documentation, and a PostgreSQL
            database for reliable data storage.
          </Typography>
        </Paper>

        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Technology Stack
        </Typography>

        {technologies.map((tech, index) => (
          <Paper key={tech.category} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              {tech.icon}
              <Typography variant="h6" sx={{ ml: 1 }}>
                {tech.category}
              </Typography>
            </Box>
            <Divider sx={{ mb: 1 }} />
            <List dense>
              {tech.items.map((item) => (
                <ListItem key={item}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <CheckCircleIcon color="primary" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
          </Paper>
        ))}

        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Key Features
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="success" />
              </ListItemIcon>
              <ListItemText
                primary="RESTful API"
                secondary="Well-structured REST APIs with FastAPI's automatic OpenAPI documentation"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Modern UI Components"
                secondary="Professional Material UI components with responsive design"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Database ORM"
                secondary="SQLAlchemy ORM for easy database operations and migrations"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Docker Support"
                secondary="Complete Docker Compose setup for easy development and deployment"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleIcon color="success" />
              </ListItemIcon>
              <ListItemText
                primary="CRUD Examples"
                secondary="Complete examples for Create, Read, Update, and Delete operations"
              />
            </ListItem>
          </List>
        </Paper>
      </Box>
    </Container>
  );
}

export default AboutPage;