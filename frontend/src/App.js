import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>JC Energy System Portal</h1>
        <p>Advanced Monitoring & Management Interface</p>
      </header>
      <main style={{ padding: '20px' }}>
        <section className="status-card">
          <h2>System Status</h2>
          <p>The system is currently initializing...</p>
          <button onClick={() => alert('Connecting to Python Backend...')}>
            Check Connection
          </button>
        </section>
      </main>
    </div>
  );
}

export default App;