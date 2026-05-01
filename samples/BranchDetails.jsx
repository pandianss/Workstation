import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';

const BranchDetails = () => {
    const { id } = useParams();
    const { branches } = useData();
    const navigate = useNavigate();

    const branch = branches.find(b => b.id === id);

    if (!branch) return <div className="page-container">Branch not found</div>;

    return (
        <div className="page-container">
            <button className="btn btn-outline" onClick={() => navigate('/branches')} style={{ marginBottom: '1rem' }}>&larr; Back to List</button>
            <div className="card">
                <h1 className="page-title">{branch.name}</h1>
                <div className="details-grid" style={{ marginTop: '1rem' }}>
                    <div className="detail-item">
                        <strong>Branch Code:</strong> {branch.code}
                    </div>
                    <div className="detail-item">
                        <strong>Location:</strong> {branch.location || 'N/A'}
                    </div>
                    <div className="detail-item">
                        <strong>Head of Branch:</strong> Not Assigned
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '2rem' }}>
                <h3>Recent Activities</h3>
                <p style={{ color: 'gray' }}>No recent activities recorded for this branch.</p>
            </div>

            <style>{`
        .details-grid {
          display: grid;
          gap: 1rem;
        }
        .detail-item {
          padding: 1rem;
          background: hsl(var(--base-200));
          border-radius: var(--radius-sm);
        }
      `}</style>
        </div>
    );
};

export default BranchDetails;
