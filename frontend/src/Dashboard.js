import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';

const Dashboard = ({ user }) => {
  const [fuelType, setFuelType] = useState('Super');
  const [readings, setReadings] = useState({ opening_meter: 0, opening_litres: 0, price: 0 });
  const [closing, setClosing] = useState({ meter: '', litres: '', cash: '', till: '' });

  // 1. Fetch "Relay" Data from the 'pumps' table
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
  const expectedRevenue = meterDiff; // Meter Difference = Expected Revenue based on your logic
  const totalCollected = (parseFloat(closing.cash || 0) + parseFloat(closing.till || 0)).toFixed(2);
  const balance = (totalCollected - expectedRevenue).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Aligned with your 'shift_logs' columns: attendant_name, meter_reading_start, meter_reading_end, etc.
    const { error } = await supabase.from('shift_logs').insert([{
      attendant_name: user.name,
      fuel_type: fuelType,
      meter_reading_start: readings.opening_meter,
      meter_reading_end: parseFloat(closing.meter),
      pump_reading_start: readings.opening_litres, // Opening Litres
      pump_reading_end: parseFloat(closing.litres), // Closing Litres
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
    <div className="dashboard-container" style={{padding: '20px'}}>
      <h2 style={{color: 'var(--electric-yellow)'}}>Shift Handover: {fuelType}</h2>
      
      <div className="pump-selector" style={{marginBottom: '20px'}}>
        {['Super', 'Diesel', 'Kerosene'].map(type => (
          <button 
            key={type} 
            onClick={() => setFuelType(type)} 
            className={fuelType === type ? "btn-primary" : "btn-secondary"}
            style={{marginRight: '10px'}}
          >
            {type}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="status-card">
          <p>Opening Meter: <strong>{readings.opening_meter}</strong></p>
          <input 
            type="number" step="0.01" placeholder="Enter Closing Meter" 
            onChange={(e) => setClosing({...closing, meter: e.target.value})} required 
          />
        </div>

        <div className="status-card" style={{borderLeftColor: 'white'}}>
          <p>Opening Litres: <strong>{readings.opening_litres}</strong></p>
          <input 
            type="number" step="0.01" placeholder="Enter Closing Litres" 
            onChange={(e) => setClosing({...closing, litres: e.target.value})} required 
          />
        </div>

        <div className="summary-section" style={{marginTop: '20px', background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '8px'}}>
          <h3 style={{margin: '0 0 10px 0'}}>Expected (Meter): <span style={{color: 'var(--electric-yellow)'}}>KES {expectedRevenue}</span></h3>
          <div style={{display: 'flex', gap: '10px', marginBottom: '15px'}}>
            <input type="number" placeholder="Actual Cash" onChange={(e) => setClosing({...closing, cash: e.target.value})} required style={{flex: 1}}/>
            <input type="number" placeholder="Actual Till" onChange={(e) => setClosing({...closing, till: e.target.value})} required style={{flex: 1}}/>
          </div>
          
          <h2 style={{margin: 0, color: balance < 0 ? '#ff4d4d' : '#4dff4d'}}>
            {balance < 0 ? `Shortage: KES ${Math.abs(balance)}` : `Balance: KES ${balance}`}
          </h2>
        </div>

        <button type="submit" className="btn-primary" style={{width: '100%', marginTop: '20px', fontSize: '1.1rem', padding: '15px'}}>
          Finalize Shift & Submit
        </button>
      </form>
    </div>
  );
};

export default Dashboard;