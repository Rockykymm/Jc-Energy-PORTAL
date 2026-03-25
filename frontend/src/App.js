import React, { useState } from 'react';
import Dashboard from './Dashboard'; // 1. Important: This pulls in your new Dashboard.js file
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  // This function is called when a user successfully enters their Work ID
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
        // --- LOGIN SCREEN ---
        <div className="login-container">
          <div className="login-box">
            <h1><span role="img" aria-label="pump">⛽</span> JC Energy Portal</h1>
            <p>Advanced Monitoring & Management Interface</p>
            
            {/* Simple Test Login - Replace with your Work ID input logic */}
            <input type="text" placeholder="Enter Work ID (e.g. 001)" />
            <button 
              className="btn-primary" 
              onClick={() => handleLogin({ name: 'Peter Kimani', role: 'admin' })}
            >
              Login
            </button>
          </div>
        </div>
      ) : (
        // --- DASHBOARD SCREEN ---
        <>
          <div className="header-nav">
             <span>Welcome, <strong>{user.name}</strong>!</span>
             <button className="btn-logout" onClick={handleLogout}>Logout</button>
          </div>
          
          {/* 2. THE FIX: This replaces the "Coming Soon" text with the actual form */}
          <Dashboard user={user} />
        </>
      )}
    </div>
  );
}

export default App;