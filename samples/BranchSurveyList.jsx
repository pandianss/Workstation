import React from 'react';
import { useData } from '../context/DataContext';

const BranchSurveyList = ({ onCreateNew, onSelect }) => {
    const { branchSurveys, deleteBranchSurvey } = useData();

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 className="page-title">Branch Opening Survey Reports</h1>
                    <p className="text-neutral-500">Manage survey reports for new branches or location changes.</p>
                </div>
                <button className="btn btn-primary" onClick={onCreateNew}>
                    + Create New Report
                </button>
            </div>

            <div className="card">
                {(!branchSurveys || branchSurveys.length === 0) ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
                        No survey reports found. Create your first report.
                    </div>
                ) : (
                    <div className="table-container">
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Date</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Region</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Proposed Office</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Office Type</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151' }}>Status</th>
                                    <th style={{ padding: '0.75rem', fontWeight: '600', color: '#374151', textAlign: 'right' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {branchSurveys.map((survey) => (
                                    <tr
                                        key={survey.id}
                                        style={{ borderBottom: '1px solid #f3f4f6', cursor: 'pointer' }}
                                        onClick={() => onSelect && onSelect(survey)}
                                    >
                                        <td style={{ padding: '0.75rem' }}>
                                            {survey.date ? new Date(survey.date).toLocaleDateString('en-GB') : 'N/A'}
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>{survey.region || '-'}</td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ fontWeight: '500' }}>{survey.proposedName || 'Unnamed'}</div>
                                            <div style={{ fontSize: '0.85em', color: '#6b7280' }}>{survey.proposedLocation}</div>
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <span style={{
                                                display: 'inline-block',
                                                padding: '0.25rem 0.5rem',
                                                borderRadius: '9999px',
                                                fontSize: '0.75rem',
                                                fontWeight: '500',
                                                backgroundColor: '#e0f2fe',
                                                color: '#0369a1'
                                            }}>
                                                {survey.proposedStatus}
                                            </span>
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <span style={{
                                                display: 'inline-block',
                                                padding: '0.25rem 0.5rem',
                                                borderRadius: '9999px',
                                                fontSize: '0.75rem',
                                                fontWeight: '500',
                                                backgroundColor: survey.status === 'final' ? '#dcfce7' : '#f3f4f6',
                                                color: survey.status === 'final' ? '#166534' : '#374151'
                                            }}>
                                                {survey.status === 'final' ? 'Submitted' : 'Draft'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                                            <button
                                                className="btn btn-outline"
                                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem', color: 'var(--error)', borderColor: 'var(--error)' }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (confirm('Are you sure you want to delete this report?')) {
                                                        deleteBranchSurvey(survey.id);
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

export default BranchSurveyList;
