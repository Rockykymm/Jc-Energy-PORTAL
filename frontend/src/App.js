import React, { useState } from 'react';
import Dashboard from './Dashboard'; 
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [idInput, setIdInput] = useState(''); // Track what is typed in the ID box

  const handleLogin = () => {
    // If the ID entered is 001, give Admin privileges
    if (idInput === '001') {
      setUser({ 
        name: 'Peter Kimani', 
        role: 'admin', 
        workId: '001' 
      });
    } else {
      // For any other ID, log in as a standard staff member
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
    setIdInput(''); // Reset input on logout
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        <div className="login-container">
          <div className="login-box">
            <div className="login-header-inline">
               <img src="/logo.png" alt="JC" className="mini-login-logo" />
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
        <Dashboard user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;