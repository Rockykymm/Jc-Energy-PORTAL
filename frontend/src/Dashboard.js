import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import './App.css';

const Dashboard = ({ user, onLogout, isSidebarOpen }) => {
  const [activeTab, setActiveTab] = useState('handover'); 
  const [pumps, setPumps] = useState([]); 
  const [staff, setStaff] = useState([]); 
  const [selectedPump, setSelectedPump] = useState(null);
  const [history, setHistory] = useState([]);
  const [filterEmployee, setFilterEmployee] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [allReadings, setAllReadings] = useState({
    Super: { meter: '', litres: '' },
    Diesel: { meter: '', litres: '' },
    Kerosene: { meter: '', litres: '' }
  });

  const [dipstick, setDipstick] = useState({
    Super: '',
    Diesel: '',
    Kerosene: ''
  });

  const [closingFunds, setClosingFunds] = useState({ 
    cash: '', 
    till: '' 
  });

  const fetchData = async () => {
    const { data: pumpData } = await supabase
      .from('pumps')
      .select('*')
      .order('fuel_type', { ascending: true });

    if (pumpData) {
      setPumps(pumpData);
      const firstActive = pumpData.find(p => p.is_active === true);
      if (firstActive) {
        setSelectedPump(firstActive);
      } else {
        setSelectedPump(pumpData[0]);
      }
    }

    const { data: staffData } = await supabase
      .from('staff')
      .select('id, full_name, work_id, role')
      .order('full_name', { ascending: true });
  
    if (staffData) {
      setStaff(staffData);
    }

    const { data: historyData } = await supabase
      .from('shift_logs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(60);
    if (historyData) {
      setHistory(historyData);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const calculateSinglePumpRevenue = (fuelType) => {
    const pump = pumps.find(p => p.fuel_type === fuelType);
    if (!pump) return 0;
    const closing = parseFloat(allReadings[fuelType].meter || 0);
    const opening = parseFloat(pump.last_meter_reading || 0);
    return closing > opening ? (closing - opening) : 0;
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

  const areReadingsComplete = pumps
    .filter(p => p.is_active === true)
    .every(p => {
      return allReadings[p.fuel_type].meter !== '';
    });

  const getDailySummary = () => {
    const summary = {};
    history.forEach(log => {
      const dateObj = new Date(log.created_at);
      const logDate = dateObj.toLocaleDateString();
      
      if (!summary[logDate]) {
        summary[logDate] = { 
          date: logDate, 
          totalExpected: 0, 
          totalCash: 0, 
          totalTill: 0, 
          processedShifts: new Set() 
        };
      }

      const hours = dateObj.getHours();
      const minutes = dateObj.getMinutes();
      const shiftId = `${log.attendant_name}-${logDate}-${hours}:${minutes}`;

      if (!summary[logDate].processedShifts.has(shiftId)) {
        summary[logDate].totalExpected += (Number(log.combined_shift_total) || 0);
        summary[logDate].totalCash += (Number(log.actual_cash) || 0);
        summary[logDate].totalTill += (Number(log.actual_till) || 0);
        summary[logDate].processedShifts.add(shiftId);
      }
    });
    return Object.values(summary);
  };

  const updatePrice = async (id, newPrice) => {
    const { error } = await supabase
      .from('pumps')
      .update({ unit_price: parseFloat(newPrice) })
      .eq('id', id);
    if (!error) fetchData();
  };

  const updateStaffMember = async (id, field, value) => {
    const { error } = await supabase
      .from('staff')
      .update({ [field]: value })
      .eq('id', id);
    if (!error) fetchData();
  };

  const addNewStaff = async () => {
    const { error } = await supabase
      .from('staff')
      .insert([{ name: 'New Employee', work_id: '000' }]);
    if (!error) fetchData();
  };

  const removeStaff = async (id) => {
    if(window.confirm("Are you sure you want to remove this employee?")) {
      const { error } = await supabase
        .from('staff')
        .delete()
        .eq('id', id);
      if (!error) fetchData();
    }
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

    const majorTotal = parseFloat(expectedRevenue);
    const activePumps = pumps.filter(p => p.is_active);
    const timestamp = new Date().toISOString();

    try {
      for (const p of activePumps) {
        const closingReading = parseFloat(allReadings[p.fuel_type].meter);
        const recordedLitres = parseFloat(allReadings[p.fuel_type].litres) || 0;

        const { error: logError } = await supabase.from('shift_logs').insert([{
          created_at: timestamp,
          attendant_name: user.name,
          fuel_type: p.fuel_type,
          pump_reading_start: p.last_meter_reading,
          pump_reading_end: closingReading,
          litres_sold: recordedLitres,
          expected_total: calculateSinglePumpRevenue(p.fuel_type),
          combined_shift_total: majorTotal,
          actual_cash: parseFloat(closingFunds.cash) || 0,
          actual_till: parseFloat(closingFunds.till) || 0,
          total_collected: parseFloat(totalCollected),
          difference: parseFloat(balance)
        }]);

        if (logError) throw logError;

        const { error: pumpUpdateError } = await supabase
          .from('pumps')
          .update({ 
            last_meter_reading: closingReading,
            last_litres_reading: recordedLitres
          })
          .eq('fuel_type', p.fuel_type);

        if (pumpUpdateError) throw pumpUpdateError;
      }

      alert("Shift Successfully Finalized!");
      window.location.reload();

    } catch (err) {
      console.error("Submission Error:", err);
      alert(`Error submitting shift: ${err.message || "Please check your connection"}`);
    }
  };

  return (
    <div className="dashboard-wrapper">
      {/* SIDEBAR NAVIGATION SECTION */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : 'collapsed'}`}>
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
            onClick={() => {
              setActiveTab('history');
              setFilterEmployee(null);
              setSearchQuery('');
            }}
          >
            📜 Shift History
          </button>
          <button 
            className={activeTab === 'reports' ? 'nav-item active' : 'nav-item'} 
            onClick={() => setActiveTab('reports')}
          >
            📊 Daily Reports
          </button>
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

      <div className={`main-container ${isSidebarOpen ? '' : 'expanded'}`}>
        <header className="station-header">
          <h2 className="portal-title">JC ENERGY PORTAL</h2>
          <div className="welcome-badge">
            <span className="user-dot"></span>
            Welcome, <strong>{user.name}</strong>
          </div>
        </header>

        <main className="content-area">
          
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
                      <p>Opening Litres: <strong>{selectedPump.last_litres_reading || 0}</strong></p>
                      <input 
                        type="number" 
                        step="0.01" 
                        placeholder="Enter Closing Meter"
                        value={allReadings[selectedPump.fuel_type].meter}
                        onChange={(e) => setAllReadings({
                          ...allReadings,
                          [selectedPump.fuel_type]: { ...allReadings[selectedPump.fuel_type], meter: e.target.value }
                        })}
                      />
                    </div>
                    
                    <div className="status-card" style={{ borderLeft: '4px solid var(--station-gold)' }}>
                      <p>{selectedPump.fuel_type} Sales (Expected)</p>
                      <h3 style={{ color: 'var(--station-gold)', margin: '10px 0' }}>
                        KES {calculateSinglePumpRevenue(selectedPump.fuel_type).toLocaleString()}
                      </h3>
                    </div>

                    <div className="status-card">
                      <p>Litres Sold (Optional)</p>
                      <input 
                        type="number" step="0.01" placeholder="Enter Litres..." 
                        value={allReadings[selectedPump.fuel_type].litres}
                        onChange={(e) => setAllReadings({
                          ...allReadings,
                          [selectedPump.fuel_type]: { 
                            ...allReadings[selectedPump.fuel_type], 
                            litres: e.target.value 
                          }
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
                  {getDailySummary().map((day, index) => {
                    const netVariance = (day.totalCash + day.totalTill) - day.totalExpected;
                    return (
                      <tr key={index}>
                        <td><strong>{day.date}</strong></td>
                        <td>KSh {day.totalExpected.toLocaleString()}</td>
                        <td style={{ color: '#4dff4d' }}>KSh {day.totalCash.toLocaleString()}</td>
                        <td style={{ color: '#4db8ff' }}>KSh {day.totalTill.toLocaleString()}</td>
                        <td>KSh {(day.totalCash + day.totalTill).toLocaleString()}</td>
                        <td style={{ color: netVariance < 0 ? '#ff4d4d' : '#4dff4d', fontWeight: 'bold' }}>
                          {netVariance < 0 ? `Short (${netVariance.toFixed(2)})` : `Excess (+${netVariance.toFixed(2)})`}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'management' && (
            <div className="management-card">
              <h2 className="section-title">Admin Management</h2>
              <div className="management-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                
                <div className="manage-box" style={{ background: '#1a1a1a', padding: '20px', borderRadius: '8px' }}>
                  <h3 style={{ color: 'var(--station-gold)', marginBottom: '15px' }}>Staff Management</h3>
                  <div className="staff-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {staff.map(s => (
                      <div 
                        key={s.id} 
                        className="admin-row clickable" 
                        style={{ borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '15px', cursor: 'pointer' }}
                        onClick={() => {
                           setFilterEmployee(s.name);
                           setActiveTab('history');
                        }}
                      >
                        <div style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
                          <input 
                            type="text" 
                            defaultValue={s.name} 
                            placeholder="Name"
                            onClick={(e) => e.stopPropagation()} 
                            onBlur={(e) => updateStaffMember(s.id, 'name', e.target.value)} 
                            style={{ flex: 2, padding: '5px' }}
                          />
                          <input 
                            type="text" 
                            defaultValue={s.work_id} 
                            placeholder="ID"
                            onClick={(e) => e.stopPropagation()}
                            onBlur={(e) => updateStaffMember(s.id, 'work_id', e.target.value)} 
                            style={{ flex: 1, padding: '5px' }}
                          />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--station-gold)' }}>Click row to audit performance →</span>
                          <button 
                            onClick={(e) => {
                               e.stopPropagation();
                               removeStaff(s.id);
                            }}
                            style={{ background: 'transparent', color: '#ff4d4d', border: 'none', cursor: 'pointer', fontSize: '0.8rem' }}
                          >
                            Remove Employee
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <button 
                    onClick={addNewStaff} 
                    style={{ width: '100%', padding: '10px', background: 'var(--station-gold)', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginTop: '10px' }}
                  >
                    + Add New Employee
                  </button>
                </div>

                <div className="manage-box" style={{ background: '#1a1a1a', padding: '20px', borderRadius: '8px' }}>
                  <h3 style={{ color: 'var(--station-gold)', marginBottom: '15px' }}>Pump Settings</h3>
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

          {activeTab === 'history' && (
            <div className="history-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h2 className="section-title">
                  {filterEmployee ? `Audit Records: ${filterEmployee}` : "Shift History"}
                </h2>
                
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input 
                    type="text" 
                    placeholder="Search name, fuel, or date..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ 
                      padding: '8px 12px', 
                      borderRadius: '4px', 
                      border: '1px solid #333', 
                      background: '#1a1a1a', 
                      color: '#fff',
                      width: '250px'
                    }}
                  />
                  {filterEmployee && (
                    <button 
                      onClick={() => setFilterEmployee(null)}
                      className="clear-filter-btn"
                      style={{ padding: '8px 15px', background: 'var(--station-gold)', color: '#000', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                      Show All Staff
                    </button>
                  )}
                </div>
              </div>
              
              <table className="history-table" style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Attendant</th>
                    <th>Pump</th>
                    <th>Meter Start → End</th>
                    <th>Litres Sold</th>
                    <th>Pump Sales</th>
                    <th>Shift Total (Major)</th>
                    <th>Cash</th>
                    <th>Till</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody className="history-tbody">
                  {history
                    .filter(log => {
                        const matchesUser = user.workId === '001' 
                          ? (!filterEmployee || log.attendant_name === filterEmployee)
                          : log.attendant_name === user.name;
                        
                        const lowerSearch = searchQuery.toLowerCase();
                        const matchesSearch = 
                          log.attendant_name?.toLowerCase().includes(lowerSearch) ||
                          log.fuel_type?.toLowerCase().includes(lowerSearch) ||
                          new Date(log.created_at).toLocaleString().toLowerCase().includes(lowerSearch);

                        return matchesUser && matchesSearch;
                    })
                    .map((log, index, filteredArray) => {
                    const isFirstInShift = index === 0 || log.created_at !== filteredArray[index - 1]?.created_at;
                    const shiftRowCount = filteredArray.filter(item => item.created_at === log.created_at).length;

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
                        <td>{log.litres_sold || '-'}</td>
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
