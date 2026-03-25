import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';

function App() {
  const [user, setUser] = useState(null);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={
              user ? (
                <div style={{ textAlign: 'center', marginTop: '80px', fontFamily: 'Arial' }}>
                  <h2>Welcome, {user.full_name}! ⛽</h2>
                  <p>{user.is_admin ? '👑 Admin' : '👷 Attendant'}</p>
                  <p>Dashboard coming soon...</p>
                  <button 
                    onClick={() => setUser(null)}
                    style={{ padding: '10px 20px', marginTop: '20px' }}
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <Login onLoginSuccess={setUser} />
              )
            }
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;