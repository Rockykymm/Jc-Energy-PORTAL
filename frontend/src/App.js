import React, { useState, useEffect } from 'react'; // Added useEffect here
import Dashboard from './Dashboard'; 
import './App.css';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [idInput, setIdInput] = useState(''); 

  // --- START OF PWA PROGRESS CODE ---
  useEffect(() => {
    // This registers the sw.js file you created in the public folder
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then((registration) => {
            console.log('JC Energy SW registered: ', registration);
          })
          .catch((error) => {
            console.log('SW registration failed: ', error);
          });
      });
    }
  }, []);
  // --- END OF PWA PROGRESS CODE ---

  const handleLogin = () => {
    if (idInput === '001') {
      setUser({ 
        name: 'Peter Kimani', 
        role: 'admin', 
        workId: '001' 
      });
    } else {
      setUser({ 
        name: `Staff Member (${idInput})`, 
        role: 'staff', 
        workId: idInput 
      });
    }
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setIdInput(''); 
  };

 return (
    <div className={`App ${!isSidebarOpen ? 'sidebar-closed' : ''}`}>
      {!isLoggedIn ? (
        /* --- LOGIN SCREEN (Stay as is) --- */
        <div className="login-container">
          <div className="login-box">
            <div className="login-header-inline">
               <img src="/jclogo.png" alt="JC" className="mini-login-logo" />
               <h1 className="login-title">JC ENERGY PORTAL</h1>
            </div>
            <p className="subtitle">Advanced Monitoring & Management Interface</p>
            
            <input 
              type="text" 
              placeholder="Enter Work ID (e.g. 001)" 
              value={idInput}
              onChange={(e) => setIdInput(e.target.value)}
            />
            <button 
              className="btn-primary" 
              onClick={handleLogin}
            >
              LOGIN
            </button>
          </div>
        </div>
      ) : (
        /* --- DASHBOARD WITH TOGGLE ARROW --- */
        <div className="dashboard-wrapper">
          {/* This is your Arrow Button */}
          <button 
            className="sidebar-toggle" 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            {isSidebarOpen ? '◀' : '▶'}
          </button>

          <Dashboard 
            user={user} 
            onLogout={handleLogout} 
            isSidebarOpen={isSidebarOpen} 
          />
        </div>
      )}
    </div>
  );
