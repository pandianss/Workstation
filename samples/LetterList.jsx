import React from 'react';
import { useData } from '../context/DataContext';

const LetterList = ({ onCreateNew, onSelect }) => {
    const { letters, deleteLetter } = useData();

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 className="page-title">Letters</h1>
                    <p className="text-neutral-500">Manage your correspondence records.</p>
                </div>
                <button className="btn btn-primary" onClick={onCreateNew}>
                    + Create New Letter
                </button>
            </div>

            <div className="card">
                {letters.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                        No letters found. Create your first letter.
                    </div>
                ) : (
                    <div className="table-container">
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Date</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Ref No</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Recipient</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Subject</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151', textAlign: 'right' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {letters.map((letter) => (
                                    <tr
                                        key={letter.id}
                                        style={{ borderBottom: '1px solid #f3f4f6', cursor: 'pointer' }}
                                        onClick={() => onSelect && onSelect(letter)}
                                    >
                                        <td style={{ padding: '0.75rem' }}>
                                            {new Date(letter.date).toLocaleDateString()}
                                        </td>
                                        <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>{letter.refNo}</td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ fontWeight: '500' }}>{letter.recipientName}</div>
                                            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>{letter.recipientDesignation}</div>
                                        </td>
                                        <td style={{ padding: '0.75rem', maxWidth: '300px' }}>
                                            <div style={{
                                                whiteSpace: 'nowrap',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis'
                                            }}>
                                                {letter.scannedPdf && <span style={{ marginRight: '0.5rem', fontSize: '1.2rem' }} title="Has PDF Attachment">📎</span>}
                                                {letter.subject}
                                            </div>
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                                            <button
                                                className="btn btn-outline"
                                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem', color: 'var(--error)', borderColor: 'var(--error)' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (confirm('Are you sure you want to delete this letter?')) {
                                                        deleteLetter(letter.id);
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

export default LetterList;
