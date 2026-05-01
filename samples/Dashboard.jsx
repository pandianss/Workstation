import React from 'react';
import { useData } from '../context/DataContext';

const Dashboard = () => {
    const { officeNotes, letters, returns, branches } = useData();

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Dashboard</h1>
                <p className="text-neutral-500">Overview of Regional Office activities.</p>
            </div>
            <div className="grid-summary">
                <div className="card">
                    <h3>Office Notes Generated</h3>
                    <p className="stat">{officeNotes.length}</p>
                </div>
                <div className="card">
                    <h3>Letters Drafted</h3>
                    <p className="stat">{letters.length}</p>
                </div>
                <div className="card">
                    <h3>Returns Submitted</h3>
                    <p className="stat">{returns.length}</p>
                </div>
                <div className="card">
                    <h3>Active Branches</h3>
                    <p className="stat">{branches.length}</p>
                </div>
            </div>
            <style>{`
        .grid-summary {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1.5rem;
          margin-top: 1rem;
        }
        .stat {
          font-size: 2.5rem;
          font-weight: 700;
          color: hsl(var(--primary));
          margin-top: 0.5rem;
        }
      `}</style>
        </div>
    );
};

export default Dashboard;
