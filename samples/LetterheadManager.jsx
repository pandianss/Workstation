import React, { useState } from 'react';
import { useData } from '../context/DataContext';

const LetterheadManager = () => {
    const { letterheads, addLetterhead, updateLetterhead, deleteLetterhead } = useData();
    const [isEditing, setIsEditing] = useState(false);
    const [currentLh, setCurrentLh] = useState({ name: '', header: '' });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (currentLh.id) {
            updateLetterhead(currentLh.id, currentLh);
        } else {
            addLetterhead(currentLh);
        }
        setIsEditing(false);
        setCurrentLh({ name: '', header: '' });
    };

    const handleEdit = (lh) => {
        setCurrentLh(lh);
        setIsEditing(true);
    };

    const handleDelete = (id) => {
        if (window.confirm('Are you sure you want to delete this letterhead?')) {
            deleteLetterhead(id);
        }
    };

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 className="page-title">Letterhead Configuration</h1>
                {!isEditing && (
                    <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                        + New Letterhead
                    </button>
                )}
            </div>

            <div className="content-grid">
                {/* Form Section */}
                {isEditing && (
                    <div className="card form-section" style={{ marginBottom: '2rem' }}>
                        <h2>{currentLh.id ? 'Edit' : 'Create'} Letterhead</h2>
                        <form onSubmit={handleSubmit} style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Template Name</label>
                                <input
                                    type="text"
                                    className="input"
                                    value={currentLh.name}
                                    onChange={(e) => setCurrentLh({ ...currentLh, name: e.target.value })}
                                    placeholder="e.g. Standard Office"
                                    required
                                />
                            </div>
                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Header Text</label>
                                <input
                                    type="text"
                                    className="input"
                                    value={currentLh.header}
                                    onChange={(e) => setCurrentLh({ ...currentLh, header: e.target.value })}
                                    placeholder="e.g. Regional Planning Office, Dindigul"
                                    required
                                />
                            </div>
                            {/* Logo upload could go here */}

                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                                <button type="submit" className="btn btn-primary">Save Template</button>
                                <button type="button" className="btn btn-outline" onClick={() => { setIsEditing(false); setCurrentLh({ name: '', header: '' }); }}>Cancel</button>
                            </div>
                        </form>
                    </div>
                )}

                {/* List Section */}
                <div className="list-section">
                    {letterheads.map(lh => (
                        <div key={lh.id} className="card letterhead-item" style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{lh.name}</h3>
                                <p style={{ color: 'hsl(var(--neutral) / 0.7)', fontSize: '0.9rem' }}>{lh.header}</p>
                            </div>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button className="btn btn-outline" onClick={() => handleEdit(lh)}>Edit</button>
                                <button className="btn btn-outline" style={{ borderColor: 'hsl(var(--error))', color: 'hsl(var(--error))' }} onClick={() => handleDelete(lh.id)}>Delete</button>
                            </div>
                        </div>
                    ))}
                    {letterheads.length === 0 && <p style={{ textAlign: 'center', color: 'gray' }}>No letterheads configured.</p>}
                </div>
            </div>
        </div>
    );
};

export default LetterheadManager;
