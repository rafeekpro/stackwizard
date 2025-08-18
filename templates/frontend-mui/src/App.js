import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import UsersPage from './pages/UsersPage';
import ItemsPage from './pages/ItemsPage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/items" element={<ItemsPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;