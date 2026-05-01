import React from 'react';
import { useData } from '../context/DataContext';

const CircularList = ({ onCreateNew, onSelect }) => {
    const { circulars, deleteCircular } = useData();

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 className="page-title">Circulars</h1>
                    <p className="text-neutral-500">Manage internal circulars and memos.</p>
                </div>
                <button className="btn btn-primary" onClick={onCreateNew}>
                    + Create New Circular
                </button>
            </div>

            <div className="card">
                {circulars.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                        No circulars found. Create your first circular.
                    </div>
                ) : (
                    <div className="table-container">
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Date</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Ref No</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Subject</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151', textAlign: 'right' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {circulars.map((circular) => (
                                    <tr
                                        key={circular.id}
                                        style={{ borderBottom: '1px solid #f3f4f6', cursor: 'pointer' }}
                                        onClick={() => onSelect && onSelect(circular)}
                                    >
                                        <td style={{ padding: '0.75rem' }}>
                                            {circular.issuanceDate
                                                ? new Date(circular.issuanceDate).toLocaleDateString()
                                                : (circular.date ? new Date(circular.date).toLocaleDateString() : 'N/A')
                                            }
                                        </td>
                                        <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>{circular.refNo}</td>
                                        <td style={{ padding: '0.75rem', maxWidth: '300px' }}>
                                            <div style={{
                                                whiteSpace: 'nowrap',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis'
                                            }}>
                                                {circular.scannedPdf && <span style={{ marginRight: '0.5rem' }}>📎</span>}
                                                {circular.subject}
                                            </div>
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                                            <button
                                                className="btn btn-outline"
                                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem', color: 'var(--error)', borderColor: 'var(--error)' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (confirm('Are you sure you want to delete this circular?')) {
                                                        deleteCircular(circular.id);
                                                    }
                                                }}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            <style>{`
                .table-container {
                    overflow-x: auto;
                }
                tr:hover {
                    background-color: #f9fafb;
                }
            `}</style>
        </div>
    );
};

export default CircularList;
