import React, { useState } from 'react';
import Dashboard from './Dashboard'; 
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        /* --- BRANDED LOGIN SCREEN --- */
        <div className="login-container">
          <div className="login-box">
            {/* 1. Using your new logo here */}
            <img src="/logo.png" alt="JC Energy Logo" className="splash-logo" />
            <h1>JC ENERGY PORTAL</h1>
            <p className="subtitle">Advanced Monitoring & Management Interface</p>
            
            <input type="text" placeholder="Enter Work ID (e.g. 001)" />
            <button 
              className="btn-primary" 
              onClick={() => handleLogin('Peter Kimani')} // Passing string directly for your dashboard logic
            >
              Login
            </button>
          </div>
        </div>
      ) : (
        /* --- BRANDED DASHBOARD --- */
        /* Note: We removed the extra header here because the Sidebar now handles it */
        <Dashboard user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;