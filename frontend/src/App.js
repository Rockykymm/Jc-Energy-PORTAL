import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login'; 
// import Dashboard from './components/Dashboard'; // Uncomment this once you create the Dashboard file

function App() {
  // This uses the variable you set in Vercel settings
  const API_URL = process.env.REACT_APP_API_URL || '';

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Main route points to Login */}
          <Route path="/" element={<Login apiUrl={API_URL} />} />
          
          {/* Redirect any unknown paths back to login */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;