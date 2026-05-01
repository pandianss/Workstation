import React, { useState } from 'react';
import { useData } from '../context/DataContext';
import LetterheadSelector from '../components/LetterheadSelector';

import { generatePDF } from '../utils/pdfHelper';
import { generateReferenceNumber } from '../utils/idGenerator';



const OfficeNoteForm = () => {
    const { addOfficeNote, settings } = useData();
    const [formData, setFormData] = useState({
        subject: '',
        refNo: '',
        to: '',
        body: '',
        letterheadId: ''
    });

    const handleSavePDF = () => {
        // Save Record
        addOfficeNote(formData);

        const fileName = `OfficeNote_${formData.refNo.replace(/\//g, '-')}.pdf`;
        generatePDF('printable-content', fileName);
    };

    useEffect(() => {
        // Auto-generate Ref No on load
        if (settings) {
            const ref = generateReferenceNumber('ON', settings.regionCode, settings.defaultBranchCode);
            setFormData(prev => ({ ...prev, refNo: ref }));
        }
    }, [settings]);

    const handleSubmit = (e) => {
        e.preventDefault();
        addOfficeNote(formData);
        alert('Office Note Generated Successfully!');
        setFormData(prev => ({
            subject: '',
            refNo: generateReferenceNumber('ON', settings.regionCode, settings.defaultBranchCode),
            to: '',
            body: '',
            letterheadId: ''
        }));
    };



    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">New Office Note</h1>
            </div>
            <div className="card">
                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>

                    <LetterheadSelector
                        value={formData.letterheadId}
                        onChange={(val) => setFormData({ ...formData, letterheadId: val })}
                    />

                    <div className="grid-2">
                        <div>
                            <label className="label">Reference Number (Auto-generated)</label>
                            <input
                                type="text" className="input" placeholder="e.g. A2/123/2024"
                                value={formData.refNo} onChange={e => setFormData({ ...formData, refNo: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label className="label">To (Designation/Dept)</label>
                            <input
                                type="text" className="input" placeholder="e.g. Assistant Director"
                                value={formData.to} onChange={e => setFormData({ ...formData, to: e.target.value })}
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="label">Subject</label>
                        <input
                            type="text" className="input" placeholder="Note Subject..."
                            value={formData.subject} onChange={e => setFormData({ ...formData, subject: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="label">Note Content</label>
                        <textarea
                            className="input" rows="8" placeholder="Enter note details..."
                            value={formData.body} onChange={e => {
                                const val = e.target.value.replace(/INR/g, '₹');
                                setFormData({ ...formData, body: val });
                            }}
                            required
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button type="submit" className="btn btn-primary">Generate Note</button>
                        <button type="button" className="btn btn-outline" onClick={handleSavePDF}>Export as PDF</button>
                    </div>
                </form>
            </div>
            <div id="printable-content">
                {(() => {
                    const { letterheads } = useData();
                    const lh = letterheads.find(l => l.id === formData.letterheadId) || letterheads[0]; // Default to first if none selected
                    return (
                        <div className="print-page">
                            <div className="print-header" style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '2rem',
                                borderBottom: '2px solid black',
                                paddingBottom: '1rem'
                            }}>
                                <div style={{ flexShrink: 0 }}>
                                    {lh?.logo && <img src={lh.logo} alt="Logo" style={{ height: '80px' }} />}
                                </div>
                                <div style={{ textAlign: 'right', color: '#254aa0' }}>
                                    <h1 style={{ fontSize: '16pt', fontWeight: 'bold', margin: '0 0 2px 0', lineHeight: '1.2' }}>क्षेत्रीय कार्यालय दिण्डुक्कल</h1>
                                    <h2 style={{ fontSize: '13pt', fontFamily: 'Arial, sans-serif', fontWeight: 'bold', margin: 0, lineHeight: '1.2', textTransform: 'uppercase', letterSpacing: '-0.3px' }}>Regional Office Dindigul</h2>
                                </div>
                            </div>

                            <div className="print-body" style={{ fontSize: '11pt', lineHeight: '1.5' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                                    <div><strong>Ref No:</strong> {formData.refNo}</div>
                                    <div><strong>Date:</strong> {new Date().toLocaleDateString()}</div>
                                </div>

                                <div style={{ marginBottom: '1.5rem' }}>
                                    <strong>To:</strong><br />
                                    {formData.to}
                                </div>

                                <div style={{ marginBottom: '1.5rem', fontWeight: 'bold', textDecoration: 'underline' }}>
                                    Sub: {formData.subject}
                                </div>

                                <div style={{ whiteSpace: 'pre-wrap', textAlign: 'justify' }}>
                                    {formData.body}
                                </div>

                                <div style={{ marginTop: '4rem', display: 'flex', justifyContent: 'flex-end' }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <p>Assistant Director</p>
                                        <p>Regional Planning Office</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })()}
            </div>

            <style>{`
        .grid-2 {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.5rem;
        }
        @media (max-width: 640px) {
          .grid-2 { grid-template-columns: 1fr; }
        }
        .label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
      `}</style>
        </div>
    );
};

export default OfficeNoteForm;
