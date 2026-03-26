import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

const Dashboard = ({ user, onLogout }) => {
  // --- 1. STATE MANAGEMENT (Complete & Expanded) ---
  const [activeTab, setActiveTab] = useState('handover'); 
  const [pumps, setPumps] = useState([]); 
  const [selectedPump, setSelectedPump] = useState(null);
  const [history, setHistory] = useState([]);
  
  // Track readings for ALL pumps to ensure accurate combined revenue
  const [allReadings, setAllReadings] = useState({
    Super: { meter: '', litres: '' },
    Diesel: { meter: '', litres: '' },
    Kerosene: { meter: '', litres: '' }
  });

  const [closingFunds, setClosingFunds] = useState({ cash: '', till: '' });

  // --- 2. DATA FETCHING (Supabase Integration) ---
  useEffect(() => {
    const fetchData = async () => {
      // Fetch Pumps - Handles pricing and active status
      const { data: pumpData, error: pumpError } = await supabase.from('pumps').select('*');
      if (pumpData) {
        setPumps(pumpData);
        // Default to the first pump that is actually open
        const firstActive = pumpData.find(p => p.is_active);
        setSelectedPump(firstActive || pumpData[0]);
      }

      // Fetch History - Gets recent shift logs
      const { data: historyData } = await supabase
        .from('shift_logs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(15);
      if (historyData) setHistory(historyData);
    };
    fetchData();
  }, []);

  // --- 3. CALCULATION LOGIC (Preserving your exact formulas) ---
  const calculateTotalExpected = () => {
    let total = 0;
    pumps.forEach(p => {
      if (p.is_active) {
        const currentClosing = parseFloat(allReadings[p.fuel_type].meter || 0);
        // Revenue = (Closing - Opening) * Unit Price
        if (currentClosing > p.last_meter_reading) {
          total += (currentClosing - p.last_meter_reading) * p.unit_price;
        }
      }
    });
    return total.toFixed(2);
  };

  const expectedRevenue = calculateTotalExpected();
  const totalCollected = (parseFloat(closingFunds.cash || 0) + parseFloat(closingFunds.till || 0)).toFixed(2);
  const balance = (totalCollected - expectedRevenue).toFixed(2);

  // Requirement: All active pumps must have readings before submission
  const areReadingsComplete = pumps
    .filter(p => p.is_active)
    .every(p => allReadings[p.fuel_type].meter !== '' && allReadings[p.fuel_type].litres !== '');

  // --- 4. SUBMISSION LOGIC ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Insert a log for every active pump to keep the database synced
    const submissionPromises = pumps.filter(p => p.is_active).map(p => {
      return supabase.from('shift_logs').insert([{
        attendant_name: user.name,
        fuel_type: p.fuel_type,
        meter_reading_start: p.last_meter_reading,
        meter_reading_end: parseFloat(allReadings[p.fuel_type].meter),
        pump_reading_start: p.last_litre_reading,
        pump_reading_end: parseFloat(allReadings[p.fuel_type].litres),
        cash: parseFloat(closingFunds.cash),
        till: parseFloat(closingFunds.till),
        expected_total: parseFloat(expectedRevenue),
        total_collected: parseFloat(totalCollected),
        difference: parseFloat(balance)
      }]);
    });

    const results = await Promise.all(submissionPromises);
    if (!results.some(res => res.error)) {
      alert("Shift Successfully Finalized!");
      window.location.reload();
    } else {
      alert("Error saving data. Please check connection.");
    }
  };

  return (
    <div className="dashboard-wrapper">
      {/* --- SIDEBAR NAVIGATION (Exact Copy from image_2fa622.png) --- */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/logo.png" alt="JC Energy" className="sidebar-logo-img" />
        </div>
        <nav className="sidebar-nav">
          <button 
            className={activeTab === 'handover' ? 'nav-item active' : 'nav-item'} 
            onClick={() => setActiveTab('handover')}
          >
            📂 New Handover
          </button>
          <button 
            className={activeTab === 'history' ? 'nav-item active' : 'nav-item'} 
            onClick={() => setActiveTab('history')}
          >
            📜 Shift History
          </button>
          {/* Management Tab: Only visible to Work ID 001 */}
          {user.workId === '001' && (
            <button 
              className={activeTab === 'management' ? 'nav-item active' : 'nav-item'} 
              onClick={() => setActiveTab('management')}
            >
              ⚙️ Management
            </button>
          )}
        </nav>
        <div className="sidebar-footer">
          <button className="logout-sidebar" onClick={onLogout}>Logout</button>
        </div>
      </aside>

      {/* --- MAIN CONTENT CONTAINER (Exact Copy from image_2f47c6.png) --- */}
      <div className="main-container">
        <header className="station-header">
          <div className="header-left">
            <h2 className="portal-title">JC ENERGY PORTAL</h2>
          </div>
          <div className="header-right">
            <div className="welcome-badge">
                <span className="user-dot"></span>
                Welcome, <strong>{user.name}</strong>
            </div>
          </div>
        </header>

        <main className="content-area">
          
          {/* 1. HANDOVER TAB */}
          {activeTab === 'handover' && (
            <div className="handover-card">
              <h2 className="section-title">Shift Handover: {selectedPump?.fuel_type}</h2>
              
              <div className="pump-selector">
                {pumps.map(p => (
                  <button 
                    key={p.fuel_type} 
                    disabled={!p.is_active}
                    onClick={() => setSelectedPump(p)} 
                    className={`${selectedPump?.fuel_type === p.fuel_type ? "fuel-btn active" : "fuel-btn"} ${!p.is_active ? "pump-closed" : ""}`}
                  >
                    {p.fuel_type}
                  </button>
                ))}
              </div>

              {selectedPump && (
                <div className="active-pump-form">
                  <div className="entry-grid">
                    <div className="status-card">
                      <p>Opening Meter: <strong>{selectedPump.last_meter_reading}</strong></p>
                      <input 
                        type="number" step="0.01" placeholder="Enter Closing Meter" 
                        value={allReadings[selectedPump.fuel_type].meter}
                        onChange={(e) => setAllReadings({
                          ...allReadings, 
                          [selectedPump.fuel_type]: {...allReadings[selectedPump.fuel_type], meter: e.target.value}
                        })} 
                      />
                    </div>

                    <div className="status-card">
                      <p>Opening Litres: <strong>{selectedPump.last_litre_reading}</strong></p>
                      <input 
                        type="number" step="0.01" placeholder="Enter Closing Litres" 
                        value={allReadings[selectedPump.fuel_type].litres}
                        onChange={(e) => setAllReadings({
                          ...allReadings, 
                          [selectedPump.fuel_type]: {...allReadings[selectedPump.fuel_type], litres: e.target.value}
                        })} 
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className={`summary-section ${!areReadingsComplete ? "section-locked" : ""}`}>
                <h3 className="expected-label">Expected Revenue: <span className="gold-text">KES {expectedRevenue}</span></h3>
                
                <div className="cash-inputs">
                  <input 
                    type="number" placeholder="Actual Cash" 
                    onChange={(e) => setClosingFunds({...closingFunds, cash: e.target.value})} 
                  />
                  <input 
                    type="number" placeholder="Actual Till" 
                    onChange={(e) => setClosingFunds({...closingFunds, till: e.target.value})} 
                  />
                </div>
                
                <div className="balance-display">
                  <h2 style={{ color: balance < 0 ? '#ff4d4d' : '#4dff4d' }}>
                    Balance: KES {balance}
                  </h2>
                </div>

                <button 
                  onClick={handleSubmit} 
                  disabled={!areReadingsComplete || !closingFunds.cash} 
                  className="finalize-btn"
                >
                  Finalize Shift & Submit
                </button>
              </div>
            </div>
          )}

          {/* 2. HISTORY TAB */}
          {activeTab === 'history' && (
            <div className="history-card">
              <h2 className="section-title">Shift History</h2>
              <div className="history-table-wrapper">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Attendant</th>
                      <th>Fuel</th>
                      <th>Expected (KES)</th>
                      <th>Collected (KES)</th>
                      <th>Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((log, index) => (
                      <tr key={index}>
                        <td>{new Date(log.created_at).toLocaleDateString()}</td>
                        <td>{log.attendant_name}</td>
                        <td>{log.fuel_type}</td>
                        <td>{log.expected_total}</td>
                        <td>{log.total_collected}</td>
                        <td style={{ color: log.difference < 0 ? '#ff4d4d' : '#4dff4d', fontWeight: 'bold' }}>
                          {log.difference}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 3. MANAGEMENT TAB */}
          {activeTab === 'management' && (
            <div className="management-card">
              <h2 className="section-title">Pump & Price Control</h2>
              <div className="management-list">
                {pumps.map((p) => (
                  <div key={p.id} className="pump-manage-item">
                    <div className="pump-info">
                      <h3>{p.fuel_type}</h3>
                      <p>Current: <strong>KES {p.unit_price}</strong></p>
                    </div>
                    <div className="manage-actions">
                      <button 
                        className={`status-toggle ${p.is_active ? 'active-green' : 'closed-red'}`}
                        onClick={async () => {
                          await supabase.from('pumps').update({ is_active: !p.is_active }).eq('id', p.id);
                          window.location.reload();
                        }}
                      >
                        {p.is_active ? "OPEN" : "CLOSED"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
};

export default Dashboard;