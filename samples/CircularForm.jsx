import React, { useState, useEffect } from 'react';
import ReactQuill from 'react-quill-new';
import 'react-quill-new/dist/quill.snow.css';
import { useData } from '../context/DataContext';

const CircularForm = ({ onBack, initialData }) => {
    const { addCircular, updateCircular, settings, circulars, branches, isLoading } = useData();
    const [previewTab, setPreviewTab] = useState('draft'); // 'draft' | 'pdf'

    // Lazy load state from draft or defaults or INITIAL DATA
    const [formData, setFormData] = useState(() => {
        if (initialData) return initialData; // EDIT MODE

        const savedDraft = localStorage.getItem('draft_circular_form');
        if (savedDraft) {
            try {
                return JSON.parse(savedDraft);
            } catch (e) {
                console.error("Failed to load draft", e);
            }
        }
        return {
            subject: '',
            body: '',
            conclusion: '',
            letterheadId: '',
            refNo: '',
            issuanceDate: new Date().toISOString().split('T')[0], // YYYY-MM-DD
            senderName: '',
            senderDesignation: 'Senior Regional Manager',
            references: [],
            recipientMode: 'all', // 'all' or 'specific'
            selectedBranchIds: [],
            scannedPdf: null
        };
    });

    useEffect(() => {
        // Only set Ref No if it's MISSING and NOT editing an existing circular
        // AND data is not loading anymore
        if (!isLoading && settings && !formData.refNo && !initialData) {
            const nextSeq = circulars.length + 1;
            const seqStr = nextSeq.toString().padStart(3, '0');
            const ref = `CIR/${settings.regionCode}/${settings.defaultBranchCode}/${seqStr}`;
            setFormData(prev => ({ ...prev, refNo: ref }));
        }
    }, [settings, circulars.length, initialData, isLoading]);

    // Auto-save draft on change (ONLY if NOT editing existing)
    useEffect(() => {
        if (!initialData) {
            localStorage.setItem('draft_circular_form', JSON.stringify(formData));
        }
    }, [formData, initialData]);

    const handlePdfUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.type !== 'application/pdf') {
            alert('Please upload a valid PDF file.');
            return;
        }

        if (file.size > 1024 * 1024) { // 1MB Limit
            alert('File is too large! Please upload a PDF smaller than 1MB.');
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            setFormData(prev => ({ ...prev, scannedPdf: reader.result }));
            setPreviewTab('pdf');
        };
        reader.readAsDataURL(file);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (initialData && initialData.id) {
            updateCircular(initialData.id, formData);
            alert('Circular updated successfully!');
        } else {
            addCircular(formData);
            alert('Circular saved successfully!');
            localStorage.removeItem('draft_circular_form');
        }
        if (onBack) onBack();
    };

    const addReference = () => {
        setFormData(prev => ({ ...prev, references: [...prev.references, ''] }));
    };

    const updateReference = (index, value) => {
        const newRefs = [...formData.references];
        newRefs[index] = value;
        setFormData(prev => ({ ...prev, references: newRefs }));
    };

    const removeReference = (index) => {
        const newRefs = formData.references.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, references: newRefs }));
    };

    const toggleBranchSelection = (branchId) => {
        setFormData(prev => {
            const current = new Set(prev.selectedBranchIds || []);
            if (current.has(branchId)) {
                current.delete(branchId);
            } else {
                current.add(branchId);
            }
            return { ...prev, selectedBranchIds: Array.from(current) };
        });
    };

    const modules = {
        toolbar: [
            [{ 'header': [1, 2, false] }],
            ['bold', 'italic', 'underline', 'strike', 'blockquote'],
            [{ 'list': 'ordered' }, { 'list': 'bullet' }, { 'indent': '-1' }, { 'indent': '+1' }],
            ['link', 'image'],
            ['clean']
        ],
    };

    return (
        <div className="page-container">
            <div className="page-header" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {onBack && (<button className="btn btn-outline" onClick={onBack}>← Back</button>)}
                <h1 className="page-title">{initialData ? 'Edit Circular' : 'Draft Circular'}</h1>
            </div>

            <div className="grid-2-col-layout">
                {/* LEFT: FORM */}
                <div className="card left-panel">
                    <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>

                        <div className="grid-2">
                            <div>
                                <label className="label">Reference Number</label>
                                <input type="text" className="input" value={formData.refNo} onChange={e => setFormData({ ...formData, refNo: e.target.value })} required />
                            </div>
                            <div>
                                <label className="label">Issuance Date</label>
                                <input
                                    type="date"
                                    className="input"
                                    value={formData.issuanceDate || ''}
                                    onChange={e => setFormData({ ...formData, issuanceDate: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="grid-2">
                            <div>
                                <label className="label">Sending Authority Name</label>
                                <input type="text" className="input" placeholder="Name (Optional)" value={formData.senderName} onChange={e => setFormData({ ...formData, senderName: e.target.value })} />
                            </div>
                            <div>
                                <label className="label">Designation</label>
                                <input type="text" className="input" value={formData.senderDesignation} onChange={e => setFormData({ ...formData, senderDesignation: e.target.value })} />
                            </div>
                        </div>

                        {/* Recipient Mode Selection */}
                        <div>
                            <label className="label">Recipients</label>
                            <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.5rem' }}>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                    <input type="radio" name="recipientMode" checked={formData.recipientMode !== 'specific'} onChange={() => setFormData({ ...formData, recipientMode: 'all', selectedBranchIds: [] })} />
                                    All Branches
                                </label>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                                    <input type="radio" name="recipientMode" checked={formData.recipientMode === 'specific'} onChange={() => setFormData({ ...formData, recipientMode: 'specific' })} />
                                    Specific Branches
                                </label>
                            </div>
                            {formData.recipientMode === 'specific' && (
                                <div style={{ border: '1px solid #e5e7eb', padding: '0.5rem', borderRadius: '0.5rem', maxHeight: '150px', overflowY: 'auto' }}>
                                    {branches.map(branch => (
                                        <label key={branch.id} style={{ display: 'block', fontSize: '0.85rem', cursor: 'pointer', marginBottom: '0.25rem' }}>
                                            <input
                                                type="checkbox"
                                                style={{ marginRight: '0.5rem' }}
                                                checked={(formData.selectedBranchIds || []).includes(branch.id)}
                                                onChange={() => toggleBranchSelection(branch.id)}
                                            />
                                            {branch.name} ({branch.code})
                                        </label>
                                    ))}
                                    {branches.length === 0 && <span style={{ color: 'red', fontSize: '0.8rem' }}>No branches imported.</span>}
                                </div>
                            )}
                        </div>

                        <div>
                            <label className="label">Subject</label>
                            <input type="text" className="input" value={formData.subject} onChange={e => setFormData({ ...formData, subject: e.target.value })} required />
                        </div>

                        {/* References */}
                        <div>
                            <label className="label">References</label>
                            {formData.references.map((ref, index) => (
                                <div key={index} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                    <input type="text" className="input" value={ref} onChange={(e) => updateReference(index, e.target.value)} required />
                                    <button type="button" className="btn btn-outline" style={{ color: 'red', borderColor: 'red' }} onClick={() => removeReference(index)}>X</button>
                                </div>
                            ))}
                            <button type="button" className="btn btn-outline" style={{ fontSize: '0.8rem', padding: '0.2rem 0.5rem' }} onClick={addReference}>+ Add Reference</button>
                        </div>

                        <div>
                            <label className="label">Body</label>
                            <div style={{ background: 'white' }}>
                                <ReactQuill theme="snow" value={formData.body} onChange={val => setFormData({ ...formData, body: val.replace(/INR/g, '₹') })} modules={modules} style={{ height: '200px', marginBottom: '3rem' }} />
                            </div>
                        </div>

                        <div>
                            <label className="label">Conclusion</label>
                            <textarea
                                className="input" rows="2"
                                value={formData.conclusion || ''}
                                onChange={e => setFormData({ ...formData, conclusion: e.target.value.replace(/INR/g, '₹') })}
                            />
                        </div>

                        <div className="card" style={{ background: '#f9fafb', border: '1px dashed #ccc' }}>
                            <label className="label">📎 Attach Scanned Copy (PDF)</label>
                            <input type="file" accept="application/pdf" onChange={handlePdfUpload} style={{ marginTop: '0.5rem' }} />
                            {formData.scannedPdf && <p style={{ color: 'green', fontSize: '0.8rem', marginTop: '0.5rem' }}>✓ PDF Attached</p>}
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                            <button type="submit" className="btn btn-primary">{initialData ? 'Update' : 'Save'}</button>
                        </div>
                    </form>
                </div>

                {/* RIGHT: PREVIEW */}
                <div className="right-panel">
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                        <button className={`btn ${previewTab === 'draft' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setPreviewTab('draft')}>📄 Draft Circular</button>
                        {formData.scannedPdf && (
                            <button className={`btn ${previewTab === 'pdf' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setPreviewTab('pdf')}>📎 Scanned File</button>
                        )}
                    </div>

                    {previewTab === 'pdf' && formData.scannedPdf ? (
                        <div className="card" style={{ height: '800px', padding: 0, overflow: 'hidden' }}>
                            <object data={formData.scannedPdf} type="application/pdf" width="100%" height="100%">
                                <p>PDF cannot be displayed. <a href={formData.scannedPdf} download="circular.pdf">Download</a></p>
                            </object>
                        </div>
                    ) : (
                        <div id="printable-content" className="card" style={{ minHeight: '800px' }}>
                            {(() => {
                                const { letterheads } = useData();
                                const lh = letterheads.find(l => l.id === formData.letterheadId) || letterheads[0];
                                const recipientsText = formData.recipientMode === 'specific' && formData.selectedBranchIds?.length > 0
                                    ? formData.selectedBranchIds.length === 1
                                        ? branches.find(b => b.id === formData.selectedBranchIds[0])?.name || 'Selected Branch'
                                        : 'Selected Branches'
                                    : null;

                                return (
                                    <div className="print-page">
                                        <div className="print-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid black', paddingBottom: '1rem' }}>
                                            <div>{lh?.logo && <img src={lh.logo} alt="Logo" style={{ height: '80px' }} />}</div>
                                            <div style={{ textAlign: 'right', color: '#254aa0' }}>
                                                <h1 style={{ fontSize: '16pt', fontWeight: 'bold', margin: '0 0 2px 0', lineHeight: '1.2' }}>क्षेत्रीय कार्यालय दिण्डुक्कल</h1>
                                                <h2 style={{ fontSize: '13pt', fontFamily: 'Arial', fontWeight: 'bold', margin: 0 }}>Regional Office Dindigul</h2>
                                            </div>
                                        </div>

                                        <div className="print-body">
                                            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '1.5rem', border: '1px solid black' }}>
                                                <tbody>
                                                    <tr>
                                                        <td style={{ width: '50%', padding: '10px', border: '1px solid black', verticalAlign: 'top', textAlign: 'left' }}>
                                                            <strong>वरिष्ठ क्षेत्रीय प्रबंधक</strong><br />
                                                            <strong>Senior Regional Manager</strong><br />
                                                            क्षेत्रीय कार्यालय दिण्डुक्कल<br />
                                                            Regional Office Dindigul<br />
                                                            इण्डियन ओवरसीज़ बैंक<br />
                                                            Indian Overseas Bank
                                                        </td>
                                                        <td style={{ width: '50%', padding: '10px', border: '1px solid black', verticalAlign: 'top', textAlign: 'left' }}>
                                                            <strong>सभी शाखाएँ</strong><br />
                                                            <strong>{recipientsText || 'All Branches'}</strong><br />
                                                            दिण्डुक्कल क्षेत्र<br />
                                                            Dindigul Region<br />
                                                            इण्डियन ओवरसीज़ बैंक<br />
                                                            Indian Overseas Bank
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3rem', marginTop: '0.5rem' }}>
                                                <div><strong>Ref No:</strong> {formData.refNo}</div>
                                                <div><strong>Date:</strong> {formData.issuanceDate ? new Date(formData.issuanceDate).toLocaleDateString() : new Date().toLocaleDateString()}</div>
                                            </div>

                                            <div style={{ marginBottom: '1.5rem', fontWeight: 'bold', textAlign: 'center' }}>
                                                {formData.subject}
                                            </div>

                                            {formData.references.length > 0 && (
                                                <div style={{ marginBottom: '1.5rem', display: 'flex' }}>
                                                    <strong style={{ minWidth: '40px' }}>Ref:</strong>
                                                    <div>
                                                        {formData.references.map((ref, index) => (
                                                            <div key={index} style={{ display: 'flex' }}>
                                                                <span style={{ marginRight: '0.5rem' }}>{index + 1}.</span>
                                                                <span>{ref}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            <div className="ql-editor" style={{ padding: 0, textAlign: 'justify', marginBottom: '4rem' }} dangerouslySetInnerHTML={{ __html: formData.body }} />

                                            {formData.conclusion && (
                                                <div style={{ marginBottom: '4rem', textAlign: 'justify' }}>
                                                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Conclusion:</div>
                                                    {formData.conclusion}
                                                </div>
                                            )}

                                            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                                                <div style={{ textAlign: 'left' }}>
                                                    {formData.senderName && <p style={{ fontWeight: 'bold' }}>({formData.senderName})</p>}
                                                    <p>{formData.senderDesignation}</p>
                                                    <p>Regional Office Dindigul</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}
                        </div>
                    )}

                    {previewTab === 'draft' && (
                        <div style={{ margin: '2rem 0', textAlign: 'center' }}>
                            <button type="button" className="btn btn-primary" onClick={() => window.print()}>🖨️ Print Final Circular</button>
                        </div>
                    )}
                </div>
            </div>

            <style>{`
                .grid-2-col-layout {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 2rem;
                    max-width: 1000px;
                    margin: 0 auto;
                }
                .label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
                .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
                @media print {
                    .page-header, .left-panel, .btn { display: none !important; }
                    .right-panel { display: block !important; width: 100% !important; }
                    .card { box-shadow: none !important; border: none !important; }
                }
                 /* No specific media query needed for responsive as it is now always stacked */
            `}</style>
        </div>
    );
};

export default CircularForm;
