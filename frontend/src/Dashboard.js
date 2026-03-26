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

  // --- 3. BUSINESS CALCULATIONS (Updated for True Meter Logic) ---
  
  // NEW: Calculate revenue for just the selected pump
  const calculateSinglePumpRevenue = (fuelType) => {
    const pump = pumps.find(p => p.fuel_type === fuelType);
    if (!pump) return 0;
    const closing = parseFloat(allReadings[fuelType].meter || 0);
    const opening = parseFloat(pump.last_meter_reading || 0);
    // Logic: Revenue is strictly the difference in meter readings
    return closing > opening ? closing - opening : 0;
  };

  const calculateTotalExpected = () => {
    let total = 0;
    pumps.forEach(p => {
      if (p.is_active === true) {
        total += calculateSinglePumpRevenue(p.fuel_type);
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
      return allReadings[p.fuel_type].meter !== '';
    });

  // ADDED: Logic to aggregate History into Daily Reports
  const getDailySummary = () => {
    const summary = {};
    history.forEach(log => {
      const date = new Date(log.created_at).toLocaleDateString();
      if (!summary[date]) {
        summary[date] = { date, totalExpected: 0, totalCash: 0, totalTill: 0, totalDiff: 0 };
      }
      
      const isDuplicateShift = history.find(h => h.created_at === log.created_at && h.id < log.id);
      
      summary[date].totalExpected += (log.expected_total || 0);
      if (!isDuplicateShift) {
        summary[date].totalCash += (log.actual_cash || 0);
        summary[date].totalTill += (log.actual_till || 0);
        summary[date].totalDiff += (log.difference || 0);
      }
    });
    return Object.values(summary);
  };

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
  
    // 1. Major Total is the combined expected revenue calculated above
    const majorTotal = parseFloat(expectedRevenue);
  
    // 2. Create the submission entries for each active pump
    const submissionPromises = pumps.filter(p => p.is_active).map(p => {
      return supabase.from('shift_logs').insert([{
        attendant_name: user.name,
        fuel_type: p.fuel_type,
        pump_reading_start: p.last_meter_reading,
        pump_reading_end: parseFloat(allReadings[p.fuel_type].meter),
        expected_total: calculateSinglePumpRevenue(p.fuel_type), // Sub-total for this specific pump
        combined_shift_total: majorTotal, // The Major total for the entire shift
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

          {/* ADDED: Daily Reports Button */}
          <button 
            className={activeTab === 'reports' ? 'nav-item active' : 'nav-item'} 
            onClick={() => setActiveTab('reports')}
          >
            📊 Daily Reports
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
                    
                    {/* NEW: Individual Pump Revenue Display */}
                    <div className="status-card" style={{ borderLeft: '4px solid var(--station-gold)' }}>
                      <p>{selectedPump.fuel_type} Sales (Expected)</p>
                      <h3 style={{ color: 'var(--station-gold)', margin: '10px 0' }}>
                        KES {calculateSinglePumpRevenue(selectedPump.fuel_type).toLocaleString()}
                      </h3>
                    </div>

                    <div className="status-card" style={{ opacity: 0.6 }}>
                      <p>Last recorded Litres: <strong>{selectedPump.last_litre_reading}</strong></p>
                      <input 
                        type="number" step="0.01" placeholder="Litres (Optional)" 
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

          {/* ADDED: TAB: DAILY REPORTS SUMMARY */}
          {activeTab === 'reports' && (
            <div className="history-card">
              <h2 className="section-title">Daily Performance Summary</h2>
              <table className="history-table" style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Expected Revenue</th>
                    <th>Actual Cash</th>
                    <th>Actual Till</th>
                    <th>Total Collected</th>
                    <th>Net Variance</th>
                  </tr>
                </thead>
                <tbody>
                  {getDailySummary().map((day, index) => (
                    <tr key={index}>
                      <td><strong>{day.date}</strong></td>
                      <td>KSh {day.totalExpected.toLocaleString()}</td>
                      <td style={{ color: '#4dff4d' }}>KSh {day.totalCash.toLocaleString()}</td>
                      <td style={{ color: '#4db8ff' }}>KSh {day.totalTill.toLocaleString()}</td>
                      <td>KSh {(day.totalCash + day.totalTill).toLocaleString()}</td>
                      <td style={{ color: day.totalDiff < 0 ? '#ff4d4d' : '#4dff4d', fontWeight: 'bold' }}>
                        {day.totalDiff < 0 ? `Short (${day.totalDiff.toFixed(2)})` : `Excess (+${day.totalDiff.toFixed(2)})`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
                    <th>Meter Start → End</th>
                    <th>Pump Sales</th>
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