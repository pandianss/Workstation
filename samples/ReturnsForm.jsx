import React, { useState } from 'react';
import { useData } from '../context/DataContext';

const ReturnsForm = () => {
    const { setReturns } = useData();
    const [formData, setFormData] = useState({
        returnType: 'Monthly',
        period: '',
        description: '',
        status: 'Submitted'
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        setReturns(prev => [...prev, { ...formData, id: Date.now().toString(), date: new Date().toISOString() }]);
        alert('Return Entry Added!');
        setFormData({ returnType: 'Monthly', period: '', description: '', status: 'Submitted' });
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Periodical Returns Entry</h1>
            </div>
            <div className="card">
                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem', maxWidth: '600px' }}>

                    <div>
                        <label className="label">Return Type</label>
                        <select
                            className="input"
                            value={formData.returnType}
                            onChange={e => setFormData({ ...formData, returnType: e.target.value })}
                        >
                            <option value="Monthly">Monthly Progress Report</option>
                            <option value="Quarterly">Quarterly Review</option>
                            <option value="Annual">Annual Report</option>
                        </select>
                    </div>

                    <div>
                        <label className="label">Period (Month/Year)</label>
                        <input
                            type="month" className="input"
                            value={formData.period} onChange={e => setFormData({ ...formData, period: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="label">Details / Remarks</label>
                        <textarea
                            className="input" rows="4"
                            value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Enter details..."
                        />
                    </div>

                    <button type="submit" className="btn btn-primary">Submit Entry</button>
                </form>
            </div>
            <style>{`
        .label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
      `}</style>
        </div>
    );
};

export default ReturnsForm;
