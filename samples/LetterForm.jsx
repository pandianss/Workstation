import React, { useState, useEffect } from 'react';
import ReactQuill from 'react-quill-new';
import 'react-quill-new/dist/quill.snow.css';
import { useData } from '../context/DataContext';

const LetterForm = ({ onBack, initialData }) => {
    const { addLetter, updateLetter, settings, letters, branches, isLoading } = useData();
    const [previewTab, setPreviewTab] = useState('draft'); // 'draft' | 'pdf'

    // Lazy load state from draft or defaults or INITIAL DATA
    const [formData, setFormData] = useState(() => {
        if (initialData) return {
            ...initialData,
            letterType: initialData.letterType || 'Branch',
            classification: initialData.classification || initialData.letterType || '',
            fromName: initialData.fromName || '',
            fromDesignation: initialData.fromDesignation || '',
            toName: initialData.toName || '',
            toDesignation: initialData.toDesignation || '',
            toAddress: initialData.toAddress || initialData.recipientAddress || '', // Migration fallback
            refNo: initialData.refNo || '',
        };

        const savedDraft = localStorage.getItem('draft_letter_form');
        if (savedDraft) {
            try {
                return JSON.parse(savedDraft);
            } catch (e) {
                console.error("Failed to load draft", e);
            }
        }
        return {
            refNo: '',
            date: new Date().toLocaleDateString('en-GB'), // Default to today
            issuanceDate: new Date().toISOString().split('T')[0], // YYYY-MM-DD for input
            letterType: 'Branch',
            classification: '',
            fromName: '',
            fromDesignation: '',
            toName: '',
            toDesignation: '',
            toAddress: '',
            subject: '',
            body: '',
            recipientBranchId: '', // For auto-fill
            letterheadId: '',
            scannedPdf: null // Base64 string
        };
    });

    useEffect(() => {
        // Only set Ref No if it's MISSING and NOT editing
        // AND data is not loading anymore
        if (!isLoading && settings && !formData.refNo && !initialData) {
            const nextSeq = letters.length + 1;
            const seqStr = nextSeq.toString().padStart(3, '0');
            const ref = `LT/${settings.regionCode}/${settings.defaultBranchCode}/${seqStr}`;
            setFormData(prev => ({ ...prev, refNo: ref }));
        }
    }, [settings, letters.length, initialData, isLoading]);

    // Auto-save draft
    useEffect(() => {
        if (!initialData) {
            localStorage.setItem('draft_letter_form', JSON.stringify(formData));
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
            alert('File is too large! Please upload a PDF smaller than 1MB to avoid storage issues.');
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            setFormData(prev => ({ ...prev, scannedPdf: reader.result }));
            setPreviewTab('pdf'); // Switch to PDF view
        };
        reader.readAsDataURL(file);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (initialData && initialData.id) {
            updateLetter(initialData.id, formData);
            alert('Letter updated successfully!');
        } else {
            addLetter(formData);
            alert('Letter saved successfully!');
            localStorage.removeItem('draft_letter_form');
        }
        if (onBack) onBack();
    };

    const handleBranchChange = (e) => {
        const branchId = e.target.value;
        setFormData(prev => ({ ...prev, recipientBranchId: branchId }));

        if (branchId) {
            const branch = branches.find(b => b.id === branchId);
            if (branch) {
                // Pre-fill fields
                setFormData(prev => ({
                    ...prev,
                    letterType: 'Branch',
                    classification: branch.name, // Set classification to Branch Name
                    toName: 'The Branch Manager',
                    toDesignation: 'Indian Overseas Bank',
                    toAddress: `${branch.name} Branch\n${branch.location}`
                }));
            }
        }
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
                <h1 className="page-title">{initialData ? 'Edit Letter' : 'Draft Letter'}</h1>
            </div>

            <div className="grid-2-col-layout">
                {/* LEFT: FORM */}
                <div className="card left-panel">
                    <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>

                        <div className="grid-2">
                            <div>
                                <label className="label">Letter Label / Classification</label>
                                <select
                                    className="input"
                                    value={formData.letterType}
                                    onChange={(e) => {
                                        const type = e.target.value;
                                        setFormData(prev => ({
                                            ...prev,
                                            letterType: type,
                                            classification: type === 'Branch' ? '' : type,
                                            recipientBranchId: type === 'Branch' ? prev.recipientBranchId : ''
                                        }));
                                    }}
                                >
                                    <option value="Central Office">Central Office</option>
                                    <option value="Branch">Branch</option>
                                    <option value="External">External</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            {formData.letterType === 'Branch' ? (
                                <div>
                                    <label className="label">Select Branch</label>
                                    <select
                                        className="input"
                                        value={formData.recipientBranchId || ''}
                                        onChange={handleBranchChange}
                                    >
                                        <option value="">-- Select Branch --</option>
                                        {branches.map(b => (
                                            <option key={b.id} value={b.id}>{b.name}</option>
                                        ))}
                                    </select>
                                </div>
                            ) : (
                                <div>
                                    <label className="label">Reference Number</label>
                                    <input type="text" className="input" value={formData.refNo} onChange={e => setFormData({ ...formData, refNo: e.target.value })} required />
                                </div>
                            )}
                        </div>

                        {formData.letterType === 'Branch' && (
                            <div className="grid-2">
                                <div>
                                    <label className="label">Reference Number</label>
                                    <input type="text" className="input" value={formData.refNo} onChange={e => setFormData({ ...formData, refNo: e.target.value })} required />
                                </div>
                                <div />
                            </div>
                        )}

                        <div className="grid-2">
                            <div>
                                <label className="label">Letter Date</label>
                                <input type="text" className="input" value={formData.date} onChange={e => setFormData({ ...formData, date: e.target.value })} />
                            </div>
                            <div>
                                <label className="label">Issuance Date (Manual)</label>
                                <input
                                    type="date"
                                    className="input"
                                    value={formData.issuanceDate || ''}
                                    onChange={e => setFormData({ ...formData, issuanceDate: e.target.value })}
                                />
                            </div>
                        </div>

                        {/* From Section */}
                        <div style={{ border: '1px solid #e5e7eb', padding: '1rem', borderRadius: '0.5rem' }}>
                            <h4 style={{ marginTop: 0, marginBottom: '1rem', color: '#4b5563' }}>From Detail</h4>
                            <div className="grid-2">
                                <div>
                                    <label className="label">Name</label>
                                    <input className="input" value={formData.fromName} onChange={e => setFormData({ ...formData, fromName: e.target.value })} placeholder="e.g. R. Velmurugan" />
                                </div>
                                <div>
                                    <label className="label">Designation</label>
                                    <input className="input" value={formData.fromDesignation} onChange={e => setFormData({ ...formData, fromDesignation: e.target.value })} placeholder="e.g. Chief Regional Manager" />
                                </div>
                            </div>
                            <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'gray' }}>
                                <i>Fixed Suffix:</i><br />
                                Regional Office Dindigul / क्षेत्रीय कार्यालय दिण्डुक्कल<br />
                                Indian Overseas Bank / इण्डियन ओवरसीज़ बैंक
                            </div>
                        </div>

                        {/* To Section */}
                        <div style={{ border: '1px solid #e5e7eb', padding: '1rem', borderRadius: '0.5rem' }}>
                            <h4 style={{ marginTop: 0, marginBottom: '1rem', color: '#4b5563' }}>To Detail</h4>



                            <div className="grid-2">
                                <div>
                                    <label className="label">Recipient Name</label>
                                    <input className="input" value={formData.toName} onChange={e => setFormData({ ...formData, toName: e.target.value })} placeholder="Name" />
                                </div>
                                <div>
                                    <label className="label">Designation</label>
                                    <input className="input" value={formData.toDesignation} onChange={e => setFormData({ ...formData, toDesignation: e.target.value })} placeholder="Designation" />
                                </div>
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <label className="label">Address</label>
                                <textarea className="input" rows="3" value={formData.toAddress} onChange={e => setFormData({ ...formData, toAddress: e.target.value })} placeholder="Full Address..." />
                            </div>
                        </div>

                        <div>
                            <label className="label">Subject</label>
                            <input type="text" className="input" value={formData.subject} onChange={e => setFormData({ ...formData, subject: e.target.value })} required />
                        </div>

                        <div>
                            <label className="label">Body</label>
                            <div style={{ background: 'white' }}>
                                <ReactQuill theme="snow" value={formData.body} onChange={val => setFormData({ ...formData, body: val })} modules={modules} style={{ height: '200px', marginBottom: '3rem' }} />
                            </div>
                        </div>

                        <div className="card" style={{ background: '#f9fafb', border: '1px dashed #ccc' }}>
                            <label className="label">📎 Attach Scanned Copy (PDF)</label>
                            <input type="file" accept="application/pdf" onChange={handlePdfUpload} style={{ marginTop: '0.5rem' }} />
                            {formData.scannedPdf && <p style={{ color: 'green', fontSize: '0.8rem', marginTop: '0.5rem' }}>✓ PDF Attached</p>}
                            <p style={{ fontSize: '0.75rem', color: '#666' }}>Max size: 1MB. Storage is limited.</p>
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                            <button type="submit" className="btn btn-primary">{initialData ? 'Update' : 'Save'}</button>
                        </div>
                    </form>
                </div>

                {/* RIGHT: PREVIEW */}
                <div className="right-panel">
                    {/* TABS */}
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                        <button
                            className={`btn ${previewTab === 'draft' ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => setPreviewTab('draft')}
                        >
                            📄 Draft Preview
                        </button>
                        {formData.scannedPdf && (
                            <button
                                className={`btn ${previewTab === 'pdf' ? 'btn-primary' : 'btn-outline'}`}
                                onClick={() => setPreviewTab('pdf')}
                            >
                                📎 Scanned File
                            </button>
                        )}
                    </div>

                    {previewTab === 'pdf' && formData.scannedPdf ? (
                        <div className="card" style={{ height: '800px', padding: 0, overflow: 'hidden' }}>
                            <object data={formData.scannedPdf} type="application/pdf" width="100%" height="100%">
                                <p>PDF cannot be displayed. <a href={formData.scannedPdf} download="scanned_doc.pdf">Download</a></p>
                            </object>
                        </div>
                    ) : (
                        <div id="printable-content" className="card" style={{ minHeight: '800px' }}>
                            {/* ... EXISING PRINT LAYOUT ... */}
                            {(() => {
                                const { letterheads } = useData();
                                const lh = letterheads.find(l => l.id === formData.letterheadId) || letterheads[0];
                                return (
                                    <div className="print-page">
                                        <div className="print-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid black', paddingBottom: '1rem' }}>
                                            <div>{lh?.logo && <img src={lh.logo} alt="Logo" style={{ height: '80px' }} />}</div>
                                            <div style={{ textAlign: 'right', color: '#254aa0' }}>
                                                <h1 style={{ fontSize: '16pt', fontWeight: 'bold', margin: '0 0 2px 0', lineHeight: '1.2' }}>क्षेत्रीय कार्यालय दिण्डुक्कल</h1>
                                                <h2 style={{ fontSize: '13pt', fontFamily: 'Arial', fontWeight: 'bold', margin: 0 }}>Regional Office Dindigul</h2>
                                            </div>
                                        </div>

                                        <div className="print-body" style={{ marginTop: '2rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                                                <div style={{ maxWidth: '50%' }}>
                                                    <strong>From:</strong><br />
                                                    {formData.fromName && <div>{formData.fromName}</div>}
                                                    {formData.fromDesignation && <div>{formData.fromDesignation}</div>}
                                                    <div>Regional Office Dindigul / क्षेत्रीय कार्यालय दिण्डुक्कल</div>
                                                    <div>Indian Overseas Bank / इण्डियन ओवरसीज़ बैंक</div>
                                                </div>
                                                <div style={{ textAlign: 'right' }}>
                                                    <div><strong>Ref:</strong> {formData.refNo}</div>
                                                    <div><strong>Date:</strong> {formData.issuanceDate ? new Date(formData.issuanceDate).toLocaleDateString() : (formData.date || new Date().toLocaleDateString())}</div>
                                                </div>
                                            </div>

                                            <div style={{ marginBottom: '2rem', whiteSpace: 'pre-wrap' }}>
                                                <strong>To:</strong><br />
                                                {formData.toName && <div>{formData.toName}</div>}
                                                {formData.toDesignation && <div>{formData.toDesignation}</div>}
                                                {formData.toAddress}
                                            </div>

                                            <div style={{ marginBottom: '1.5rem' }}>
                                                <strong>Sub:</strong> {formData.subject}
                                            </div>

                                            <div className="ql-editor" style={{ padding: 0, textAlign: 'justify', marginBottom: '4rem' }} dangerouslySetInnerHTML={{ __html: formData.body }} />

                                            <div style={{ textAlign: 'left', marginTop: '4rem' }}>
                                                <p>Yours Faithfully,</p>
                                                <br /><br />
                                                <p><strong>{formData.fromName || 'Senior Regional Manager'}</strong></p>
                                                <p>{formData.fromDesignation || 'Regional Office'}</p>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}
                        </div>
                    )}

                    {previewTab === 'draft' && (
                        <div style={{ margin: '2rem 0', textAlign: 'center' }}>
                            <button type="button" className="btn btn-primary" onClick={() => window.print()}>🖨️ Print Final Letter</button>
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

export default LetterForm;
