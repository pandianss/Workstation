import React, { useState, useEffect } from 'react';
import { useData } from '../context/DataContext';

const BranchOpeningSurveyReport = ({ onBack, initialData }) => {
    const { letterheads, addBranchSurvey, updateBranchSurvey } = useData();
    const lh = letterheads && letterheads.length > 0 ? letterheads[0] : null;

    const [viewMode, setViewMode] = useState('edit'); // 'edit' | 'preview'
    const [currentStep, setCurrentStep] = useState(0);

    const steps = [
        { title: 'General Info', icon: '📋' },
        { title: 'Application Details', icon: '📝' },
        { title: 'Proposed Office', icon: '🏢' },
        { title: 'Competitor Analysis', icon: '📊' },
        { title: 'Command Area', icon: '🌍' },
        { title: 'Financials', icon: '💰' },
        { title: 'Logistics', icon: '🚚' }
    ];

    const [formData, setFormData] = useState(() => {
        if (initialData) return initialData;
        return {
            region: '',
            date: new Date().toISOString().split('T')[0],
            status: 'draft', // 'draft' | 'final'
            applicationType: 'new', // 'new' | 'change'
            applicationLocation: '',
            applicationFrom: '',
            applicationTo: '',
            applicantName: '',
            applicantDesignation: 'Senior Regional Manager',
            surveyorName: '',
            surveyorDesignation: '',
            surveyorBranch: '',

            // Section 2
            proposedName: '', // 2(a)
            proposedLocation: '', // 2(b)
            proposedRevenueCentre: '', // 2(b)(i)
            proposedBlock: '', // 2(c)(i)
            proposedTehsil: '', // 2(c)(ii)
            proposedDistrict: '', // 2(c)(iii)
            proposedDistrictGDP: '',
            proposedState: '', // 2(c)(iv)
            proposedStateGDP: '',
            proposedPin: '', // 2(c)(v)

            // Header Fields
            regionName: 'Dindigul',
            reportDate: new Date().toLocaleDateString('en-GB'), // DD/MM/YYYY

            proposedStatus: 'Branch', // 2(d)
            existingBranches: '', // 2(e)
            nearestBankDistance: '', // 2(f)


            // Competitor Analysis 2(g)
            competitorAnalysisApplicable: true,
            competitors: Array(5).fill({
                bankName: '', centreName: '', deposits: '', depositsNo: '', advances: '', advancesNo: '', businessMix: '', businessMixNo: ''
            }),

            // Section 3 & 4
            previousApplications: '', // 3
            reasonForOffice: '', // 4
            population: '', // 4(i)

            // Command Area 4(ii)
            commandRadius: '',
            commandPopulation: '',
            commandVillages: '',

            // Production 4(iii)
            production: Array(3).fill({
                commodity: '', prodVol: '', prodVal: '', impVol: '', impVal: '', expVol: '', expVal: ''
            }),

            // Development 4(iv)
            developmentSchemes: '',

            // Inadequate Facilities 4(v)
            inadequateReason: '',

            // Prospects 4(vi)
            prospectsDeposits: '',
            prospectsAdvances: '',

            // Section 5, 6
            changeLocationDetails: '', // 5
            expenditureDetails: '', // 6

            // Financials (Expenditure)
            estCharges: '',
            stationeryMisc: '',
            rentBuilding: '',
            interestDeposits: '',
            interestBorrowed: '',
            interestBorrowedRate: '',
            totalExpenditure: '',

            // Financials (Income)
            interestAdvances: '',
            commission: '',
            exchange: '',
            interestLent: '',
            totalIncome: '',
            cumulativeProfit: '',

            // Financial Calculators (Not in Report)
            depositGrowth: '',
            costOfDeposit: '',
            advanceGrowth: '',
            yieldOnAdvance: '',
            monthlyRent: '',
            manualHolidays: '',

            // Logistics
            otherParticulars: '', // 7
            brickMortarAvailable: '', // 8
            networkLeasedLine: '', // 9
            networkDataCard: '' // 10
        };
    });

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleCompetitorChange = (index, field, value) => {
        const newCompetitors = [...formData.competitors];
        newCompetitors[index] = { ...newCompetitors[index], [field]: value };
        setFormData(prev => ({ ...prev, competitors: newCompetitors }));
    };

    const handleProductionChange = (index, field, value) => {
        const newProduction = [...formData.production];
        newProduction[index] = { ...newProduction[index], [field]: value };
        setFormData(prev => ({ ...prev, production: newProduction }));
    };


    // Auto-calculate Financials
    useEffect(() => {
        const parse = (val) => parseFloat(String(val).replace(/[^\d.-]/g, '')) || 0;

        // Calculator Logic: Growth/Day * 365 / 2 * Rate/100
        // Simplified: Growth * 182.5 * Rate / 100
        // NOTE: Inputs are in '000s, so NO conversion needed.

        const workingDays = 365 - 52 - 24 - parse(formData.manualHolidays); // 52 Suns, 24 Sats (2nd/4th)

        let calcIntDep = parse(formData.interestDeposits);
        let calcIntAdv = parse(formData.interestAdvances);

        // Prospects & Interest: Growth (Actual Rs) -> Prospects (000s), Interest (000s)
        let calcProspectsDep = parse(formData.prospectsDeposits);
        let calcProspectsAdv = parse(formData.prospectsAdvances);

        if (parse(formData.depositGrowth) > 0) {
            // Prospects = Growth * Working Days
            calcProspectsDep = (parse(formData.depositGrowth) * workingDays);

            if (parse(formData.costOfDeposit) > 0) {
                // Interest = (Growth * 182.5 * Rate/100)
                calcIntDep = (parse(formData.depositGrowth) * 182.5 * (parse(formData.costOfDeposit) / 100));
            }
        }

        if (parse(formData.advanceGrowth) > 0) {
            // Prospects = Growth * Working Days / 1000
            calcProspectsAdv = (parse(formData.advanceGrowth) * workingDays);

            if (parse(formData.yieldOnAdvance) > 0) {
                // Interest = (Growth * 182.5 * Rate/100) / 1000
                calcIntAdv = (parse(formData.advanceGrowth) * 182.5 * (parse(formData.yieldOnAdvance) / 100));
            }
        }

        // Rent Calculation: Monthly * 12 / 1000
        let calcRent = parse(formData.rentBuilding);
        if (parse(formData.monthlyRent) > 0) {
            calcRent = (parse(formData.monthlyRent) * 12);
        }

        const totalExp =
            parse(formData.stationeryMisc) +
            calcRent +
            calcIntDep +
            parse(formData.interestBorrowed);

        const totalInc =
            calcIntAdv +
            parse(formData.commission) +
            parse(formData.exchange) +
            parse(formData.interestLent);

        const profit = totalInc - totalExp;

        // Only update if values have changed to avoid infinite loop
        if (
            parse(formData.totalExpenditure) !== totalExp ||
            parse(formData.totalIncome) !== totalInc ||
            parse(formData.cumulativeProfit) !== profit ||
            (calcIntDep !== parse(formData.interestDeposits) && (parse(formData.depositGrowth) > 0 && parse(formData.costOfDeposit) > 0)) ||
            (calcIntAdv !== parse(formData.interestAdvances) && (parse(formData.advanceGrowth) > 0 && parse(formData.yieldOnAdvance) > 0)) ||
            (calcRent !== parse(formData.rentBuilding) && parse(formData.monthlyRent) > 0) ||
            (calcProspectsDep !== parse(formData.prospectsDeposits) && parse(formData.depositGrowth) > 0) ||
            (calcProspectsAdv !== parse(formData.prospectsAdvances) && parse(formData.advanceGrowth) > 0)
        ) {
            setFormData(prev => ({
                ...prev,
                interestDeposits: (parse(prev.depositGrowth) > 0 && parse(prev.costOfDeposit) > 0) ? calcIntDep.toFixed(2) : prev.interestDeposits,
                interestAdvances: (parse(prev.advanceGrowth) > 0 && parse(prev.yieldOnAdvance) > 0) ? calcIntAdv.toFixed(2) : prev.interestAdvances,
                rentBuilding: (parse(prev.monthlyRent) > 0) ? calcRent.toFixed(2) : prev.rentBuilding,
                prospectsDeposits: (parse(prev.depositGrowth) > 0) ? calcProspectsDep.toFixed(2) : prev.prospectsDeposits,
                prospectsAdvances: (parse(prev.advanceGrowth) > 0) ? calcProspectsAdv.toFixed(2) : prev.prospectsAdvances,
                totalExpenditure: totalExp.toFixed(2),
                totalIncome: totalInc.toFixed(2),
                cumulativeProfit: profit.toFixed(2)
            }));
        }
    }, [
        formData.stationeryMisc,
        formData.rentBuilding,
        formData.interestDeposits,
        formData.interestBorrowed,
        formData.estCharges, // Added back explicitly if needed even if not in calculation, but good for completeness to avoid stale closure warnings though not used
        formData.interestAdvances,
        formData.commission,
        formData.exchange,
        formData.interestLent,
        formData.totalExpenditure,
        formData.totalIncome,
        formData.cumulativeProfit,
        formData.depositGrowth,
        formData.costOfDeposit,
        formData.advanceGrowth,
        formData.yieldOnAdvance,
        formData.monthlyRent,
        formData.manualHolidays,
        formData.prospectsDeposits,
        formData.prospectsAdvances
    ]);

    const handleSave = async (status = 'draft', silent = false) => {
        const dataToSave = { ...formData, status };
        if (formData.id) {
            updateBranchSurvey(formData.id, dataToSave);
            if (!silent) alert(`Report saved as ${status === 'draft' ? 'Draft' : 'Final'}!`);
        } else {
            const newItem = await addBranchSurvey(dataToSave);
            setFormData(prev => ({ ...prev, id: newItem.id }));
            if (!silent) alert(`Report saved as ${status === 'draft' ? 'Draft' : 'Final'}!`);
        }
        if (status === 'final' && onBack) onBack();
    };

    const handleCurrencyBlur = (field, value) => {
        if (!value) return;
        // Strip existing non-numeric (except dot/minus) to get clean number
        const numeric = String(value).replace(/[^\d.-]/g, '');
        if (numeric) {
            setFormData(prev => ({ ...prev, [field]: `₹ ${numeric}` }));
        }
    };

    return (
        <div className="page-container" style={{ paddingBottom: '5rem' }}>
            <div className="page-header noprint" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {onBack && <button className="btn btn-outline" onClick={onBack}>← Back</button>}
                    <h1 className="page-title">{initialData ? 'Edit Survey Report' : 'New Survey Report'}</h1>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button type="button" className="btn btn-outline" onClick={(e) => { e.preventDefault(); handleSave('draft'); }} style={{ borderColor: '#6b7280', color: '#6b7280' }}>
                        Draft
                    </button>
                    <button type="button" className="btn btn-success" onClick={(e) => { e.preventDefault(); handleSave('final'); }} style={{ backgroundColor: '#10b981', color: 'white', borderColor: '#10b981' }}>
                        Save Report
                    </button>
                    <button
                        className={`btn ${viewMode === 'edit' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setViewMode('edit')}
                    >
                        ✏️ Edit Data
                    </button>

                    <button
                        className={`btn ${viewMode === 'preview' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setViewMode('preview')}
                    >
                        📄 Preview Report
                    </button>
                    {viewMode === 'preview' && (
                        <button className="btn btn-secondary" onClick={() => window.print()}>
                            🖨️ Print
                        </button>
                    )}
                </div>
            </div>

            {/* Content Wrapper handling Split View */}
            <div style={viewMode === 'split' ? { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', alignItems: 'start' } : {}}>

                {(viewMode === 'edit' || viewMode === 'split') && (
                    <div className="card form-container" style={{ maxWidth: viewMode === 'split' ? '100%' : '1000px', margin: '0 auto', height: viewMode === 'split' ? '80vh' : 'auto', overflowY: viewMode === 'split' ? 'auto' : 'visible' }}>

                        {/* Stepper Progress */}
                        <div className="stepper mb-6">
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                {steps.map((s, i) => (
                                    <div key={i}
                                        onClick={() => setCurrentStep(i)}
                                        style={{
                                            cursor: 'pointer',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            opacity: currentStep === i ? 1 : 0.5,
                                            fontWeight: currentStep === i ? 'bold' : 'normal',
                                            color: currentStep === i ? '#2563eb' : '#6b7280'
                                        }}
                                    >
                                        <div style={{
                                            width: '30px',
                                            height: '30px',
                                            borderRadius: '50%',
                                            background: currentStep === i ? '#2563eb' : '#e5e7eb',
                                            color: currentStep === i ? 'white' : '#6b7280',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            marginBottom: '0.25rem'
                                        }}>
                                            {i + 1}
                                        </div>
                                        <span style={{ fontSize: '0.8rem' }}>{s.title}</span>
                                    </div>
                                ))}
                            </div>
                            <div style={{ height: '4px', background: '#e5e7eb', borderRadius: '2px', position: 'relative' }}>
                                <div style={{
                                    height: '100%',
                                    background: '#2563eb',
                                    borderRadius: '2px',
                                    width: `${((currentStep) / (steps.length - 1)) * 100}%`,
                                    transition: 'width 0.3s ease'
                                }}></div>
                            </div>
                        </div>

                        {/* Section 1: General Info */}
                        {currentStep === 0 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>📋 General Information</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="grid-3">
                                            <div className="form-group">
                                                <label className="label">Region</label>
                                                <input className="input" value={formData.region} onChange={e => handleChange('region', e.target.value)} placeholder="e.g. Madurai" />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Report Date</label>
                                                <input type="date" className="input" value={formData.date} onChange={e => handleChange('date', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Application Type</label>
                                                <select className="input" value={formData.applicationType} onChange={e => handleChange('applicationType', e.target.value)}>
                                                    <option value="new">Open New Place</option>
                                                    <option value="change">Change Location</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 2: Application Details */}
                        {currentStep === 1 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>📝 Application Details</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="form-group">
                                            <label className="label">Full Application Text</label>
                                            <div className="note">"We apply to open a new place at <b>[Location]</b> existing from <b>[From]</b> to <b>[To]</b>..."</div>
                                            <div className={formData.applicationType === 'change' ? "grid-2" : ""}>
                                                {formData.applicationType === 'new' && (
                                                    <input className="input" placeholder="New Location" value={formData.applicationLocation} onChange={e => handleChange('applicationLocation', e.target.value)} style={{ width: '100%' }} />
                                                )}
                                                {formData.applicationType === 'change' && (
                                                    <>
                                                        <input className="input" placeholder="Existing From" value={formData.applicationFrom} onChange={e => handleChange('applicationFrom', e.target.value)} />
                                                        <input className="input" placeholder="Existing To" value={formData.applicationTo} onChange={e => handleChange('applicationTo', e.target.value)} />
                                                    </>
                                                )}
                                            </div>
                                        </div>

                                        <div className="grid-2 mt-4">
                                            <div className="form-group">
                                                <label className="label">Region Name</label>
                                                <input className="input" value={formData.regionName} onChange={e => handleChange('regionName', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Report Date</label>
                                                <input className="input" value={formData.reportDate} onChange={e => handleChange('reportDate', e.target.value)} placeholder="DD/MM/YYYY" />
                                            </div>
                                        </div>

                                        <div className="grid-2 mt-4">
                                            <div className="sub-section">
                                                <h4 className="sub-header">Applicant (SRM/CRM)</h4>
                                                <div className="form-group">
                                                    <label className="label">Name</label>
                                                    <input className="input" value={formData.applicantName} onChange={e => handleChange('applicantName', e.target.value)} />
                                                </div>
                                                <div className="form-group">
                                                    <label className="label">Designation</label>
                                                    <select className="input" value={formData.applicantDesignation} onChange={e => handleChange('applicantDesignation', e.target.value)}>
                                                        <option>Senior Regional Manager</option>
                                                        <option>Chief Regional Manager</option>
                                                        <option>General Manager</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div className="sub-section">
                                                <h4 className="sub-header">Surveyor</h4>
                                                <div className="form-group">
                                                    <label className="label">Name</label>
                                                    <input className="input" value={formData.surveyorName} onChange={e => handleChange('surveyorName', e.target.value)} />
                                                </div>
                                                <div className="form-group">
                                                    <label className="label">Designation</label>
                                                    <input className="input" value={formData.surveyorDesignation} onChange={e => handleChange('surveyorDesignation', e.target.value)} />
                                                </div>
                                                <div className="form-group">
                                                    <label className="label">Branch</label>
                                                    <input className="input" value={formData.surveyorBranch} onChange={e => handleChange('surveyorBranch', e.target.value)} />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 3: Proposed Office */}
                        {currentStep === 2 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>🏢 Proposed Office</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="grid-2">
                                            <div className="question-card">
                                                <label>2(a) Name of City/Town</label>
                                                <input className="input" value={formData.proposedName} onChange={e => handleChange('proposedName', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>2(b) Locality/Location</label>
                                                <input className="input" value={formData.proposedLocation} onChange={e => handleChange('proposedLocation', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>2(b)(i) Revenue Centre</label>
                                                <input className="input" value={formData.proposedRevenueCentre} onChange={e => handleChange('proposedRevenueCentre', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>2(c)(i) Block</label>
                                                <input className="input" value={formData.proposedBlock} onChange={e => handleChange('proposedBlock', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>2(c)(ii) Tehsil/Taluk</label>
                                                <input className="input" value={formData.proposedTehsil} onChange={e => handleChange('proposedTehsil', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>2(c)(v) PIN Code</label>
                                                <input className="input" value={formData.proposedPin} onChange={e => handleChange('proposedPin', e.target.value)} />
                                            </div>
                                        </div>
                                        <div className="grid-2 mt-4">
                                            <div className="question-card">
                                                <label>2(c)(iii) District</label>
                                                <div className="input-group-row">
                                                    <input className="input flex-1" value={formData.proposedDistrict} onChange={e => handleChange('proposedDistrict', e.target.value)} placeholder="Name" />
                                                    <input className="input w-24" value={formData.proposedDistrictGDP} onChange={e => handleChange('proposedDistrictGDP', e.target.value)} placeholder="GDP %" />
                                                </div>
                                            </div>
                                            <div className="question-card">
                                                <label>2(c)(iv) State</label>
                                                <div className="input-group-row">
                                                    <input className="input flex-1" value={formData.proposedState} onChange={e => handleChange('proposedState', e.target.value)} placeholder="Name" />
                                                    <input className="input w-24" value={formData.proposedStateGDP} onChange={e => handleChange('proposedStateGDP', e.target.value)} placeholder="GDP %" />
                                                </div>
                                            </div>
                                        </div>
                                        <div className="form-group mt-4">
                                            <label className="label">2(d) Status of Proposed Office</label>
                                            <select className="input" value={formData.proposedStatus} onChange={e => handleChange('proposedStatus', e.target.value)}>
                                                <option>Branch</option>
                                                <option>Specialised Branch</option>
                                                <option>Extension Counter</option>
                                                <option>Satellite Office</option>
                                                <option>Service Branch</option>
                                                <option>Processing Centre</option>
                                                <option>Administrative Office</option>
                                            </select>
                                        </div>
                                        <div className="grid-2 mt-4">
                                            <div className="form-group">
                                                <label className="label">2(e) Banks in centre</label>
                                                <textarea className="input" rows="2" value={formData.existingBranches} onChange={e => handleChange('existingBranches', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">2(f) Dist. to nearest bank</label>
                                                <textarea className="input" rows="2" value={formData.nearestBankDistance} onChange={e => handleChange('nearestBankDistance', e.target.value)} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 4: Competitor Analysis */}
                        {currentStep === 3 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>📊 Competitor Analysis (2g)</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="form-group mb-4">
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                <input
                                                    type="checkbox"
                                                    id="competitorApplicable"
                                                    checked={!formData.competitorAnalysisApplicable}
                                                    onChange={e => handleChange('competitorAnalysisApplicable', !e.target.checked)}
                                                    style={{ width: '20px', height: '20px' }}
                                                />
                                                <label htmlFor="competitorApplicable" className="label" style={{ marginBottom: 0, cursor: 'pointer' }}>
                                                    Mark as Not Applicable (Strikethrough in Report)
                                                </label>
                                            </div>
                                        </div>

                                        <div className="table-wrapper" style={{ opacity: formData.competitorAnalysisApplicable ? 1 : 0.5, pointerEvents: formData.competitorAnalysisApplicable ? 'auto' : 'none' }}>
                                            <table className="input-table">
                                                <thead>
                                                    <tr>
                                                        <th>No</th>
                                                        <th>Bank</th>
                                                        <th>Centre</th>
                                                        <th>Dep (amt)</th>
                                                        <th>Dep (no)</th>
                                                        <th>Adv (amt)</th>
                                                        <th>Adv (no)</th>
                                                        <th>Biz Mix</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {formData.competitors.map((row, i) => (
                                                        <tr key={i}>
                                                            <td>{i + 1}</td>
                                                            <td><input className="input-sm" value={row.bankName} onChange={e => handleCompetitorChange(i, 'bankName', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.centreName} onChange={e => handleCompetitorChange(i, 'centreName', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.deposits} onChange={e => handleCompetitorChange(i, 'deposits', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.depositsNo} onChange={e => handleCompetitorChange(i, 'depositsNo', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.advances} onChange={e => handleCompetitorChange(i, 'advances', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.advancesNo} onChange={e => handleCompetitorChange(i, 'advancesNo', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.businessMix} onChange={e => handleCompetitorChange(i, 'businessMix', e.target.value)} /></td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 5: Command Area & Production */}
                        {currentStep === 4 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>🌍 Command Area & Production</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="grid-2">
                                            <div className="form-group">
                                                <label className="label">3. Previous Applications</label>
                                                <textarea className="input" rows="3" value={formData.previousApplications} onChange={e => handleChange('previousApplications', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">4. Reason for Office</label>
                                                <textarea className="input" rows="3" value={formData.reasonForOffice} onChange={e => handleChange('reasonForOffice', e.target.value)} />
                                            </div>
                                        </div>
                                        <div className="grid-4 mt-4">
                                            <div className="form-group">
                                                <label className="label">4(i) Population</label>
                                                <input className="input" value={formData.population} onChange={e => handleChange('population', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Radius</label>
                                                <input className="input" value={formData.commandRadius} onChange={e => handleChange('commandRadius', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Command Pop.</label>
                                                <input className="input" value={formData.commandPopulation} onChange={e => handleChange('commandPopulation', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">No. Villages</label>
                                                <input className="input" value={formData.commandVillages} onChange={e => handleChange('commandVillages', e.target.value)} />
                                            </div>
                                        </div>

                                        <h4 className="sub-header mt-4">4(iii) Production Data</h4>
                                        <div className="table-wrapper">
                                            <table className="input-table">
                                                <thead>
                                                    <tr>
                                                        <th>No</th>
                                                        <th>Commodity</th>
                                                        <th>Prod Vol</th>
                                                        <th>Prod Val</th>
                                                        <th>Imp Vol</th>
                                                        <th>Imp Val</th>
                                                        <th>Exp Vol</th>
                                                        <th>Exp Val</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {formData.production.map((row, i) => (
                                                        <tr key={i}>
                                                            <td>{i + 1}</td>
                                                            <td><input className="input-sm" value={row.commodity} onChange={e => handleProductionChange(i, 'commodity', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.prodVol} onChange={e => handleProductionChange(i, 'prodVol', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.prodVal} onChange={e => handleProductionChange(i, 'prodVal', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.impVol} onChange={e => handleProductionChange(i, 'impVol', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.impVal} onChange={e => handleProductionChange(i, 'impVal', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.expVol} onChange={e => handleProductionChange(i, 'expVol', e.target.value)} /></td>
                                                            <td><input className="input-sm" value={row.expVal} onChange={e => handleProductionChange(i, 'expVal', e.target.value)} /></td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 6: Financials */}
                        {currentStep === 5 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>💰 Prospects & Financials</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="grid-2">
                                            <div className="form-group">
                                                <label className="label">4(iv) Development Schemes</label>
                                                <textarea className="input" rows="2" value={formData.developmentSchemes} onChange={e => handleChange('developmentSchemes', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">4(v) Inadequacy Reason</label>
                                                <textarea className="input" rows="2" value={formData.inadequateReason} onChange={e => handleChange('inadequateReason', e.target.value)} />
                                            </div>
                                        </div>
                                        <div className="grid-2 mt-4">
                                            <div className="form-group">
                                                <label className="label">Prospects Deposits</label>
                                                <input className="input" value={formData.prospectsDeposits} onChange={e => handleChange('prospectsDeposits', e.target.value)} />
                                            </div>
                                            <div className="form-group">
                                                <label className="label">Prospects Advances</label>
                                                <input className="input" value={formData.prospectsAdvances} onChange={e => handleChange('prospectsAdvances', e.target.value)} />
                                            </div>
                                        </div>

                                        <div className="grid-2 mt-4 gap-6">
                                            {/* Calculator Inputs */}
                                            <div className="bg-blue-50 p-4 rounded-lg col-span-2">
                                                <div className="mb-4 font-bold text-blue-800 border-b border-blue-200 pb-2">
                                                    📊 Projections & Calculators (Inputs in '000s)
                                                </div>

                                                {/* Working Days Config */}
                                                <div className="grid-3 gap-6 mb-4">
                                                    <div className="form-group">
                                                        <label className="label">Manual Holidays</label>
                                                        <input className="input" type="number" value={formData.manualHolidays} onChange={e => handleChange('manualHolidays', e.target.value)} placeholder="0" />
                                                        <small className="text-gray-500">Less: Sundays (52), 2nd/4th Sats (24)</small>
                                                    </div>
                                                    <div className="form-group">
                                                        <label className="label">Working Days</label>
                                                        <div className="input bg-gray-100 text-gray-700 font-semibold">
                                                            {365 - 52 - 24 - (parseFloat(formData.manualHolidays) || 0)} Days
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="grid-4 gap-6">
                                                    <div className="form-group"><label className="label">Growth/Day (Dep)</label><input className="input" value={formData.depositGrowth} onChange={e => handleChange('depositGrowth', e.target.value)} onBlur={e => handleCurrencyBlur('depositGrowth', e.target.value)} placeholder="(000s)" /></div>
                                                    <div className="form-group"><label className="label">Cost of Dep (%)</label><input className="input" value={formData.costOfDeposit} onChange={e => handleChange('costOfDeposit', e.target.value)} placeholder="%" /></div>
                                                    <div className="form-group"><label className="label">Growth/Day (Adv)</label><input className="input" value={formData.advanceGrowth} onChange={e => handleChange('advanceGrowth', e.target.value)} onBlur={e => handleCurrencyBlur('advanceGrowth', e.target.value)} placeholder="(000s)" /></div>
                                                    <div className="form-group"><label className="label">Yield on Adv (%)</label><input className="input" value={formData.yieldOnAdvance} onChange={e => handleChange('yieldOnAdvance', e.target.value)} placeholder="%" /></div>
                                                    <div className="form-group"><label className="label">Est. Monthly Rent</label><input className="input" value={formData.monthlyRent} onChange={e => handleChange('monthlyRent', e.target.value)} onBlur={e => handleCurrencyBlur('monthlyRent', e.target.value)} placeholder="(000s)" /></div>
                                                </div>
                                            </div>

                                            <div className="bg-gray-50 p-4 rounded-lg">
                                                <h4 className="sub-header text-red-600">📉 Est. Annual Expenditure</h4>
                                                <div className="form-group"><label className="label">Est. Charges</label><input className="input" value={formData.estCharges} onChange={e => handleChange('estCharges', e.target.value)} onBlur={e => handleCurrencyBlur('estCharges', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Stationery</label><input className="input" value={formData.stationeryMisc} onChange={e => handleChange('stationeryMisc', e.target.value)} onBlur={e => handleCurrencyBlur('stationeryMisc', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Rent</label><input className="input" value={formData.rentBuilding} onChange={e => handleChange('rentBuilding', e.target.value)} onBlur={e => handleCurrencyBlur('rentBuilding', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Int. on Deposits</label><input className="input" value={formData.interestDeposits} onChange={e => handleChange('interestDeposits', e.target.value)} onBlur={e => handleCurrencyBlur('interestDeposits', e.target.value)} /></div>
                                                <div className="input-group-row">
                                                    <div className="form-group flex-1"><label className="label">Int. Borrowed</label><input className="input w-full" value={formData.interestBorrowed} onChange={e => handleChange('interestBorrowed', e.target.value)} onBlur={e => handleCurrencyBlur('interestBorrowed', e.target.value)} /></div>
                                                    <div className="form-group w-24"><label className="label">Rate %</label><input className="input w-full" value={formData.interestBorrowedRate} onChange={e => handleChange('interestBorrowedRate', e.target.value)} /></div>
                                                </div>
                                                <div className="form-group"><label className="label font-bold">Total Expenditure</label><input className="input font-bold" value={formData.totalExpenditure} readOnly placeholder="Auto-calculated" /></div>
                                            </div>
                                            <div className="bg-gray-50 p-4 rounded-lg">
                                                <h4 className="sub-header text-green-600">📈 Est. Annual Income</h4>
                                                <div className="form-group"><label className="label">Int. on Advances</label><input className="input" value={formData.interestAdvances} onChange={e => handleChange('interestAdvances', e.target.value)} onBlur={e => handleCurrencyBlur('interestAdvances', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Commission</label><input className="input" value={formData.commission} onChange={e => handleChange('commission', e.target.value)} onBlur={e => handleCurrencyBlur('commission', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Exchange</label><input className="input" value={formData.exchange} onChange={e => handleChange('exchange', e.target.value)} onBlur={e => handleCurrencyBlur('exchange', e.target.value)} /></div>
                                                <div className="form-group"><label className="label">Int. on Lent Fund</label><input className="input" value={formData.interestLent} onChange={e => handleChange('interestLent', e.target.value)} onBlur={e => handleCurrencyBlur('interestLent', e.target.value)} /></div>
                                                <div className="form-group"><label className="label font-bold">Total Income</label><input className="input font-bold" value={formData.totalIncome} readOnly placeholder="Auto-calculated" /></div>
                                                <div className="form-group bg-green-100 p-2 rounded mt-4"><label className="label font-bold text-green-800">Cumulative Profit</label><input className="input font-bold text-green-800" value={formData.cumulativeProfit} readOnly placeholder="Income - Expenditure" /></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Section 7: Logistics & Misc */}
                        {currentStep === 6 && (
                            <div className="dashboard-layout">
                                <div className="section-card col-span-full">
                                    <div className="section-header">
                                        <h3>🚚 Logistics & Misc</h3>
                                    </div>
                                    <div className="section-body">
                                        <div className="form-group">
                                            <label className="label">5. Change Location Details</label>
                                            <textarea className="input" rows="2" value={formData.changeLocationDetails} onChange={e => handleChange('changeLocationDetails', e.target.value)} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">6. Expenditure Details</label>
                                            <textarea className="input" rows="2" value={formData.expenditureDetails} onChange={e => handleChange('expenditureDetails', e.target.value)} />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">7. Other Particulars</label>
                                            <textarea className="input" rows="2" value={formData.otherParticulars} onChange={e => handleChange('otherParticulars', e.target.value)} />
                                        </div>
                                        <div className="grid-3 mt-4">
                                            <div className="question-card">
                                                <label>8. Brick & Mortar?</label>
                                                <input className="input" value={formData.brickMortarAvailable} onChange={e => handleChange('brickMortarAvailable', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>9. Leased Line?</label>
                                                <input className="input" value={formData.networkLeasedLine} onChange={e => handleChange('networkLeasedLine', e.target.value)} />
                                            </div>
                                            <div className="question-card">
                                                <label>10. Datacard?</label>
                                                <input className="input" value={formData.networkDataCard} onChange={e => handleChange('networkDataCard', e.target.value)} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                        )}

                        {/* Stepper Navigation Controls */}
                        <div className="flex justify-between mt-6 pt-4 border-t">
                            <button
                                className="btn btn-outline"
                                onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
                                disabled={currentStep === 0}
                            >
                                Previous
                            </button>

                            {currentStep < steps.length - 1 ? (
                                <button
                                    className="btn btn-primary"
                                    onClick={async () => {
                                        await handleSave('draft', true);
                                        setCurrentStep(prev => Math.min(steps.length - 1, prev + 1));
                                    }}
                                >
                                    Next Section
                                </button>
                            ) : (
                                <button
                                    className="btn btn-success"
                                    onClick={() => handleSave('final')}
                                >
                                    Submit Report
                                </button>
                            )}
                        </div>

                    </div>
                )}

                {(viewMode === 'preview' || viewMode === 'split') && (
                    <div id="printable-content" className="card report-container" style={{ height: viewMode === 'split' ? '80vh' : 'auto', overflowY: viewMode === 'split' ? 'auto' : 'visible' }}>
                        {/* Header from LetterForm */}
                        <div className="form-content">

                            <div className="print-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid black', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                                <div>{lh?.logo && <img src={lh.logo} alt="Logo" style={{ height: '80px' }} />}</div>
                                <div style={{ textAlign: 'right', color: '#254aa0' }}>
                                    <h1 style={{ fontSize: '16pt', fontWeight: 'bold', margin: '0 0 2px 0', lineHeight: '1.2' }}>क्षेत्रीय कार्यालय दिण्डुक्कल</h1>
                                    <h2 style={{ fontSize: '13pt', fontFamily: 'Arial', fontWeight: 'bold', margin: 0 }}>Regional Office Dindigul</h2>
                                </div>
                            </div>

                            <div className="center bold" style={{ fontSize: '1.2rem', textDecoration: 'underline', marginBottom: '1.5rem' }}>
                                {formData.applicationType === 'new' ? 'SURVEY REPORT FOR OPENING OF A NEW BRANCH' : 'SURVEY REPORT FOR CHANGING THE LOCATION OF AN EXISTING BRANCH'}
                            </div>

                            <div style={{ textAlign: 'center', fontWeight: 'bold', marginBottom: '1rem', fontFamily: 'Arial, sans-serif' }}>
                                Region: {formData.regionName || 'Dindigul'}
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', fontFamily: 'Arial, sans-serif' }}>
                                <div>
                                    <div style={{ fontWeight: 'bold' }}>To:</div>
                                    <div style={{ marginLeft: '0px', fontWeight: 'bold' }}>
                                        The General Manager<br />
                                        Indian Overseas Bank<br />
                                        Planning Department<br />
                                        Central Office, Chennai
                                    </div>
                                </div>
                                <div style={{ fontWeight: 'bold' }}>
                                    Date: {formData.reportDate || new Date().toLocaleDateString('en-GB')}
                                </div>
                            </div>

                            <p>Dear Sir,</p>
                            <p>We hereby apply for permission to <span style={{ textDecoration: formData.applicationType !== 'new' ? 'line-through' : 'none' }}>open a new place of business</span> / <span style={{ textDecoration: formData.applicationType !== 'change' ? 'line-through' : 'none' }}>change the location</span> at <u>{formData.applicationLocation || '________________________'}</u> <span style={{ textDecoration: formData.applicationType === 'new' ? 'line-through' : 'none' }}>of an existing place of business from <u>{formData.applicationFrom || '_______'}</u> to <u>{formData.applicationTo || '_____'}</u></span> in terms of section 23 of the Banking Regulation Act, 1949. We give below the necessary information in the form prescribed for the purpose.</p>

                            <br />

                            <table className="header-table">
                                <tbody>
                                    <tr>
                                        <td width="40%">
                                            Recommended by,<br /><br /><br /><br />
                                            Name: <u>{formData.applicantName || '___________________'}</u><br />
                                            <strong>{formData.applicantDesignation || 'Senior Regional Manager / Chief Regional Manager / General Manager'}</strong>
                                        </td>
                                        <td width="20%" className="center" style={{ verticalAlign: 'bottom' }}>
                                            <div style={{ border: '1px solid black', height: '104px', width: '110px', margin: '0 auto', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', fontSize: '12px', paddingBottom: '10px', color: 'rgba(0,0,0,0.3)' }}>RO SEAL</div>
                                        </td>
                                        <td width="40%" style={{ textAlign: 'right' }}>
                                            <strong>Survey done by:</strong><br /><br /><br /><br />
                                            Name: <u>{formData.surveyorName || '___________________'}</u><br />
                                            Designation: <u>{formData.surveyorDesignation || '_____________'}</u><br />
                                            Branch: <u>{formData.surveyorBranch || '___________________'}</u>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            {/* Main Data Table */}
                            <table className="main-table">
                                <tbody>
                                    {/* Section 1 */}
                                    <tr>
                                        <td className="serial-col">1.</td>
                                        <td width="45%">Name of the banking company</td>
                                        <td width="50%"><strong>Indian Overseas Bank</strong></td>
                                    </tr>

                                    {/* Section 2 */}
                                    <tr>
                                        <td className="serial-col">2.</td>
                                        <td colSpan="2"><strong>Proposed office (Give the following information)</strong></td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (a)</td>
                                        <td>Name of city/town/village : (in case the place is known by more than one name, the relative information should also be furnished)</td>
                                        <td>{formData.proposedName}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (b)</td>
                                        <td>Name of locality/location</td>
                                        <td>{formData.proposedLocation}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (b)(i)</td>
                                        <td>Name of Revenue Centre</td>
                                        <td>{formData.proposedRevenueCentre}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)</td>
                                        <td>Name of :-</td>
                                        <td></td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)(i)</td>
                                        <td>Block</td>
                                        <td>{formData.proposedBlock}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)(ii)</td>
                                        <td>Tehsil / Taluk / Sub-District</td>
                                        <td>{formData.proposedTehsil}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)(iii)</td>
                                        <td>District</td>
                                        <td>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
                                                <div style={{ borderRight: '1px solid black', padding: '0 8px', fontWeight: 'bold', textDecoration: 'underline' }}>{formData.proposedDistrict}</div>
                                                <div style={{ padding: '0 8px', textAlign: 'center' }}>GDP% - {formData.proposedDistrictGDP}</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)(iv)</td>
                                        <td>State</td>
                                        <td>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
                                                <div style={{ borderRight: '1px solid black', padding: '0 8px', fontWeight: 'bold', textDecoration: 'underline' }}>{formData.proposedState}</div>
                                                <div style={{ padding: '0 8px', textAlign: 'center' }}>GDP% - {formData.proposedStateGDP}</div>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (c)(v)</td>
                                        <td>PIN Code of the centre</td>
                                        <td>{formData.proposedPin}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (d)</td>
                                        <td>Status of the proposed office</td>
                                        <td>{formData.proposedStatus}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (e)</td>
                                        <td>Name(s) of the Bank branch(es) functioning in the centre for which permission is applied for</td>
                                        <td>{formData.existingBranches}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">2 (f)</td>
                                        <td>The distance between the proposed office and the nearest existing commercial bank office together with the name of the bank and that of the Centre / locality</td>
                                        <td>{formData.nearestBankDistance}</td>
                                    </tr>
                                </tbody>
                            </table>

                            {/* Competitor Analysis Section */}
                            <div className="report-section page-break" style={{ position: 'relative', marginTop: '20px' }}>
                                <h3>2(g) Particulars of other Banks at the Centre:</h3>

                                <div className="na-container">
                                    <div className="na-content" style={{ opacity: !formData.competitorAnalysisApplicable ? 0.5 : 1 }}>
                                        <table className="main-table">
                                            <thead>
                                                <tr className="center bold">
                                                    <th rowSpan="2" className="serial-col">No.</th>
                                                    <th rowSpan="2">Name of Bank</th>
                                                    <th rowSpan="2">Name of Centre</th>
                                                    <th colSpan="2">Deposits</th>
                                                    <th colSpan="2">Advances</th>
                                                    <th rowSpan="2">Business Mix</th>
                                                </tr>
                                                <tr className="center bold">
                                                    <th>Amount</th>
                                                    <th>Accounts</th>
                                                    <th>Amount</th>
                                                    <th>Accounts</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {/* Empty Rows */}
                                                {[...Array(5)].map((_, i) => (
                                                    <tr key={i}>
                                                        <td className="serial-col">{i + 1}</td>
                                                        <td></td>
                                                        <td></td>
                                                        <td></td>
                                                        <td></td>
                                                        <td></td>
                                                        <td></td>
                                                        <td></td>
                                                    </tr>
                                                ))}
                                                {formData.competitors.map((row, i) => (
                                                    <tr key={`data-${i}`}>
                                                        <td className="serial-col">{i + 6}</td>
                                                        <td>{row.bankName}</td>
                                                        <td>{row.centreName}</td>
                                                        <td>{row.deposits}</td>
                                                        <td>{row.depositsNo}</td>
                                                        <td>{row.advances}</td>
                                                        <td>{row.advancesNo}</td>
                                                        <td>{row.businessMix}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    {!formData.competitorAnalysisApplicable && (
                                        <div className="na-overlay">
                                            <div style={{
                                                background: 'white',
                                                padding: '0.5rem 1rem',
                                                fontWeight: 'bold',
                                                fontSize: '1.2rem',
                                                border: '1px solid black',
                                                borderRadius: '4px'
                                            }}>
                                                NO BANK BRANCHES OPERATING
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Section 3 & 4 */}
                            <table className="main-table">
                                <tbody>
                                    <tr>
                                        <td className="serial-col">3</td>
                                        <td width="45%">Previous applications (Give particulars of applications, if any, previously made to the Reserve Bank in respect of the proposed place of business)</td>
                                        <td width="50%">{formData.previousApplications}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">4</td>
                                        <td>Reason for the proposed office:- (State detailed reasons for the proposed office and give statistical and other data, as under, which may have been collected for the proposed office)</td>
                                        <td>{formData.reasonForOffice}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">4 (i)</td>
                                        <td>Population of the place (2001 census)</td>
                                        <td>{formData.population}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">4 (ii)</td>
                                        <td><strong># Particulars of the command area (i.e. the area of operation of the proposed office)</strong></td>
                                        <td></td>
                                    </tr>
                                    <tr>
                                        <td></td>
                                        <td>(a) Approx. radius of the command area</td>
                                        <td>{formData.commandRadius}</td>
                                    </tr>
                                    <tr>
                                        <td></td>
                                        <td>(b) Population</td>
                                        <td>{formData.commandPopulation}</td>
                                    </tr>
                                    <tr>
                                        <td></td>
                                        <td>(c) No. of villages in the command area</td>
                                        <td>{formData.commandVillages}</td>
                                    </tr>
                                </tbody>
                            </table>

                            {/* Production Table */}
                            <table className="main-table">
                                <tbody>
                                    <tr>
                                        <td colSpan="8">
                                            <strong>4 (iii) The volume and value of agricultural, mineral and industrial production and imports and exports of the area of operation of the proposed office as under:</strong>
                                        </td>
                                    </tr>
                                    <tr className="center bold">
                                        <td rowSpan="2" className="serial-col">No.</td>
                                        <td rowSpan="2">Commodity</td>
                                        <td colSpan="2">Production</td>
                                        <td colSpan="2">Imports</td>
                                        <td colSpan="2">Exports</td>
                                    </tr>
                                    <tr className="center bold">
                                        <td>Volume</td>
                                        <td>Value (Rs. In lakhs)</td>
                                        <td>Volume</td>
                                        <td>Value (Rs. In lakhs)</td>
                                        <td>Volume</td>
                                        <td>Value (Rs. In lakhs)</td>
                                    </tr>
                                    {/* Empty Rows */}
                                    {formData.production.map((row, i) => (
                                        <tr key={i}>
                                            <td className="serial-col">{i + 1}</td>
                                            <td>{row.commodity}</td>
                                            <td>{row.prodVol}</td>
                                            <td>{row.prodVal}</td>
                                            <td>{row.impVol}</td>
                                            <td>{row.impVal}</td>
                                            <td>{row.expVol}</td>
                                            <td>{row.expVal}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            {/* Development & Prospects */}
                            <table className="main-table">
                                <tbody>
                                    <tr>
                                        <td className="serial-col">4 (iv)</td>
                                        <td width="45%">If there are schemes for agricultural, mineral or industrial development give details of the same and their probable effect on the volume and value of the present production, imports & exports</td>
                                        <td width="50%">{formData.developmentSchemes}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">4 (v)</td>
                                        <td>If the existing banking facilities are considered inadequate, give reasons</td>
                                        <td>{formData.inadequateReason}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">4 (vi)</td>
                                        <td>
                                            <strong>Prospects :</strong> (Give an estimate of the minimum business which the banking company expects to attract at the proposed place of business within 12 months)
                                        </td>
                                        <td>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', border: '1px solid black' }}>
                                                <div style={{ borderRight: '1px solid black', textAlign: 'center' }}>
                                                    <div style={{ borderBottom: '1px solid black', padding: '4px', background: '#f0f0f0', fontWeight: 'bold' }}>Deposits<br />Rs. (000s)</div>
                                                    <div style={{ padding: '8px' }}>{formData.prospectsDeposits}</div>
                                                </div>
                                                <div style={{ textAlign: 'center' }}>
                                                    <div style={{ borderBottom: '1px solid black', padding: '4px', background: '#f0f0f0', fontWeight: 'bold' }}>Advances<br />Rs. (000s)</div>
                                                    <div style={{ padding: '8px' }}>{formData.prospectsAdvances}</div>
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            {/* Relocation & Expenditure */}
                            <table className="main-table">
                                <tbody>
                                    <tr>
                                        <td className="serial-col">5</td>
                                        <td width="45%">
                                            <strong>Change of location of an existing office :</strong><br />
                                            (Give the exact location of the office which is proposed to be closed and of the place to which it is proposed to be shifted giving particulars of the new location as in items (2), (3), (4))
                                        </td>
                                        <td width="50%">{formData.changeLocationDetails}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">6</td>
                                        <td colSpan="2">
                                            <strong>Expenditure :</strong> (State the amount already spent or proposed to be spent on staff, premises, furniture, stationery, advertising, etc., in connection with the proposed office. Also state the minimum income which the banking company expects to earn at the proposed office within 12 months)
                                            <div style={{ marginTop: '0.5rem' }}>{formData.expenditureDetails}</div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <table className="financial-table">
                                <tbody>
                                    <tr className="bold">
                                        <td width="70%">Estimate of Annual expenditure</td>
                                        <td width="30%">Amount Rs. (000s)</td>
                                    </tr>
                                    <tr>
                                        <td>a) Establishment charges</td>
                                        <td>{formData.estCharges}</td>
                                    </tr>
                                    <tr>
                                        <td>b) Stationery & Miscellaneous</td>
                                        <td>{formData.stationeryMisc}</td>
                                    </tr>
                                    <tr>
                                        <td>c) Rent & Building</td>
                                        <td>{formData.rentBuilding}</td>
                                    </tr>
                                    <tr>
                                        <td>d) Interest to be paid on deposits</td>
                                        <td>{formData.interestDeposits}</td>
                                    </tr>
                                    <tr>
                                        <td>e) Interest on funds borrowed from H.O. on {formData.interestBorrowedRate && `${formData.interestBorrowedRate}%`}</td>
                                        <td>{formData.interestBorrowed}</td>
                                    </tr>
                                    <tr className="bold">
                                        <td>TOTAL EXPENDITURE</td>
                                        <td>{formData.totalExpenditure}</td>
                                    </tr>
                                </tbody>
                            </table>

                            <table className="financial-table">
                                <tbody>
                                    <tr className="bold">
                                        <td width="70%">Estimated Annual Income</td>
                                        <td width="30%">Amount Rs. (000s)</td>
                                    </tr>
                                    <tr>
                                        <td>a) Interest on advances</td>
                                        <td>{formData.interestAdvances}</td>
                                    </tr>
                                    <tr>
                                        <td>b) Commission</td>
                                        <td>{formData.commission}</td>
                                    </tr>
                                    <tr>
                                        <td>c) Exchange</td>
                                        <td>{formData.exchange}</td>
                                    </tr>
                                    <tr>
                                        <td>d) Interest on funds lent to H.O.</td>
                                        <td>{formData.interestLent}</td>
                                    </tr>
                                    <tr className="bold">
                                        <td>TOTAL INCOME</td>
                                        <td>{formData.totalIncome}</td>
                                    </tr>
                                    <tr className="bold" style={{ backgroundColor: '#f0f0f0' }}>
                                        <td>Cumulative Profit for the first year</td>
                                        <td>{formData.cumulativeProfit}</td>
                                    </tr>
                                </tbody>
                            </table>

                            {/* Final Logistics */}
                            <table className="main-table">
                                <tbody>
                                    <tr>
                                        <td className="serial-col">7</td>
                                        <td width="45%">Other particulars : (Any additional facts which the branch may wish to adduce in support of its application)</td>
                                        <td width="50%">{formData.otherParticulars}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">8</td>
                                        <td>Is brick & mortar premises for commercial use available in the centre</td>
                                        <td>{formData.brickMortarAvailable}</td>
                                    </tr>
                                    <tr>
                                        <td className="serial-col">9</td>
                                        <td>Is network connectivity through BSNL / MTNL leased line available in the proposed centre</td>
                                        <td>{formData.networkLeasedLine}</td>
                                    </tr>
                                    <tr>
                                        <td>10</td>
                                        <td>Is network connectivity through datacard available in the proposed centre</td>
                                        <td>{formData.networkDataCard}</td>
                                    </tr>
                                </tbody>
                            </table>


                            {/* Footer Notes */}
                            <div className="note">
                                <p>***** The portion not applicable to be struck off.</p>
                                <p><strong>#</strong> The information need be furnished only in the case of applications for centres with a population of less than one lakh.</p>
                                <p><strong>Note:</strong></p>
                                <ul>
                                    <li>Item (5) is to be filled up if the application is for changing the location of an existing place of business.</li>
                                    <li>Survey has to be conducted by a senior official from Regional Office or nearby branch.</li>
                                    <li>Availability of suitable premises and network connectivity should also be ascertained especially in unbanked rural and semi urban centres.</li>
                                </ul>
                                <p style={{ border: '1px solid black', padding: '10px' }}>
                                    The business and profitability projections furnished in the survey report should not be done in a routine manner as a form-filling exercise. <strong>Please note that all branches should start making profits within the first 12 months of opening.</strong><br />
                                    All pages of this application must be authenticated with seal of Regional Office.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <style>{`
                .form-container {
                    padding: 0 !important;
                    background: transparent;
                    box-shadow: none;
                }
                .dashboard-layout {
                    display: grid;
                    grid-template-columns: repeat(12, 1fr);
                    gap: 1.5rem;
                }
                .section-card {
                    background: white;
                    border-radius: 0.5rem;
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                    overflow: hidden;
                    border: 1px solid #e5e7eb;
                }
                .col-span-full { grid-column: span 12 / span 12; }
                .section-header {
                    background-color: #f8fafc;
                    padding: 1rem 1.5rem;
                    border-bottom: 1px solid #e5e7eb;
                }
                .section-header h3 {
                    margin: 0;
                    font-size: 1.125rem;
                    font-weight: 600;
                    color: #1e293b;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                .section-body { padding: 1.5rem; }
                .form-group { margin-bottom: 1rem; }
                .label { display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem; }
                .input {
                    display: block;
                    width: 100%;
                    border-radius: 0.375rem;
                    border: 1px solid #d1d5db;
                    padding: 0.5rem;
                    font-size: 0.875rem;
                    line-height: 1.25rem;
                }
                .input:focus {
                    outline: 2px solid transparent;
                    outline-offset: 2px;
                    border-color: #2563eb;
                    box-shadow: 0 0 0 2px #bfdbfe;
                }
                .sub-header {
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: #4b5563;
                    margin-bottom: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                .sub-section {
                    background-color: #f9fafb;
                    padding: 1rem;
                    border-radius: 0.375rem;
                    border: 1px solid #e5e7eb;
                }
                .question-card {
                    background-color: #ffffff;
                    padding: 1rem;
                    border-radius: 0.25rem;
                    border: 1px solid #d1d5db;
                    width: 100%;
                }
                .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
                .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; }
                .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1.5rem; }
                .mt-4 { margin-top: 1rem; }
                .gap-6 { gap: 1.5rem; }
                .bg-gray-50 { background-color: #f9fafb; }
                .bg-green-100 { background-color: #dcfce7; }
                .text-red-600 { color: #dc2626; }
                .text-green-600 { color: #166534; }
                .text-green-800 { color: #166534; }
                .font-bold { font-weight: 700; }
                .rounded-lg { border-radius: 0.5rem; }
                .rounded { border-radius: 0.25rem; }
                .p-4 { padding: 1rem; }
                .p-2 { padding: 0.5rem; }
                .w-24 { width: 6rem; }
                .w-full { width: 100%; }
                .flex-1 { flex: 1; }
                .input-group-row { display: flex; gap: 0.5rem; }
                .table-wrapper {
                    border: 1px solid #e5e7eb;
                    border-radius: 0.5rem;
                    overflow: hidden;
                }
                .input-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .input-table th {
                    background: #f8fafc;
                    padding: 0.75rem;
                    text-align: left;
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: #475569;
                    border-bottom: 1px solid #e5e7eb;
                }
                .input-table td {
                    padding: 0.5rem;
                    border-bottom: 1px solid #f1f5f9;
                }
                .note {
                    background: #eff6ff; 
                    color: #1e40af; 
                    padding: 0.5rem; 
                    border-radius: 4px; 
                    font-size: 0.8rem; 
                    margin-bottom: 1rem; 
                    font-style: italic;
                    border: 1px solid #dbeafe;
                }

                /* Report Styles */
                .report-container {
                    background: white;
                    padding: 40px;
                    max-width: 900px;
                    margin: 0 auto;
                }
                .form-content {
                    font-family: 'Century Gothic', sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                    color: black;
                }
                .form-content .print-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid black; padding-bottom: 1rem; margin-bottom: 1.5rem; }
                h2, h3 { text-align: center; text-decoration: underline; }
                .header-table, .main-table, .financial-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                .main-table th, .main-table td, .financial-table th, .financial-table td { border: 1px solid black; padding: 5px; vertical-align: top; }
                .text-right { text-align: right; }
                .center { text-align: center; }
                .bold { font-weight: bold; }
                .input-sm { width: 100%; padding: 0.25rem; border: none; background: transparent; }
                
                .serial-col {
                    white-space: nowrap !important;
                    width: 1% !important;
                    min-width: 60px !important;
                    text-align: center;
                    vertical-align: top;
                    padding: 4px !important;
                }
                @page { margin: 10mm; }
                .na-container {
                    display: grid;
                    grid-template-columns: 1fr;
                    margin-bottom: 20px;
                }
                .na-content .main-table { margin-bottom: 0 !important; }
                .na-content {
                    grid-row: 1;
                    grid-column: 1;
                }
                .na-overlay {
                    grid-row: 1;
                    grid-column: 1;
                    z-index: 10;
                    pointer-events: none;
                    background-image: repeating-linear-gradient(
                        45deg,
                        transparent,
                        transparent 10px,
                        rgba(0, 0, 0, 0.3) 10px,
                        rgba(0, 0, 0, 0.3) 20px
                    );
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                @media print {
                    .na-overlay {
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }
                    .noprint, .sidebar, .page-header { display: none !important; }
                    .page-container { padding: 0 !important; margin: 0 !important; }
                    .card { box-shadow: none !important; border: none !important; padding: 0 !important; }
                    body { margin: 0; padding: 0; background: white; }
                    .report-container { 
                        max-width: 100% !important; 
                        margin: 0 !important; 
                        width: 100% !important; 
                        padding: 0 !important;
                        min-height: 0 !important;
                    }
                    html, body {
                        height: auto !important;
                        overflow: visible !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .page-container {
                        padding-bottom: 0 !important;
                        margin: 0 !important;
                        display: block !important;
                        width: 100% !important;
                    }
                    .note {
                        margin-bottom: 0 !important;
                        page-break-inside: avoid;
                    }
                    /* Ensure headers/footers dont force breaks unnecessarily */
                    h1, h2, h3, h4, p {
                        margin-top: 0;
                    }
                    .report-container * { visibility: visible; }
                    .page-break { page-break-before: always !important; }
                }
            `}</style>
        </div >
    );
};

export default BranchOpeningSurveyReport;
