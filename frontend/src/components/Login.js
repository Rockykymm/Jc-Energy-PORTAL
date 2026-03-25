import React, { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL,
  process.env.REACT_APP_SUPABASE_ANON_KEY
);

const Login = ({ onLoginSuccess }) => {
  const [workId, setWorkId] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const { data, error } = await supabase
        .from('staff')
        .select('*')
        .eq('work_id', workId)
        .single();

      if (error || !data) {
        setMessage('Invalid Work ID. Please try again.');
      } else {
        setMessage(`Welcome, ${data.full_name}!`);
        onLoginSuccess(data);
      }
    } catch (err) {
      setMessage('Error connecting. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '80px', fontFamily: 'Arial' }}>
      <h1>⛽ JC Energy Portal</h1>
      <p>Advanced Monitoring & Management Interface</p>
      <form onSubmit={handleLogin} style={{ marginTop: '30px' }}>
        <input
          type="text"
          placeholder="Enter Work ID (e.g. 001)"
          value={workId}
          onChange={(e) => setWorkId(e.target.value)}
          required
          style={{ padding: '10px', width: '250px', fontSize: '16px' }}
        /><br/><br/>
        <button 
          type="submit" 
          disabled={loading}
          style={{ padding: '10px 30px', fontSize: '16px', cursor: 'pointer' }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ color: message.includes('Welcome') ? 'green' : 'red', marginTop: '20px' }}>
        {message}
      </p>
    </div>
  );
};

export default Login;