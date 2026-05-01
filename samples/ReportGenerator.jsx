import React, { useState } from 'react';
import { useData } from '../context/DataContext';

const ReportGenerator = () => {
    const { officeNotes, letters, returns, circulars } = useData();
    const [filterType, setFilterType] = useState('all');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    const getAllItems = () => {
        let items = [];
        if (filterType === 'all' || filterType === 'notes') {
            items = [...items, ...officeNotes.map(i => ({ ...i, type: 'Office Note' }))];
        }
        if (filterType === 'all' || filterType === 'letters') {
            items = [...items, ...letters.map(i => ({ ...i, type: 'Letter' }))];
        }
        if (filterType === 'all' || filterType === 'returns') {
            items = [...items, ...returns.map(i => ({ ...i, type: 'Direct Return' }))]; // Mock
        }
        if (filterType === 'all' || filterType === 'circulars') {
            items = [...items, ...circulars.map(i => ({ ...i, type: 'Circular' }))];
        }
        // Filter by date (using issuanceDate or date)
        if (startDate) {
            items = items.filter(i => new Date(i.issuanceDate || i.date) >= new Date(startDate));
        }
        if (endDate) {
            items = items.filter(i => new Date(i.issuanceDate || i.date) <= new Date(endDate));
        }
        return items.sort((a, b) => new Date(b.issuanceDate || b.date) - new Date(a.issuanceDate || a.date));
    };

    const items = getAllItems();

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Generate Reports</h1>
            </div>

            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'end' }}>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <label style={{ fontWeight: 500, display: 'block', marginBottom: '0.5rem' }}>Report Type</label>
                        <select className="input" value={filterType} onChange={e => setFilterType(e.target.value)}>
                            <option value="all">All Activities</option>
                            <option value="notes">Office Notes</option>
                            <option value="letters">Letters</option>
                            <option value="circulars">Circulars</option>
                            <option value="returns">Periodical Returns</option>
                        </select>
                    </div>
                    <div style={{ flex: 1, minWidth: '150px' }}>
                        <label style={{ fontWeight: 500, display: 'block', marginBottom: '0.5rem' }}>From Date</label>
                        <input type="date" className="input" value={startDate} onChange={e => setStartDate(e.target.value)} />
                    </div>
                    <div style={{ flex: 1, minWidth: '150px' }}>
                        <label style={{ fontWeight: 500, display: 'block', marginBottom: '0.5rem' }}>To Date</label>
                        <input type="date" className="input" value={endDate} onChange={e => setEndDate(e.target.value)} />
                    </div>
                    <div>
                        <button className="btn btn-primary" onClick={() => window.print()}>Print Report</button>
                    </div>
                </div>
            </div>

            <div className="report-results">
                <h3 style={{ marginBottom: '1rem' }}>Results ({items.length})</h3>
                {items.length === 0 ? (
                    <p style={{ color: 'gray' }}>No records found for the selected criteria.</p>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Classification</th>
                                    <th>Description/Subject</th>
                                    <th>Ref No / Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map(item => (
                                    <tr key={item.id}>
                                        <td>{new Date(item.issuanceDate || item.date).toLocaleDateString()}</td>
                                        <td><span className={`badge badge-${item.type.replace(' ', '-').toLowerCase()}`}>{item.type}</span></td>
                                        <td>{item.classification || item.letterType || '-'}</td>
                                        <td>{item.subject || item.description || item.recipientName}</td>
                                        <td>{item.refNo || item.recipientAddress || item.returnType}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style>{`
        .table-container {
          background: white;
          border-radius: var(--radius-md);
          border: 1px solid hsl(var(--base-200));
          overflow-x: auto;
        }
        .data-table {
          width: 100%;
          border-collapse: collapse;
          min-width: 600px;
        }
        .data-table th, .data-table td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid hsl(var(--base-200));
        }
        .data-table th {
          background-color: hsl(var(--base-100));
          font-weight: 600;
          color: hsl(var(--neutral));
        }
        .badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 999px;
          font-size: 0.75rem;
          font-weight: 600;
        }
        .badge-office-note { background: hsl(var(--primary) / 0.1); color: hsl(var(--primary)); }
        .badge-letter { background: hsl(var(--secondary) / 0.1); color: hsl(var(--secondary)); }
        .badge-circular { background: #dcfce7; color: #166534; }
        .badge-direct-return { background: hsl(var(--accent) / 0.1); color: hsl(var(--accent-content)); }
      `}</style>
        </div>
    );
};

export default ReportGenerator;
