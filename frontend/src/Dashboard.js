import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

const Dashboard = ({ user, onLogout }) => {
  // --- 1. STATE MANAGEMENT (Expanded) ---
  const [activeTab, setActiveTab] = useState('handover'); 
  const [pumps, setPumps] = useState([]); 
  const [staff, setStaff] = useState([]); 
  const [selectedPump, setSelectedPump] = useState(null);
  const [history, setHistory] = useState([]);
  
  // Detailed individual readings for all fuel types
  const [allReadings, setAllReadings] = useState({
    Super: { meter: '', litres: '' },
    Diesel: { meter: '', litres: '' },
    Kerosene: { meter: '', litres: '' }
  });

  // Tank level monitoring (Morning Dipstick)
  const [dipstick, setDipstick] = useState({
    Super: '',
    Diesel: '',
    Kerosene: ''
  });

  // Financial tracking state
  const [closingFunds, setClosingFunds] = useState({ 
    cash: '', 
    till: '' 
  });

  // --- 2. DATA FETCHING LOGIC ---
  const fetchData = async () => {
    // Fetching Pump Pricing and Status
    const { data: pumpData, error: pumpError } = await supabase
      .from('pumps')
      .select('*')
      .order('fuel_type', { ascending: true });

    if (pumpData) {
      setPumps(pumpData);
      // Auto-selection logic for UI convenience
      const firstActive = pumpData.find(p => p.is_active === true);
      if (firstActive) {
        setSelectedPump(firstActive);
      } else {
        setSelectedPump(pumpData[0]);
      }
    }

    // Fetching Staff for the Admin Management tab
    const { data: staffData } = await supabase
      .from('staff')
      .select('*');
    if (staffData) {
      setStaff(staffData);
    }

    // Fetching Shift Logs for the History tab
    const { data: historyData } = await supabase
      .from('shift_logs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(40);
    if (historyData) {
      setHistory(historyData);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // --- 3. BUSINESS CALCULATIONS (Fully Expanded) ---
  const calculateTotalExpected = () => {
    let total = 0;
    pumps.forEach(p => {
      if (p.is_active === true) {
        const currentClosing = parseFloat(allReadings[p.fuel_type].meter || 0);
        // Only calculate if the current meter is forward of the last recorded
        if (currentClosing > p.last_meter_reading) {
          const consumption = currentClosing - p.last_meter_reading;
          const revenue = consumption * p.unit_price;
          total = total + revenue;
        }
      }
    });
    return total.toFixed(2);
  };

  const expectedRevenue = calculateTotalExpected();
  const totalCollected = (parseFloat(closingFunds.cash || 0) + parseFloat(closingFunds.till || 0)).toFixed(2);
  const balance = (totalCollected - expectedRevenue).toFixed(2);

  // Requirement: Validate that all OPEN pumps have readings before allowing submission
  const areReadingsComplete = pumps
    .filter(p => p.is_active === true)
    .every(p => {
      return allReadings[p.fuel_type].meter !== '' && allReadings[p.fuel_type].litres !== '';
    });

  // --- 4. DATABASE ACTIONS ---
  const updatePrice = async (id, newPrice) => {
    const { error } = await supabase
      .from('pumps')
      .update({ unit_price: parseFloat(newPrice) })
      .eq('id', id);
    if (!error) fetchData();
  };

  const updateStaffId = async (id, newId) => {
    const { error } = await supabase
      .from('staff')
      .update({ work_id: newId })
      .eq('id', id);
    if (!error) fetchData();
  };

  const togglePumpStatus = async (p) => {
    const { error } = await supabase
      .from('pumps')
      .update({ is_active: !p.is_active })
      .eq('id', p.id);
    if (!error) fetchData();
  };

  const handleDipstickSubmit = async () => {
    const { error } = await supabase
      .from('dipstick_logs')
      .insert([{
        attendant_name: user.name,
        super_mm: parseFloat(dipstick.Super),
        diesel_mm: parseFloat(dipstick.Diesel),
        kerosene_mm: parseFloat(dipstick.Kerosene)
      }]);
    if (!error) {
      alert("Morning Tank Levels Recorded!");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // 1. Calculate the Major Total (Sum of all active pump revenues)
    const majorTotal = pumps
      .filter(p => p.is_active)
      .reduce((sum, p) => sum + parseFloat(expectedRevenue || 0), 0);
  
    // 2. Create the submission entries for each active pump
    const submissionPromises = pumps.filter(p => p.is_active).map(p => {
      return supabase.from('shift_logs').insert([{
        attendant_name: user.name,
        fuel_type: p.fuel_type,
        pump_reading_start: p.last_meter_reading,
        pump_reading_end: parseFloat(allReadings[p.fuel_type].meter),
        expected_total: parseFloat(expectedRevenue), // Sub-total for this pump
        combined_shift_total: majorTotal, // The Major total for the shift
        actual_cash: parseFloat(closingFunds.cash) || 0,
        actual_till: parseFloat(closingFunds.till) || 0,
        total_collected: parseFloat(totalCollected),
        difference: parseFloat(balance)
      }]);
    });
  
    // 3. Execute all inserts and check for errors
    const results = await Promise.all(submissionPromises);
    
    if (!results.some(res => res.error)) {
      alert("Shift Successfully Finalized!");
      window.location.reload();
    } else {
      alert("Error submitting shift. Please check your connection.");
      console.error(results.map(res => res.error).filter(Boolean));
    }
  };

  // --- 5. INTERFACE RENDERING ---
  return (
    <div className="dashboard-wrapper">
      {/* SIDEBAR NAVIGATION SECTION */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/logo.png" alt="JC Energy" className="sidebar-logo-img" />
        </div>
        <nav className="sidebar-nav">
          <button 
            className={activeTab === 'dipstick' ? 'nav-item active' : 'nav-item'} 
            onClick={() => setActiveTab('dipstick')}
          >
            📏 Morning Dipstick
          </button>
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
          {/* Admin Restricted Management Tab */}
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

      <div className="main-container">
        <header className="station-header">
          <h2 className="portal-title">JC ENERGY PORTAL</h2>
          <div className="welcome-badge">
            <span className="user-dot"></span>
            Welcome, <strong>{user.name}</strong>
          </div>
        </header>

        <main className="content-area">
          
          {/* TAB: DIPSTICK MEASUREMENTS */}
          {activeTab === 'dipstick' && (
            <div className="handover-card">
              <h2 className="section-title">Morning Tank Dipstick Readings</h2>
              <div className="entry-grid">
                <div className="status-card">
                  <p>Super (mm)</p>
                  <input type="number" onChange={(e) => setDipstick({...dipstick, Super: e.target.value})} />
                </div>
                <div className="status-card">
                  <p>Diesel (mm)</p>
                  <input type="number" onChange={(e) => setDipstick({...dipstick, Diesel: e.target.value})} />
                </div>
                <div className="status-card">
                  <p>Kerosene (mm)</p>
                  <input type="number" onChange={(e) => setDipstick({...dipstick, Kerosene: e.target.value})} />
                </div>
              </div>
              <button className="finalize-btn" onClick={handleDipstickSubmit}>Save Morning Start</button>
            </div>
          )}

          {/* TAB: NEW SHIFT HANDOVER */}
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
                    {p.fuel_type} {!p.is_active && "(CLOSED)"}
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
                <h3 className="expected-label">Combined Expected Revenue: <span className="gold-text">KES {expectedRevenue}</span></h3>
                
                <div className="cash-inputs">
                  <input 
                    type="number" placeholder="Actual Cash" 
                    disabled={!areReadingsComplete}
                    onChange={(e) => setClosingFunds({...closingFunds, cash: e.target.value})} 
                  />
                  <input 
                    type="number" placeholder="Actual Till" 
                    disabled={!areReadingsComplete}
                    onChange={(e) => setClosingFunds({...closingFunds, till: e.target.value})} 
                  />
                </div>
                
                <div className="balance-display">
                  <h2 style={{ color: parseFloat(balance) < 0 ? '#ff4d4d' : '#4dff4d' }}>
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

          {/* TAB: MANAGEMENT COMMAND CENTER */}
          {activeTab === 'management' && (
            <div className="management-card">
              <h2 className="section-title">Admin Management</h2>
              <div className="management-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                
                <div className="manage-box">
                  <h3>Staff & IDs</h3>
                  <div className="staff-list">
                    {staff.map(s => (
                      <div key={s.id} className="admin-row" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <span>{s.name}</span>
                        <input 
                          type="text" 
                          defaultValue={s.work_id} 
                          onBlur={(e) => updateStaffId(s.id, e.target.value)} 
                          style={{ width: '80px' }}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <div className="manage-box">
                  <h3>Pump Control</h3>
                  {pumps.map(p => (
                    <div key={p.id} className="admin-row" style={{ border: '1px solid #333', padding: '10px', marginBottom: '10px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <strong>{p.fuel_type}</strong>
                        <button 
                          onClick={() => togglePumpStatus(p)} 
                          className={p.is_active ? 'btn-open' : 'btn-closed'}
                        >
                          {p.is_active ? 'OPEN' : 'CLOSED'}
                        </button>
                      </div>
                      <div style={{ marginTop: '10px' }}>
                        <label>Price: </label>
                        <input 
                          type="number" 
                          defaultValue={p.unit_price} 
                          onBlur={(e) => updatePrice(p.id, e.target.value)} 
                          style={{ width: '100px' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB: SHIFT HISTORY LOGS */}
          {activeTab === 'history' && (
            <div className="history-card">
              <h2 className="section-title">Shift History</h2>
              <table className="history-table" style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Attendant</th>
                    <th>Pump</th>
                    <th>Start → End (L)</th>
                    <th>Pump Sub-Total</th>
                    <th>Shift Total (Major)</th>
                    <th>Cash</th>
                    <th>Till</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody className="history-tbody">
                  {history.map((log, index) => {
                    const isFirstInShift = index === 0 || log.created_at !== history[index - 1]?.created_at;
                    const shiftRowCount = history.filter(item => item.created_at === log.created_at).length;

                    let statusText = "Balanced";
                    let statusClass = "balanced-text";
                    if (log.difference < 0) {
                      statusText = `Short (${log.difference})`;
                      statusClass = "shortage-text";
                    } else if (log.difference > 0) {
                      statusText = `Excess (+${log.difference})`;
                      statusClass = "excess-text";
                    }

                    return (
                      <tr key={index}>
                        {isFirstInShift && (
                          <td rowSpan={shiftRowCount} style={{ verticalAlign: 'middle' }}>
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                        )}
                        {isFirstInShift && (
                          <td rowSpan={shiftRowCount} style={{ verticalAlign: 'middle' }}>
                            {log.attendant_name}
                          </td>
                        )}
                        
                        <td style={{ fontWeight: 'bold' }}>{log.fuel_type}</td>
                        <td>{log.pump_reading_start} → {log.pump_reading_end}</td>
                        <td style={{ color: 'var(--station-gold)' }}>KSh {log.expected_total?.toLocaleString()}</td>
                        
                        {isFirstInShift ? (
                          <>
                            <td rowSpan={shiftRowCount} style={{ verticalAlign: 'middle', fontWeight: '800' }}>
                              KSh {log.combined_shift_total?.toLocaleString()}
                            </td>
                            <td rowSpan={shiftRowCount} style={{ verticalAlign: 'middle', color: '#4dff4d' }}>
                              KSh {log.actual_cash?.toLocaleString()}
                            </td>
                            <td rowSpan={shiftRowCount} style={{ verticalAlign: 'middle', color: '#4db8ff' }}>
                              KSh {log.actual_till?.toLocaleString()}
                            </td>
                            <td rowSpan={shiftRowCount} className={statusClass} style={{ verticalAlign: 'middle' }}>
                              <strong>{statusText}</strong>
                            </td>
                          </>
                        ) : null}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

        </main>
      </div>
    </div>
  );
};

export default Dashboard;