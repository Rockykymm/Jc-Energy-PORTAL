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
        <div className="login-container">
          <div className="login-box">
            {/* Logo is now small and aligned with the title */}
            <div className="login-header-inline">
               <img src="/logo.png" alt="JC" className="mini-login-logo" />
               <h1 className="login-title">JC ENERGY PORTAL</h1>
            </div>
            <p className="subtitle">Advanced Monitoring & Management Interface</p>
            
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
        /* Logic stays same: passing user and logout function to Dashboard */
        <Dashboard user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;