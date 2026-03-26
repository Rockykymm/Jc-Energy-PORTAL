import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

const Dashboard = ({ user, onLogout }) => {
  const [fuelType, setFuelType] = useState('Super');
  const [readings, setReadings] = useState({ opening_meter: 0, opening_litres: 0, price: 0 });
  const [closing, setClosing] = useState({ meter: '', litres: '', cash: '', till: '' });

  // 1. Fetch "Relay" Data from Supabase
  useEffect(() => {
    const fetchRelay = async () => {
      const { data } = await supabase
        .from('pumps')
        .select('*')
        .eq('fuel_type', fuelType)
        .single();
      
      if (data) {
        setReadings({
          opening_meter: data.last_meter_reading,
          opening_litres: data.last_litre_reading,
          price: data.unit_price
        });
      }
    };
    fetchRelay();
  }, [fuelType]);

  // 2. Real-time Calculations
  const meterDiff = closing.meter ? (parseFloat(closing.meter) - readings.opening_meter).toFixed(2) : 0;
  const expectedRevenue = meterDiff; 
  const totalCollected = (parseFloat(closing.cash || 0) + parseFloat(closing.till || 0)).toFixed(2);
  const balance = (totalCollected - expectedRevenue).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { error } = await supabase.from('shift_logs').insert([{
      attendant_name: user.name,
      fuel_type: fuelType,
      meter_reading_start: readings.opening_meter,
      meter_reading_end: parseFloat(closing.meter),
      pump_reading_start: readings.opening_litres,
      pump_reading_end: parseFloat(closing.litres),
      cash: parseFloat(closing.cash),
      till: parseFloat(closing.till),
      expected_total: parseFloat(expectedRevenue),
      total_collected: parseFloat(totalCollected),
      difference: parseFloat(balance)
    }]);

    if (!error) {
      alert("Shift Finalized Successfully!");
      window.location.reload();
    } else {
      alert("Submission Error: " + error.message);
    }
  };

  return (
    <div className="dashboard-container">
      {/* BRANDED HEADER BAR */}
      <header className="station-header">
        <div className="header-left">
          <img src="/logo.png" alt="JC Energy" className="header-logo" />
          <h2 className="portal-title">JC ENERGY PORTAL</h2>
        </div>
        
        <div className="header-right">
          <div className="welcome-badge">
             <span className="user-dot"></span>
             Welcome, <strong>{user.name}</strong>
          </div>
          <button className="logout-btn-small" onClick={onLogout}>Logout</button>
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main className="content-area">
        <div className="handover-card">
          <h2 className="section-title">Shift Handover: {fuelType}</h2>
          
          <div className="pump-selector">
            {['Super', 'Diesel', 'Kerosene'].map(type => (
              <button 
                key={type} 
                onClick={() => setFuelType(type)} 
                className={fuelType === type ? "fuel-btn active" : "fuel-btn"}
              >
                {type}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="entry-form">
            <div className="entry-grid">
              <div className="status-card meter-card">
                <p>Opening Meter: <strong>{readings.opening_meter}</strong></p>
                <input 
                  type="number" step="0.01" placeholder="Enter Closing Meter" 
                  onChange={(e) => setClosing({...closing, meter: e.target.value})} required 
                />
              </div>

              <div className="status-card litres-card">
                <p>Opening Litres: <strong>{readings.opening_litres}</strong></p>
                <input 
                  type="number" step="0.01" placeholder="Enter Closing Litres" 
                  onChange={(e) => setClosing({...closing, litres: e.target.value})} required 
                />
              </div>
            </div>

            <div className="summary-section">
  <h3 className="expected-label">Expected Revenue: <span className="gold-text">KES {expectedRevenue}</span></h3>
  
  {/* This is the new parallel layout wrapper */}
  <div className="cash-inputs">
    <input 
      type="number" 
      placeholder="Actual Cash" 
      onChange={(e) => setClosing({...closing, cash: e.target.value})} 
      required 
    />
    <input 
      type="number" 
      placeholder="Actual Till" 
      onChange={(e) => setClosing({...closing, till: e.target.value})} 
      required 
    />
  </div>
  
  <div className="balance-display">
    <h2 style={{ color: balance < 0 ? '#ff4d4d' : '#4dff4d' }}>
      {balance < 0 ? `Shortage: KES ${Math.abs(balance)}` : `Balance: KES ${balance}`}
    </h2>
  </div>
</div>
            </div>

            <button type="submit" className="finalize-btn">
              Finalize Shift & Submit
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;