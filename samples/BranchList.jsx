import { useNavigate } from 'react-router-dom'; // Assuming react-router is used
import { useData } from '../context/DataContext';
import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet Default Icon Issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

import { parseBranchExcel } from '../utils/excelParser';

const BranchList = () => {
    const { branches, setBranches, updateBranch, deleteBranch } = useData();
    const navigate = useNavigate();
    const [showAdd, setShowAdd] = useState(false);
    const [viewMode, setViewMode] = useState('list'); // 'list' | 'map'
    const [showRoute, setShowRoute] = useState(false); // To toggle route visibility
    const [newBranch, setNewBranch] = useState({ name: '', code: '', location: '' });
    const [importError, setImportError] = useState('');

    const handleAdd = (e) => {
        e.preventDefault();
        if (newBranch.id) {
            // Edit Mode
            updateBranch(newBranch.id, newBranch);
            alert('Branch updated successfully');
        } else {
            // Create Mode
            const branch = { ...newBranch, id: Date.now().toString() };
            setBranches(prev => [...prev, branch]);
            alert('Branch added successfully');
        }
        setShowAdd(false);
        setNewBranch({ name: '', code: '', location: '' });
    };

    const handleImport = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const importedBranches = await parseBranchExcel(file);
            setBranches(prev => {
                // Avoid duplicates by code
                const existingCodes = new Set(prev.map(b => b.code));
                const uniqueNew = importedBranches.filter(b => !existingCodes.has(b.code));
                return [...prev, ...uniqueNew];
            });
            alert(`Successfully imported ${importedBranches.length} branches!`);
            setImportError('');
        } catch (err) {
            console.error(err);
            setImportError(typeof err === 'string' ? err : 'Failed to parse Excel file.');
        }
    };

    // Calculate Map Center (Default to Dindigul roughly if no data, or average of branches)
    const validBranches = branches.filter(b => b.lat && b.lng);
    const center = validBranches.length > 0
        ? [validBranches[0].lat, validBranches[0].lng]
        : [10.3673, 77.9803]; // Dindigul Coordinates

    // Route Coordinates
    const routePositions = validBranches.map(b => [b.lat, b.lng]);

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 className="page-title">Branch Management</h1>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>

                    {viewMode === 'map' && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <input
                                type="checkbox"
                                id="showRoute"
                                checked={showRoute}
                                onChange={(e) => setShowRoute(e.target.checked)}
                                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                            />
                            <label htmlFor="showRoute" style={{ cursor: 'pointer', fontWeight: '500' }}>Show Routes</label>
                        </div>
                    )}

                    <div className="btn-group" style={{ display: 'flex', border: '1px solid #ccc', borderRadius: '4px', overflow: 'hidden' }}>
                        <button
                            className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-outline'}`}
                            style={{ borderRadius: 0, border: 'none' }}
                            onClick={() => setViewMode('list')}
                        >
                            List View
                        </button>
                        <button
                            className={`btn ${viewMode === 'map' ? 'btn-primary' : 'btn-outline'}`}
                            style={{ borderRadius: 0, border: 'none' }}
                            onClick={() => setViewMode('map')}
                        >
                            Map View
                        </button>
                    </div>

                    <label className="btn btn-outline" style={{ cursor: 'pointer' }}>
                        📥 Import Excel
                        <input type="file" accept=".xlsx, .xls" style={{ display: 'none' }} onChange={handleImport} />
                    </label>
                    <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
                        {showAdd ? 'Cancel' : '+ Add Branch'}
                    </button>
                </div>
            </div>

            {importError && (
                <div style={{ padding: '1rem', background: '#ffebee', color: '#c62828', marginBottom: '1rem', borderRadius: '0.5rem' }}>
                    {importError}
                </div>
            )}

            {showAdd && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3>Add New Branch</h3>
                    <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                        <input
                            className="input" placeholder="Branch Name" required
                            value={newBranch.name} onChange={e => setNewBranch({ ...newBranch, name: e.target.value })}
                        />
                        <input
                            className="input" placeholder="Branch Code (SOL ID)" required
                            value={newBranch.code} onChange={e => setNewBranch({ ...newBranch, code: e.target.value })}
                        />
                        <input
                            className="input" placeholder="Location" required
                            value={newBranch.location} onChange={e => setNewBranch({ ...newBranch, location: e.target.value })}
                        />
                        <button type="submit" className="btn btn-primary">Save</button>
                    </form>
                </div>
            )}

            {viewMode === 'list' ? (
                <div className="branches-grid">
                    {branches.map(branch => (
                        <div key={branch.id} className="card branch-card" onClick={() => navigate(`/branches/${branch.id}`)}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <h3 style={{ margin: '0 0 0.5rem 0' }}>{branch.name}</h3>
                                <div style={{ display: 'flex', gap: '0.4rem' }}>
                                    <button
                                        className="btn btn-outline"
                                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setNewBranch(branch);
                                            setShowAdd(true);
                                        }}
                                    >
                                        ✏️
                                    </button>
                                    <button
                                        className="btn btn-outline"
                                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem', color: 'red', borderColor: 'red' }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (confirm(`Delete ${branch.name}?`)) {
                                                deleteBranch(branch.id);
                                            }
                                        }}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                            <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '0.2rem 0.6rem', borderRadius: '1rem', fontSize: '0.8rem', fontWeight: 'bold' }}>
                                {branch.code}
                            </span>
                            <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}>{branch.location || 'Location: N/A'}</p>
                            {branch.lat && <p style={{ fontSize: '0.8rem', color: '#16a34a' }}>📍 Map Available</p>}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card" style={{ height: '600px', padding: 0, overflow: 'hidden' }}>
                    <MapContainer center={center} zoom={10} style={{ height: '100%', width: '100%' }}>
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        {showRoute && routePositions.length > 1 && (
                            <Polyline
                                positions={routePositions}
                                color="blue"
                                weight={4}
                                opacity={0.6}
                                dashArray="10, 10" // Dashed line for effect
                            />
                        )}
                        {validBranches.map(branch => (
                            <Marker key={branch.id} position={[branch.lat, branch.lng]}>
                                <Popup>
                                    <div style={{ textAlign: 'center' }}>
                                        <strong>{branch.name} ({String(branch.code).padStart(4, '0')})</strong><br />
                                        {branch.location}
                                    </div>
                                </Popup>
                            </Marker>
                        ))}
                    </MapContainer>
                </div>
            )}

            <style>{`
        .branches-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1.5rem;
        }
        .branch-card {
          cursor: pointer;
          transition: transform 0.2s;
        }
        .branch-card:hover {
          transform: translateY(-4px);
          border-color: hsl(var(--primary));
        }
      `}</style>
        </div>
    );
};

export default BranchList;
