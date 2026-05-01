import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { useData } from '../context/DataContext';
import fileList from '../data/advances_files.json';

const BranchPerformance = () => {
    const { branchPerformance, updateBranchPerformance, branches } = useData();
    const [activeTab, setActiveTab] = useState('sanctions');
    const [loading, setLoading] = useState(false);
    const [sanctionsData, setSanctionsData] = useState([]);
    const [lastUpdated, setLastUpdated] = useState(null);

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const ROWS_PER_PAGE = 100;

    const [showSchemesModal, setShowSchemesModal] = useState(false);

    // New Scheme Groups State
    const [schemeGroups, setSchemeGroups] = useState([]);

    // Generic Group State
    const [newGroupName, setNewGroupName] = useState('');
    const [newGroupType, setNewGroupType] = useState('Retail'); // Acts as Sector for Generic
    const [newGroupFile, setNewGroupFile] = useState(null);

    // Specific State for Jewel Loan Quick Upload
    const [jlGroupName, setJlGroupName] = useState('');
    const [jlSector, setJlSector] = useState('Agri'); // Default Sector for JL
    const [jlGroupFile, setJlGroupFile] = useState(null);

    // Editing State
    const [editingGroupId, setEditingGroupId] = useState(null);
    const [editGroupData, setEditGroupData] = useState(null); // Local copy for editing
    const [newSchemeCode, setNewSchemeCode] = useState('');

    // Branch Filter State
    const [selectedBranch, setSelectedBranch] = useState('All');

    // FY Filter State
    const [selectedFY, setSelectedFY] = useState('All');
    const [recentPeriod, setRecentPeriod] = useState('month'); // 'week' | 'month'

    // Load data from context on mount
    useEffect(() => {
        const savedData = branchPerformance['sanctions'];
        if (savedData) {
            setSanctionsData(savedData.data || []);
            setLastUpdated(savedData.updatedAt ? new Date(savedData.updatedAt) : null);
        }

        // Load Schemes Groups
        const savedSchemes = branchPerformance['schemes'];
        if (savedSchemes && savedSchemes.groups) {
            setSchemeGroups(savedSchemes.groups);
        } else if (savedSchemes && savedSchemes.data) {
            // Migration: If old data exists, wrap it in a "Legacy" group
            setSchemeGroups([{ id: 'legacy', name: 'Legacy Imports', category: 'Others', sector: 'Others', data: savedSchemes.data }]);
        }
    }, [branchPerformance]);

    const handleSchemesClick = () => {
        setShowSchemesModal(true);
    };

    const handleFileChange = (e, type = 'generic') => {
        if (e.target.files && e.target.files[0]) {
            if (type === 'jl') setJlGroupFile(e.target.files[0]);
            else setNewGroupFile(e.target.files[0]);
        }
    };

    const processGroupFile = async (name, category, sector, file, onSuccess) => {
        if (!name || !file) {
            alert("Please provide a Group Name and Select a File.");
            return;
        }

        const reader = new FileReader();
        reader.onload = async (evt) => {
            try {
                const arrayBuffer = evt.target.result;
                const workbook = XLSX.read(arrayBuffer, { type: 'array' });
                const wsname = workbook.SheetNames[0];
                const ws = workbook.Sheets[wsname];
                const data = XLSX.utils.sheet_to_json(ws);

                if (data.length === 0) {
                    alert("File appears empty.");
                    return;
                }

                const newGroup = {
                    id: Date.now().toString(),
                    name: name,
                    category: category,
                    sector: sector,
                    data: data,
                    fileName: file.name,
                    type: category === 'Jewel Loan' ? 'Jewel Loan' : sector // Compat fallback
                };

                // Use functional update to avoid stale closures if multiple uploads happen rapidly
                setSchemeGroups(prev => {
                    const updated = [...prev, newGroup];
                    updateBranchPerformance('schemes', { groups: updated });
                    return updated;
                });

                alert(`Added group "${name}" with ${data.length} schemes.`);
                if (onSuccess) onSuccess();

            } catch (err) {
                console.error("Error parsing file:", err);
                alert("Failed to parse file.");
            }
        };
        reader.readAsArrayBuffer(file);
    };

    const handleAddGroup = () => {
        // Generic Uploads are always "Non-Jewel Loan" (or general) category
        // The "Type" dropdown acts as the Sector
        processGroupFile(newGroupName, 'Non-Jewel Loan', newGroupType, newGroupFile, () => {
            setNewGroupName('');
            setNewGroupFile(null);
            setNewGroupType('Retail');
            if (document.getElementById('group-file-input')) document.getElementById('group-file-input').value = null;
        });
    };

    const handleAddJewelGroup = () => {
        // Jewel Loan Uploads are "Jewel Loan" category
        // Sector comes from new state
        processGroupFile(jlGroupName, 'Jewel Loan', jlSector, jlGroupFile, () => {
            setJlGroupName('');
            setJlGroupFile(null);
            setJlSector('Agri');
            if (document.getElementById('jl-file-input')) document.getElementById('jl-file-input').value = null;
        });
    };

    const handleDeleteGroup = async (id) => {
        if (window.confirm("Are you sure you want to remove this scheme group?")) {
            const updatedGroups = schemeGroups.filter(g => g.id !== id);
            setSchemeGroups(updatedGroups);
            await updateBranchPerformance('schemes', { groups: updatedGroups });
        }
    };

    // --- Editor Handlers ---
    const handleEditClick = (group) => {
        setEditingGroupId(group.id);
        setEditGroupData({ ...group, data: [...group.data] }); // Deep copy data array
        setNewSchemeCode('');
    };

    const handleBackFromEdit = () => {
        setEditingGroupId(null);
        setEditGroupData(null);
    };

    const handleRemoveSchemeFromEdit = (index) => {
        setEditGroupData(prev => {
            const newData = [...prev.data];
            newData.splice(index, 1);
            return { ...prev, data: newData };
        });
    };

    const handleAddSchemeToEdit = () => {
        if (!newSchemeCode.trim()) return;
        setEditGroupData(prev => {
            // Standardize format: Scheme Code key
            const newRow = { 'Scheme Code': newSchemeCode.trim() };
            return { ...prev, data: [newRow, ...prev.data] };
        });
        setNewSchemeCode('');
    };

    const handleSaveEdit = async () => {
        const updatedGroups = schemeGroups.map(g => {
            if (g.id === editingGroupId) {
                return editGroupData;
            }
            return g;
        });
        setSchemeGroups(updatedGroups);
        await updateBranchPerformance('schemes', { groups: updatedGroups });
        setEditingGroupId(null);
        setEditGroupData(null);
    };
    // -----------------------

    const handleUpdateSanctions = async () => {
        setLoading(true);
        try {
            const allData = [];

            for (const filename of fileList) {
                try {
                    const response = await fetch(`/data/advances/${filename}`);
                    if (!response.ok) throw new Error(`Failed to fetch ${filename}`);

                    const arrayBuffer = await response.arrayBuffer();
                    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    const jsonData = XLSX.utils.sheet_to_json(worksheet);

                    // Add filename to each record for lineage and Normalize Data
                    const dataWithSource = jsonData.map(row => {
                        const newRow = { ...row, _sourceFile: filename };

                        // Normalize Priority Type
                        const pKey = Object.keys(row).find(k => k.trim().toLowerCase() === 'priority type');
                        if (pKey) {
                            const val = String(row[pKey] || '').trim().toLowerCase();
                            if (['sme', 'sme_np'].includes(val)) {
                                newRow[pKey] = 'SME';
                            }
                        }

                        // Format OPEN_DT (YYYYMMDD -> DD-MM-YYYY) and Calculate FY
                        const dateKey = Object.keys(row).find(k => k.trim().toUpperCase() === 'OPEN_DT');
                        if (dateKey) {
                            const dateVal = String(row[dateKey] || '').trim();
                            // regex check for YYYYMMDD (8 digits)
                            if (/^\d{8}$/.test(dateVal)) {
                                const yyyy = parseInt(dateVal.substring(0, 4));
                                const mm = parseInt(dateVal.substring(4, 6));
                                const dd = dateVal.substring(6, 8);

                                newRow[dateKey] = `${dd}-${String(mm).padStart(2, '0')}-${yyyy}`;

                                // Calculate Financial Year
                                // If Month >= 4 (April), FY is Current-Next (e.g., 2023-04 -> FY 2023-2024)
                                // Else, FY is Prev-Current (e.g., 2023-03 -> FY 2022-2023)
                                const fyStart = mm >= 4 ? yyyy : yyyy - 1;
                                newRow['_fy'] = `FY ${fyStart}-${fyStart + 1}`;
                            }
                        }

                        return newRow;
                    });
                    allData.push(...dataWithSource);
                } catch (err) {
                    console.error(`Error processing ${filename}:`, err);
                }
            }

            // Persist to Context/DB
            await updateBranchPerformance('sanctions', { data: allData });

            setSanctionsData(allData);
            setLastUpdated(new Date());
            console.log('Processed Data:', allData);
        } catch (error) {
            console.error("Global update error:", error);
            alert("Failed to update sanctions data.");
        } finally {
            setLoading(false);
        }
    };

    // Use branches from Context
    // Sort logic handled in Context or here if needed
    const sortedBranches = React.useMemo(() => {
        return [...branches].sort((a, b) => a.name.localeCompare(b.name));
    }, [branches]);

    // Memoize Classified Data and Stats
    const statsResult = React.useMemo(() => {
        if (!sanctionsData.length) return { classifiedData: [], dashboardStats: null, schemeMapReference: new Map() };

        // 1. Helpers
        const getVal = (r, k) => {
            const key = Object.keys(r).find(rk => rk.trim().toLowerCase() === k.toLowerCase());
            return key ? r[key] : undefined;
        };

        // Filter Data based on Selected Branch
        let filteredData = sanctionsData;
        if (selectedBranch !== 'All') {
            filteredData = sanctionsData.filter(row => {
                const solId = String(getVal(row, 'SOL_ID') || getVal(row, 'Branch Code') || getVal(row, 'SOL ID') || '0000').trim();
                // Loose comparison to handle potential leading zeros mismatch if necessary, 
                // but direct string comparison is safest if data is consistent.
                return solId === selectedBranch;
            });
        }

        // 2. Build Scheme Map from GROUPS
        // Map: SchemeCode -> { category, sector, groupName, bucketKey }
        const schemeMap = new Map();
        let totalSchemes = 0;

        // Sort groups to process Jewel Loan LAST so they override any conflicts
        const sortedGroups = [...schemeGroups].sort((a, b) => {
            const isA = a.category === 'Jewel Loan' || a.type === 'Jewel Loan';
            const isB = b.category === 'Jewel Loan' || b.type === 'Jewel Loan';
            if (isA && !isB) return 1; // A is JL, put after B
            if (!isA && isB) return -1; // B is JL, put before A
            return 0;
        });

        sortedGroups.forEach(group => {
            // New structure: category (L1), sector (L2), name (L3)
            // Fallback for legacy data/generic uploads
            const l1 = group.category || (group.type === 'Jewel Loan' ? 'Jewel Loan' : 'Non-Jewel Loan');
            const l2 = group.sector || (group.type === 'Jewel Loan' ? 'Agri' : group.type);
            const l3 = group.name;

            // Map L2 Sector to Dashboard Bucket
            let bucketKey = 'others';
            if (l1 === 'Jewel Loan') bucketKey = 'jl';
            else if (['Retail'].includes(l2)) bucketKey = 'retail';
            else if (['Agri', 'Agriculture'].includes(l2)) bucketKey = 'agri';
            else if (['MSME', 'SME', 'Corporate'].includes(l2)) bucketKey = 'sme';

            if (group.data) {
                // Smart Column Detection
                let codeKey = null;
                const sampleRow = group.data[0] || {};
                const keys = Object.keys(sampleRow);

                const standardKeys = ['Scheme Code', 'SCHM_CODE', 'Code', 'Scheme', 'SCHEME_CODE'];
                codeKey = keys.find(k => standardKeys.some(sk => sk.toLowerCase() === k.toLowerCase().trim()));

                if (!codeKey) {
                    codeKey = keys.find(k => k.toLowerCase().includes('code') || k.toLowerCase().includes('schm'));
                }

                if (!codeKey && keys.length > 0) {
                    // Fallback to first column
                    codeKey = keys[0];
                }

                group.data.forEach(s => {
                    const rawCode = codeKey ? String(s[codeKey] || '').trim() : '';
                    if (rawCode) {
                        schemeMap.set(rawCode.toLowerCase(), { l1, l2, l3, bucketKey, sector: l2 });
                        totalSchemes++;
                    }
                });
            }
        });

        // Compute Dashboard Stats (L1 Buckets)
        const buckets = {
            jl: { emoji: '💎', title: 'Jewel Loan', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } },
            retail: { emoji: '🛍️', title: 'Core Retail', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } },
            sme: { emoji: '🏭', title: 'Core SME', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } },
            agri: { emoji: '🌾', title: 'Core Agri', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } },
            corporate: { emoji: '🏢', title: 'Corporate', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } },
            others: { emoji: '❓', title: 'Others', count: 0, balance: 0, smas: { '0': { c: 0, b: 0 }, '1': { c: 0, b: 0 }, '2': { c: 0, b: 0 }, 'npa': { c: 0, b: 0 }, regular: { c: 0, b: 0 } } }
        };

        const categoryLabels = {
            jl: { label: 'Jewel Loan', emoji: '💎' },
            retail: { label: 'Retail', emoji: '🛍️' },
            sme: { label: 'SME', emoji: '🏭' },
            agri: { label: 'Agri', emoji: '🌾' },
            corporate: { label: 'Corporate', emoji: '🏢' },
            others: { label: 'Others', emoji: '❓' }
        };

        // 4. Process Every Row (Using Filtered Data)
        const enriched = filteredData.map(row => {
            // Helper to find normalized keys
            const findKey = (search) => Object.keys(row).find(k => k.trim().toLowerCase() === search.toLowerCase());

            // Dynamic _fy Calculation & Date Parsing
            let fy = row._fy;
            let openDateObj = null;
            let dateParts = null; // { d, m }

            const dateKey = findKey('OPEN_DT');
            if (dateKey) {
                const val = String(row[dateKey] || '').trim();
                let yyyy, mm, dd;

                // Try YYYYMMDD
                if (/^\d{8}$/.test(val)) {
                    yyyy = parseInt(val.substring(0, 4));
                    mm = parseInt(val.substring(4, 6));
                    dd = parseInt(val.substring(6, 8));
                }
                // Try DD-MM-YYYY
                else if (/^\d{2}-\d{2}-\d{4}$/.test(val)) {
                    const parts = val.split('-');
                    dd = parseInt(parts[0]);
                    mm = parseInt(parts[1]);
                    yyyy = parseInt(parts[2]);
                }

                if (yyyy && mm) {
                    if (!fy) {
                        const fyStart = mm >= 4 ? yyyy : yyyy - 1;
                        fy = `FY ${fyStart}-${fyStart + 1}`;
                    }
                    if (dd) {
                        openDateObj = new Date(yyyy, mm - 1, dd);
                        dateParts = { d: dd, m: mm };
                    }
                }
            }

            // Extract REPORT_DT for Max Date calculation
            // Assuming REPORT_DT is uniform, but we extract per row
            let reportDateObj = null;
            const rptKey = findKey('REPORT_DT'); // or REPORT_DATE
            if (rptKey) {
                const val = String(row[rptKey] || '').trim();
                // Assuming YYYYMMDD usually
                if (/^\d{8}$/.test(val)) {
                    const y = parseInt(val.substring(0, 4));
                    const m = parseInt(val.substring(4, 6));
                    const d = parseInt(val.substring(6, 8));
                    reportDateObj = new Date(y, m - 1, d);
                } else if (/^\d{2}-\d{2}-\d{4}$/.test(val)) { // DD-MM-YYYY support for REPORT_DT too
                    const parts = val.split('-');
                    const d = parseInt(parts[0]);
                    const m = parseInt(parts[1]);
                    const y = parseInt(parts[2]);
                    reportDateObj = new Date(y, m - 1, d);
                }
            }

            const schemeCode = String(getVal(row, 'SCHM_CODE') || getVal(row, 'Scheme Code') || '').trim().toLowerCase();
            const segment = String(getVal(row, 'PRIORITY_TYPE') || getVal(row, 'Priority Type') || getVal(row, 'Segment') || '').trim().toLowerCase();

            // Step 1: Check Scheme Map
            let match = schemeMap.get(schemeCode); // { l1, l2, l3, bucketKey, sector }

            // Refinement: Validate Scheme Sector against Priority Type (Segment)
            // Ensures "Housing Loan" (Retail) only appears if Priority Type is also Retail.
            if (match) {
                const sSector = (match.sector || '').toLowerCase();
                const pType = segment;

                let isCompatible = false;
                if (sSector === 'retail' && pType.includes('retail')) isCompatible = true;
                else if ((sSector === 'sme' || sSector === 'msme') && (pType.includes('sme') || pType.includes('msme'))) isCompatible = true;
                else if ((sSector === 'agri' || sSector === 'agriculture') && (pType.includes('agri') || pType.includes('agriculture'))) isCompatible = true;
                else if (sSector === 'jewel loan' || (sSector === 'agri' && pType.includes('jewel'))) isCompatible = true; // JL often overlaps
                else if (pType === '') isCompatible = true; // Assume match if Segment undefined? Or strict? User implies strict "compare". Let's be lenient on empty to avoid data loss, or strict?
                // Given "Housing Loan will become a subset of Core Retail", likely want strict alignment.

                // If undefined sector in scheme, assume generic
                if (!sSector) isCompatible = true;

                if (!isCompatible) {
                    match = null; // Invalidate match if sectors don't align
                }
            }

            let l1 = match ? match.l1 : 'Others';
            let l2 = match ? match.l2 : 'Others';
            let l3 = match ? match.l3 : 'Others'; // If no match, default to Others instead of Unknown
            let bKey = match ? match.bucketKey : null;

            // Step 2: Refine L2 for Non-Jewel Loan based on PRIORITY_TYPE
            if (l1 !== 'Jewel Loan') {
                if (segment.includes('retail')) {
                    l2 = 'Core Retail';
                    bKey = 'retail';
                    if (l1 === 'Others' || l1 === 'Unclassified') l1 = 'Non-Jewel Loan';
                }
                else if (segment.includes('sme') || segment.includes('msme')) {
                    l2 = 'Core MSME';
                    bKey = 'sme';
                    if (l1 === 'Others' || l1 === 'Unclassified') l1 = 'Non-Jewel Loan';
                }
                else if (segment.includes('agri')) {
                    l2 = 'Core Agri';
                    bKey = 'agri';
                    if (l1 === 'Others' || l1 === 'Unclassified') l1 = 'Non-Jewel Loan';
                }
                else if (segment.includes('corporate') || segment.includes('corp')) {
                    l2 = 'Corporate';
                    bKey = 'corporate';
                    if (l1 === 'Others' || l1 === 'Unclassified') l1 = 'Non-Jewel Loan';
                }
            }

            if (!bKey) bKey = 'others';

            // Stats Aggregation
            if (buckets[bKey]) {
                // User Request: Pick up balance from NET_BALANCE, show in Crores, remove negative sign
                let rawBal = parseFloat(getVal(row, 'NET_BALANCE') || getVal(row, 'Balance') || getVal(row, 'Clear Balance') || 0);
                const balance = Math.abs(rawBal) / 10000000; // Divide by 1 Crore

                // Sanctioned Amount (DOC_AMOUNT)
                let rawSanction = parseFloat(getVal(row, 'DOC_AMOUNT') || getVal(row, 'Sanction Limit') || 0);
                const sanctionAmt = Math.abs(rawSanction) / 10000000; // Crores

                // Asset Code (Unused for now)
                // const assetCode = String(getVal(row, 'Asset Code') || getVal(row, 'Asset Class') || '').trim().toUpperCase();
                const glSubCd = String(getVal(row, 'GL_SUB_CD') || '').trim();
                const smaTypeRaw = String(getVal(row, 'SMA_TYPE') || '').trim().toUpperCase();

                buckets[bKey].count++;
                buckets[bKey].balance += balance;

                // Retail Sub-Classification (for Sanctions Summary)
                let retailSub = null;
                if (bKey === 'retail') {
                    // Normalize Scheme Desc/Code for matching
                    const desc = String(getVal(row, 'SCHM_DESC') || getVal(row, 'Scheme Description') || '').toLowerCase();
                    const code = schemeCode.toLowerCase();

                    if (desc.includes('housing') || desc.includes('home') || code.includes('hl')) retailSub = 'Housing';
                    else if (desc.includes('vehicle') || desc.includes('car') || desc.includes('two wheeler') || code.includes('vehicle')) retailSub = 'Vehicle';
                    else if (desc.includes('education') || desc.includes('vidya') || code.includes('el')) retailSub = 'Education';
                    else if (desc.includes('mortgage') || desc.includes('lap') || desc.includes('property')) retailSub = 'Mortgage';
                    else if (desc.includes('personal') || desc.includes('salary') || desc.includes('pension') || code.includes('pl')) retailSub = 'Personal Loan';
                    else if (desc.includes('liquirent') || desc.includes('rent')) retailSub = 'Liquirent';
                    else retailSub = 'Other Retail';
                }

                // Add to Aggregated Sanctions Stats (Attached to row for lighter pass later? No, better aggregate here if possible or create a new parallel structure)
                // Let's attach metadata to the row for easy filtering/aggregation in the Memo
                row._sanctionAmt = sanctionAmt; // Store normalized for stats
                row._retailSub = retailSub;

                // Risk Classification
                // NPA based on GL_SUB_CD
                const isNPA = ['33750', '33850', '33950', '33999'].includes(glSubCd);

                // SMA based on SMA_TYPE (0, 1, 2)
                let smaKey = null;
                if (smaTypeRaw.includes('0') || smaTypeRaw === 'SMA0') smaKey = '0';
                else if (smaTypeRaw.includes('1') || smaTypeRaw === 'SMA1') smaKey = '1';
                else if (smaTypeRaw.includes('2') || smaTypeRaw === 'SMA2') smaKey = '2';

                if (isNPA) {
                    buckets[bKey].smas.npa.c++;
                    buckets[bKey].smas.npa.b += balance;
                } else if (smaKey) {
                    buckets[bKey].smas[smaKey].c++;
                    buckets[bKey].smas[smaKey].b += balance;
                } else {
                    // Regular Account (Not NPA, Not SMA)
                    buckets[bKey].smas.regular = buckets[bKey].smas.regular || { c: 0, b: 0 };
                    buckets[bKey].smas.regular.c++;
                    buckets[bKey].smas.regular.b += balance;
                }
            }

            // Emojis for 3-Level Categorization
            const l1Emoji = l1 === 'Jewel Loan' ? '💎' : '📄';
            const l2Emoji = ['Agri', 'Agriculture'].includes(l2) ? '🌾' :
                ['Retail'].includes(l2) ? '🛍️' :
                    ['SME', 'MSME'].includes(l2) ? '🏭' :
                        ['Corporate'].includes(l2) ? '🏢' : '❓';

            return {
                ...row,
                _fy: fy, // Add computed FY
                _l1_category: `${l1Emoji} ${l1}`,
                _l2_sector: `${l2Emoji} ${l2}`,
                _l3_sub_category: `📁 ${l3}`,
                _l3: l3, // Raw L3 for stats
                _bucket_key: bKey,
                _category: categoryLabels[bKey],
                _openDateObj: openDateObj,
                _reportDateObj: reportDateObj // Return for max date calc
            };
        });

        // 5. Calculate Grand Totals for Percentages
        let grandTotalCount = 0;
        let grandTotalBalance = 0;
        Object.values(buckets).forEach(b => {
            grandTotalCount += b.count;
            grandTotalBalance += b.balance;
        });

        return { classifiedData: enriched, dashboardStats: buckets, grandTotalCount, grandTotalBalance, schemeMapReference: schemeMap, totalSchemes };
    }, [sanctionsData, schemeGroups, selectedBranch]);

    // Extract Unique FYs for Dropdown
    const fyOptions = React.useMemo(() => {
        const fys = new Set();
        (statsResult?.classifiedData || []).forEach(row => {
            if (row._fy) fys.add(row._fy);
        });
        const sorted = Array.from(fys).sort(); // Ascending (Oldest -> Newest)
        if (sorted.length > 1) {
            sorted.shift(); // Remove oldest
        }
        return sorted.reverse(); // Newest First
    }, [statsResult]);

    // Filter Data by FY for Sanctions Tab
    const sanctionsTabData = React.useMemo(() => {
        if (!statsResult?.classifiedData) return [];
        if (selectedFY === 'All') return statsResult.classifiedData;
        return statsResult.classifiedData.filter(row => row._fy === selectedFY);
    }, [statsResult, selectedFY]);

    // Helper for aggregation
    const aggregateSanctionRows = (rows) => {
        const stats = {
            retail: { count: 0, amount: 0, subs: {} },
            sme: { count: 0, amount: 0 }, // Core SME
            agri: { count: 0, amount: 0 }, // Core Agri
            jl: { count: 0, amount: 0 },
            corporate: { count: 0, amount: 0 }
        };

        const ignoredRetail = ['Others', 'Unknown Scheme', 'Unclassified', 'unknown', 'others', 'jl', 'jewel loan'];

        rows.forEach(row => {
            // 1. Exclude DLDEP
            const schemeCode = String(row['SCHM_CODE'] || row['Scheme Code'] || '').trim().toUpperCase();
            if (schemeCode === 'DLDEP') return;

            const amt = row._sanctionAmt || 0;
            let cat = row._bucket_key; // retail, sme, agri, jl, corporate...

            // 2. Ensure Jewel Loan is strictly 'jl' bucket
            if (cat === 'jl' || String(row._l1).toLowerCase().includes('jewel')) {
                cat = 'jl';
            }

            if (stats[cat]) {
                // For Retail: STRICTLY Sum of Valid L3 Subs
                if (cat === 'retail') {
                    const l3Name = row._l3 || 'Others';

                    // Filter out Others/Unknown AND ensures no JL leaks in
                    if (!ignoredRetail.includes(l3Name) && !ignoredRetail.includes(l3Name.toLowerCase()) && !l3Name.toLowerCase().includes('jewel')) {
                        // Increment Core Retail ONLY if it's a valid sub-category
                        stats.retail.count++;
                        stats.retail.amount += amt;

                        stats.retail.subs[l3Name] = stats.retail.subs[l3Name] || { c: 0, a: 0 };
                        stats.retail.subs[l3Name].c++;
                        stats.retail.subs[l3Name].a += amt;
                    }
                } else {
                    // For others (SME, Agri, JL, Corp), just sum up
                    stats[cat].count++;
                    stats[cat].amount += amt;
                }
            }
        });
        return stats;
    };

    // Sanctions Summary Stats (Current FY vs Previous FY)
    const sanctionsSummaryStats = React.useMemo(() => {
        if (!statsResult?.classifiedData || !fyOptions.length) return { current: null, previous: null, currentFYLabel: '', prevFYLabel: '', maxReportDateObj: null };

        const currentFYLabel = selectedFY === 'All' ? fyOptions[0] : selectedFY;
        const currentIndex = fyOptions.indexOf(currentFYLabel);
        const prevFYLabel = currentIndex !== -1 && currentIndex + 1 < fyOptions.length ? fyOptions[currentIndex + 1] : null;

        const isLatestFY = currentFYLabel === fyOptions[0];

        // Calculate Max Report Date
        let maxReportDate = null;
        statsResult.classifiedData.forEach(row => {
            if (row._reportDateObj) {
                if (!maxReportDate || row._reportDateObj > maxReportDate) {
                    maxReportDate = row._reportDateObj;
                }
            }
        });

        // Current FY Data
        const currentData = statsResult.classifiedData.filter(r => r._fy === currentFYLabel);
        const currentStats = aggregateSanctionRows(currentData);

        // Previous FY Data (Filtered)
        let previousStats = null;
        let prevAsOnDate = null;

        if (prevFYLabel) {
            const prevRowsRaw = statsResult.classifiedData.filter(r => r._fy === prevFYLabel);
            let prevRowsFiltered = prevRowsRaw;

            if (isLatestFY && maxReportDate) {
                // Filter YTD
                const rMonth = maxReportDate.getMonth();
                const rDay = maxReportDate.getDate();

                prevRowsFiltered = prevRowsRaw.filter(row => {
                    if (!row._openDateObj) return false;
                    const oMonth = row._openDateObj.getMonth();
                    const oDay = row._openDateObj.getDate();
                    // Keep if before or equal to report date month/day
                    return oMonth < rMonth || (oMonth === rMonth && oDay <= rDay);
                });

                // Set Prev As On Date
                const d = new Date(maxReportDate);
                d.setFullYear(d.getFullYear() - 1);
                prevAsOnDate = d.toLocaleDateString('en-GB');

            } else {
                // Historical Full Year
                const parts = prevFYLabel.split('-');
                if (parts.length === 2) {
                    prevAsOnDate = `31/03/${parts[1]}`;
                }
            }
            previousStats = aggregateSanctionRows(prevRowsFiltered);
        }

        return {
            current: currentStats,
            previous: previousStats,
            currentFYLabel,
            prevFYLabel,
            reportDateFormatted: maxReportDate ? maxReportDate.toLocaleDateString('en-GB') : '',
            maxReportDateObj: maxReportDate,
            prevAsOnDate
        };
    }, [statsResult, selectedFY, fyOptions]);

    // Recent Performance Stats
    const recentStats = React.useMemo(() => {
        if (!sanctionsSummaryStats.maxReportDateObj || !statsResult?.classifiedData) return null;

        const anchorDate = sanctionsSummaryStats.maxReportDateObj;
        const filteredRows = statsResult.classifiedData.filter(row => {
            if (!row._openDateObj) return false;

            if (recentPeriod === 'week') {
                // Previous Week (Mon-Sun) relative to Anchor
                // Getting the "Previous Week" usually means: Find start of current week, subtract 7 days.
                // Assuming "Current Week" starts on Monday.
                const dayOfWeek = anchorDate.getDay(); // 0 (Sun) to 6 (Sat)
                // Adjust to Make Monday = 0, Sunday = 6
                const dayIndex = (dayOfWeek + 6) % 7;

                const currentWeekMonday = new Date(anchorDate);
                currentWeekMonday.setDate(anchorDate.getDate() - dayIndex);
                currentWeekMonday.setHours(0, 0, 0, 0);

                const prevWeekMonday = new Date(currentWeekMonday);
                prevWeekMonday.setDate(currentWeekMonday.getDate() - 7);

                const prevWeekSunday = new Date(currentWeekMonday);
                prevWeekSunday.setDate(currentWeekMonday.getDate() - 1);
                prevWeekSunday.setHours(23, 59, 59, 999);

                return row._openDateObj >= prevWeekMonday && row._openDateObj <= prevWeekSunday;

            } else {
                // Current Month (Up to Date)
                // 1st of Anchor Month to Anchor Date
                const monthStart = new Date(anchorDate.getFullYear(), anchorDate.getMonth(), 1);
                return row._openDateObj >= monthStart && row._openDateObj <= anchorDate;
            }
        });

        return aggregateSanctionRows(filteredRows);

    }, [sanctionsSummaryStats.maxReportDateObj, statsResult, recentPeriod]);

    // Deconstruct with default
    const { classifiedData, dashboardStats, grandTotalCount, grandTotalBalance, schemeMapReference = new Map() } = statsResult || {};

    // --- Components ---

    const SanctionsCard = ({ title, data, isPrimary, retailKeys = [], topAction = null, customStyle = {}, highlightZero = false }) => {
        if (!data) return <div className="card empty">No Data for Comparison</div>;

        const Row = ({ label, count, amount, isBold = false, indent = false }) => {
            const isZero = count === 0;
            const applyHighlight = highlightZero && isZero;
            const textColor = applyHighlight ? '#fbbf24' : (customStyle.color || (isBold ? '#0f172a' : '#64748b')); // Amber-400 equivalent for visibility
            const valueColor = applyHighlight ? '#fbbf24' : (customStyle.color || '#0f172a');
            const pipeColor = applyHighlight ? 'rgba(251, 191, 36, 0.7)' : (customStyle.color ? 'rgba(255,255,255,0.7)' : '#94a3b8');

            // Removed text shadow as per request

            return (
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', paddingLeft: indent ? '1rem' : '0', fontWeight: isBold ? 600 : 400, borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
                    <span style={{ color: textColor }}>{label}</span>
                    <span style={{ color: valueColor }}>
                        {count} <span style={{ color: pipeColor, fontSize: '0.8em' }}>|</span> ₹{amount.toFixed(2)} Cr
                    </span>
                </div>
            );
        };

        return (
            <div className={`card ${isPrimary ? 'primary-shadow' : ''}`} style={{ flex: 1, minWidth: '300px', padding: '1.5rem', background: 'white', borderRadius: '0.75rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', ...customStyle }}>
                {/* Top Action Area (Toggle) - Reserved height for alignment */}
                <div style={{ minHeight: '32px', marginBottom: '0.5rem', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    {topAction}
                </div>

                <h3 style={{
                    margin: 0,
                    marginBottom: '1rem',
                    color: customStyle.titleColor || (isPrimary ? '#2563eb' : '#475569'),
                    borderBottom: `2px solid ${customStyle.borderColor || '#e2e8f0'}`,
                    paddingBottom: '0.5rem',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    fontSize: '1.1rem',
                    display: 'block'
                }} title={title}>
                    {title}
                </h3>

                {/* Core Retail */}
                <Row label="Core Retail" count={data.retail.count} amount={data.retail.amount} isBold />
                {retailKeys.map(sub => {
                    const val = data.retail.subs[sub] || { c: 0, a: 0 };
                    // Render even if 0 to align with other card
                    return <Row key={sub} label={sub} count={val.c} amount={val.a} indent />;
                })}

                <div style={{ height: '0.5rem' }}></div>
                <Row label="Core SME" count={data.sme.count} amount={data.sme.amount} isBold />
                <Row label="Core Agri" count={data.agri.count} amount={data.agri.amount} isBold />
                {/* Jewel Loan Removed as per request */}
                <Row label="Corporate" count={data.corporate.count} amount={data.corporate.amount} isBold />
            </div>
        );
    };

    const MiniPieChart = ({ data }) => {
        // Data format: { npa: val, '2': val, '1': val, '0': val, regular: val }
        // Colors
        const colors = {
            npa: '#dc2626', // Red
            '2': '#ea580c', // Orange Red
            '1': '#f97316', // Orange
            '0': '#eab308', // Yellow
            regular: '#22c55e' // Green
        };

        const total = Object.values(data).reduce((acc, v) => acc + v, 0);
        if (total === 0) return null;

        let currentAngle = 0;
        const gradientParts = [];
        const tooltipParts = [];

        // Order: Regular, SMA0, SMA1, SMA2, NPA
        ['regular', '0', '1', '2', 'npa'].forEach(key => {
            const val = data[key] || 0;
            if (val > 0) {
                const percentage = (val / total) * 100;
                const angle = (val / total) * 360;
                gradientParts.push(`${colors[key]} 0 ${currentAngle + angle}deg`);
                currentAngle += angle;

                // Tooltip text
                const label = key === 'regular' ? 'Regular' : key === 'npa' ? 'NPA' : `SMA ${key}`;
                tooltipParts.push(`${label}: ${val.toFixed(2)} (${percentage.toFixed(1)}%)`);
            }
        });

        const conicGradient = `conic-gradient(${gradientParts.map((p, i) => {
            // Adjust syntax for valid CSS conic-gradient
            // red 0deg 60deg, blue 60deg 120deg...
            const prevAngle = i === 0 ? 0 : parseFloat(gradientParts[i - 1].split(' ').pop());
            const currentAngleStr = p.split(' ').pop();
            const color = p.split(' ')[0];
            return `${color} ${prevAngle}deg ${currentAngleStr}`;
        }).join(', ')})`;

        return (
            <div className="mini-pie-chart" title={tooltipParts.join('\n')} style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: conicGradient,
                position: 'relative',
                cursor: 'pointer'
            }}>
                <div style={{
                    position: 'absolute',
                    top: '50%', left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '30px', height: '30px',
                    borderRadius: '50%',
                    background: 'white' // Donut hole
                }}></div>
            </div>
        );
    };

    const TabButton = ({ id, label }) => (
        <button
            onClick={() => setActiveTab(id)}
            className={`tab-btn ${activeTab === id ? 'active' : ''}`}
        >
            {label}
        </button>
    );

    return (
        <div className="performance-container">
            <div className="card">
                <div className="card-header">
                    <h1 className="title">Branch Performance Analytics</h1>
                    <div className="header-actions" style={{ flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                            {/* Branch Filter Dropdown */}
                            <select
                                className="branch-select"
                                value={selectedBranch}
                                onChange={(e) => setSelectedBranch(e.target.value)}
                                style={{ padding: '0.5rem', borderRadius: '0.375rem', borderColor: '#d1d5db' }}
                            >
                                <option value="All">Region (All Branches)</option>
                                {sortedBranches.map(b => (
                                    <option key={b.code} value={b.code}>{b.name} ({b.code})</option>
                                ))}
                            </select>

                            <button
                                onClick={handleSchemesClick}
                                className="btn-update btn-schemes"
                            >
                                Schemes
                            </button>
                            <button
                                onClick={handleUpdateSanctions}
                                disabled={loading}
                                className={`btn-update ${loading ? 'loading' : ''}`}
                            >
                                {loading ? 'Updating...' : '↻ Update Data'}
                            </button>
                        </div>
                        {lastUpdated && (
                            <span className="last-updated">
                                Last updated: {lastUpdated.toLocaleString()}
                            </span>
                        )}
                    </div>
                </div>

                {/* Tabs Header */}
                <div className="tabs">
                    <TabButton id="sanctions" label="Loans Summary" />
                    <TabButton id="sanctions_tab" label="Sanctions" />
                    <TabButton id="list_all" label="List of all accounts" />
                    <TabButton id="collections" label="Collections" />
                    <TabButton id="recoveries" label="Recoveries" />
                </div>

                <div className="tab-content">
                    {activeTab === 'sanctions_tab' && (
                        <div className="content-pane">
                            {/* FY Filter Toolbar */}
                            <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '1rem', background: '#f8fafc', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                                <label style={{ fontWeight: 600, color: '#475569' }}>Filter by Financial Year:</label>
                                <select
                                    value={selectedFY}
                                    onChange={(e) => setSelectedFY(e.target.value)}
                                    style={{ padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #cbd5e1', minWidth: '150px' }}
                                >
                                    <option value="All">All Years</option>
                                    {fyOptions.map(fy => (
                                        <option key={fy} value={fy}>{fy}</option>
                                    ))}
                                </select>
                                <div style={{ flex: 1, textAlign: 'right', fontSize: '0.875rem', color: '#64748b' }}>
                                    Showing {sanctionsTabData.length} records
                                </div>
                            </div>

                            {/* Sanctions Summary Cards */}
                            {(() => {
                                const currentKeys = sanctionsSummaryStats?.current?.retail?.subs ? Object.keys(sanctionsSummaryStats.current.retail.subs) : [];
                                const prevKeys = sanctionsSummaryStats?.previous?.retail?.subs ? Object.keys(sanctionsSummaryStats.previous.retail.subs) : [];
                                const recentKeys = recentStats?.retail?.subs ? Object.keys(recentStats.retail.subs) : [];
                                const unifiedRetailKeys = Array.from(new Set([...currentKeys, ...prevKeys, ...recentKeys])).sort();

                                return (
                                    <div className="comparison-section" style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                                        <SanctionsCard
                                            title={sanctionsSummaryStats.currentFYLabel ? `Curr FY (${sanctionsSummaryStats.currentFYLabel.replace('FY ', '')})` : 'Curr FY'}
                                            data={sanctionsSummaryStats.current}
                                            isPrimary={true}
                                            retailKeys={unifiedRetailKeys}
                                        />
                                        <SanctionsCard
                                            title={sanctionsSummaryStats.prevFYLabel ? `Prev FY (${sanctionsSummaryStats.prevFYLabel.replace('FY ', '')})${sanctionsSummaryStats.prevAsOnDate ? ` - ${sanctionsSummaryStats.prevAsOnDate}` : ''}` : 'Prev FY'}
                                            data={sanctionsSummaryStats.previous}
                                            isPrimary={false}
                                            retailKeys={unifiedRetailKeys}
                                        />
                                        <SanctionsCard
                                            title={recentPeriod === 'week' ? 'Prev Week (Mon-Sun)' : 'Curr Month (YTD)'}
                                            data={recentStats}
                                            isPrimary={false}
                                            retailKeys={unifiedRetailKeys}
                                            highlightZero={true}
                                            customStyle={{
                                                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                                                color: 'white',
                                                titleColor: 'white',
                                                borderColor: 'rgba(255,255,255,0.2)',
                                                borderRadius: '0.75rem',
                                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                                            }}
                                            topAction={
                                                <div style={{ display: 'flex', background: 'rgba(255,255,255,0.2)', padding: '2px', borderRadius: '4px' }}>
                                                    <button
                                                        onClick={() => setRecentPeriod('week')}
                                                        style={{ padding: '0.25rem 0.5rem', border: 'none', background: recentPeriod === 'week' ? 'white' : 'transparent', color: recentPeriod === 'week' ? '#4f46e5' : 'white', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, transition: 'all 0.2s' }}>
                                                        Prev Week
                                                    </button>
                                                    <button
                                                        onClick={() => setRecentPeriod('month')}
                                                        style={{ padding: '0.25rem 0.5rem', border: 'none', background: recentPeriod === 'month' ? 'white' : 'transparent', color: recentPeriod === 'month' ? '#4f46e5' : 'white', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, transition: 'all 0.2s' }}>
                                                        Curr Month
                                                    </button>
                                                </div>
                                            }
                                        />
                                    </div>
                                );
                            })()}

                            {/* List Table Removed as per request */}
                        </div>
                    )}

                    {activeTab === 'sanctions' && (
                        <div className="sanctions-view">
                            {/* Dashboard Cards */}
                            {dashboardStats && (
                                <div className="dashboard-grid">
                                    {['jl', 'retail', 'sme', 'agri', 'corporate', 'others']
                                        .map(key => dashboardStats[key])
                                        .filter(b => b && b.count > 0) // Show all with data, including Others
                                        .map((bucket, idx) => {
                                            // Calculate % of Grand Total
                                            const countPct = grandTotalCount ? ((bucket.count / grandTotalCount) * 100).toFixed(1) : '0.0';
                                            const balPct = grandTotalBalance ? ((bucket.balance / grandTotalBalance) * 100).toFixed(1) : '0.0';

                                            return (
                                                <div key={idx} className="dash-card">
                                                    <div className="dash-card-header" style={{ flexDirection: 'column' }}>
                                                        {/* Top Row: Emoji + Title + Pie Chart */}
                                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '0.5rem' }}>
                                                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                                                <div className="dash-icon">{bucket.emoji}</div>
                                                                <div className="dash-title" style={{ fontSize: '1rem' }}>{bucket.title}</div>
                                                            </div>
                                                            <div style={{ margin: '0' }}>
                                                                <MiniPieChart data={{
                                                                    npa: bucket.smas.npa?.b || 0,
                                                                    '2': bucket.smas['2']?.b || 0,
                                                                    '1': bucket.smas['1']?.b || 0,
                                                                    '0': bucket.smas['0']?.b || 0,
                                                                    regular: bucket.smas.regular?.b || 0
                                                                }} />
                                                            </div>
                                                        </div>

                                                        {/* Bottom Row: Stats Stats below Emoji/Title */}
                                                        <div className="dash-stats" style={{ width: '100%', display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #f3f4f6', paddingTop: '0.5rem', marginBottom: '0.5rem' }}>
                                                            <div>
                                                                <span className="lbl">Count: </span>
                                                                <span className="val">{bucket.count}</span>
                                                                <span className="pct" style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '2px' }}>({countPct}%)</span>
                                                            </div>
                                                            <div>
                                                                <span className="lbl">Bal: </span>
                                                                <span className="val">₹{bucket.balance.toFixed(2)} Cr</span>
                                                                <span className="pct" style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '2px' }}>({balPct}%)</span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Risk Summary Table */}
                                                    {(bucket.smas['0'].c > 0 || bucket.smas['1'].c > 0 || bucket.smas['2'].c > 0 || bucket.smas['npa'].c > 0) && (
                                                        <div className="risk-summary">
                                                            <div className="risk-row header" style={{ gridTemplateColumns: '1fr 0.8fr 0.8fr 1.2fr 0.8fr' }}>
                                                                <span>Type</span>
                                                                <span style={{ textAlign: 'right' }}>Cnt</span>
                                                                <span style={{ textAlign: 'right' }}>%</span>
                                                                <span style={{ textAlign: 'right' }}>Bal</span>
                                                                <span style={{ textAlign: 'right' }}>%</span>
                                                            </div>
                                                            {['0', '1', '2', 'npa'].map(type => {
                                                                const s = bucket.smas[type];
                                                                if (s.c === 0) return null;

                                                                // % of Bucket Total
                                                                const cPct = bucket.count ? ((s.c / bucket.count) * 100).toFixed(1) : '0.0';
                                                                const bPct = bucket.balance ? ((s.b / bucket.balance) * 100).toFixed(1) : '0.0';

                                                                return (
                                                                    <div key={type} className={`risk-row ${type === 'npa' ? 'row-npa' : ''}`} style={{ gridTemplateColumns: '1fr 0.8fr 0.8fr 1.2fr 0.8fr' }}>
                                                                        <span>{type === 'npa' ? 'NPA' : `SMA ${type}`}</span>
                                                                        <span style={{ textAlign: 'right' }}>{s.c}</span>
                                                                        <span style={{ textAlign: 'right', fontSize: '0.7rem', opacity: 0.8 }}>{cPct}%</span>
                                                                        <span style={{ textAlign: 'right' }}>{s.b.toFixed(2)}</span>
                                                                        <span style={{ textAlign: 'right', fontSize: '0.7rem', opacity: 0.8 }}>{bPct}%</span>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                </div>
                            )}

                            {!sanctionsData.length && (
                                <div className="empty-state">
                                    <p>No loans data available. Please upload a file.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'list_all' && (
                        <div className="content-pane">
                            {classifiedData.length > 0 ? (
                                <div>
                                    <div style={{ background: '#333', color: '#fff', padding: '1rem', marginBottom: '1rem', borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                                        <strong>DEBUG INFO:</strong>
                                        <br />
                                        Groups: {schemeGroups.length} | Total Schemes: {statsResult?.totalSchemes || 0} | Sanctions: {sanctionsData.length}
                                        <br />
                                        <strong>First Group Keys (Row 0):</strong> {schemeGroups.length > 0 && schemeGroups[0].data.length > 0 ? JSON.stringify(Object.keys(schemeGroups[0].data[0])) : 'No Groups/Data'}
                                        <br />
                                        <strong>First Group Name:</strong> {schemeGroups.length > 0 ? schemeGroups[0].name : 'N/A'}
                                        <br />
                                        <strong>JL Codes (First 10):</strong> {[...schemeMapReference.entries()].filter(e => e[1].bucketKey === 'jl').slice(0, 10).map(e => e[0]).join(', ')}
                                        <br />
                                        <strong>First 3 Sanctions Rows Match Status:</strong>
                                        {sanctionsData.slice(0, 3).map((row, i) => {
                                            const code = String(row['SCHM_CODE'] || row['Scheme Code'] || '').trim().toLowerCase();
                                            const match = schemeMapReference.has(code) ? schemeMapReference.get(code) : null;
                                            return <div key={i}>Row {i}: Code='{code}' &rarr; Match? {match ? `${match.l1}/${match.l2}` : 'NO'}</div>
                                        })}
                                    </div>

                                    <div className="table-controls" style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div className="page-info">
                                            Showing {((currentPage - 1) * ROWS_PER_PAGE) + 1} - {Math.min(currentPage * ROWS_PER_PAGE, classifiedData.length)} of {classifiedData.length}
                                        </div>
                                        <div className="pagination">
                                            <button
                                                onClick={() => setCurrentPage(1)}
                                                disabled={currentPage === 1}
                                                className="btn-sm"
                                            >
                                                « First
                                            </button>
                                            <button
                                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                                disabled={currentPage === 1}
                                                className="btn-sm"
                                            >
                                                ‹ Prev
                                            </button>
                                            <span style={{ margin: '0 1rem', fontWeight: 600 }}>Page {currentPage}</span>
                                            <button
                                                onClick={() => setCurrentPage(p => Math.min(Math.ceil(classifiedData.length / ROWS_PER_PAGE), p + 1))}
                                                disabled={currentPage >= Math.ceil(classifiedData.length / ROWS_PER_PAGE)}
                                                className="btn-sm"
                                            >
                                                Next ›
                                            </button>
                                            <button
                                                onClick={() => setCurrentPage(Math.ceil(classifiedData.length / ROWS_PER_PAGE))}
                                                disabled={currentPage >= Math.ceil(classifiedData.length / ROWS_PER_PAGE)}
                                                className="btn-sm"
                                            >
                                                Last »
                                            </button>
                                        </div>
                                    </div>

                                    <div className="table-wrapper" style={{ maxHeight: '600px', overflowY: 'auto' }}>
                                        <table className="data-table">
                                            <thead style={{ position: 'sticky', top: 0, background: 'white', zIndex: 10 }}>
                                                <tr>
                                                    <th>Type (L1)</th>
                                                    <th>Sector (L2)</th>
                                                    <th>Scheme Group (L3)</th>
                                                    {Object.keys(classifiedData[0]).filter(k => !k.startsWith('_')).map((header) => (
                                                        <th key={header}>{header}</th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {classifiedData
                                                    .slice((currentPage - 1) * ROWS_PER_PAGE, currentPage * ROWS_PER_PAGE)
                                                    .map((row, index) => (
                                                        <tr key={index} style={{ backgroundColor: row._l1_category === 'Jewel Loan' ? '#f0f9ff' : 'transparent' }}>
                                                            <td>
                                                                <span className={`badge ${row._l1_category === 'Jewel Loan' ? 'jewel-loan' : 'generic'}`}>
                                                                    {row._l1_category}
                                                                </span>
                                                            </td>
                                                            <td>{row._l2_sector}</td>
                                                            <td><small>{row._l3_sub_category}</small></td>
                                                            {Object.keys(row).filter(k => !k.startsWith('_')).map((key, i) => (
                                                                <td key={i}>{row[key]}</td>
                                                            ))}
                                                        </tr>
                                                    ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <p>No data loaded.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'collections' && (
                        <div className="placeholder-content">
                            Collections module coming soon...
                        </div>
                    )}

                    {activeTab === 'recoveries' && (
                        <div className="placeholder-content">
                            Recoveries module coming soon...
                        </div>
                    )}
                </div>
            </div>

            {/* Schemes Management Modal */}
            {showSchemesModal && (
                <div className="modal-overlay">
                    <div className="modal-content large-modal">
                        <div className="modal-header">
                            <h2>Manage Scheme Groups</h2>
                            <button onClick={() => setShowSchemesModal(false)} className="close-btn">×</button>
                        </div>
                        <div className="modal-body">
                            {editingGroupId && editGroupData ? (
                                <div className="editor-view">
                                    <div className="editor-header">
                                        <h3>Editing: {editGroupData.name}</h3>
                                        <div className="editor-actions">
                                            <button onClick={handleSaveEdit} className="btn-save">💾 Save Changes</button>
                                            <button onClick={handleBackFromEdit} className="btn-cancel">Cancel</button>
                                        </div>
                                    </div>

                                    <div className="editor-add-row">
                                        <input
                                            placeholder="Enter Scheme Code"
                                            value={newSchemeCode}
                                            onChange={(e) => setNewSchemeCode(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleAddSchemeToEdit()}
                                        />
                                        <button onClick={handleAddSchemeToEdit} className="btn-add-scheme">Add Code</button>
                                    </div>

                                    <div className="scheme-list-container">
                                        <table className="editor-table">
                                            <thead>
                                                <tr>
                                                    <th>Scheme Code</th>
                                                    <th style={{ width: '60px' }}>Action</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {editGroupData.data.map((row, idx) => {
                                                    // Try to find the scheme code key
                                                    const code = row['Scheme Code'] || row['SCHM_CODE'] || row['Code'] || JSON.stringify(row);
                                                    return (
                                                        <tr key={idx}>
                                                            <td>{code}</td>
                                                            <td>
                                                                <button onClick={() => handleRemoveSchemeFromEdit(idx)} className="btn-del-scheme">×</button>
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : (
                                <div className="modal-body-content">
                                    {/* Dedicated Jewel Loan Section */}
                                    <div className="section-block" style={{ marginBottom: '2rem' }}>
                                        <h3 style={{ color: '#1e3a8a', borderBottom: '2px solid #bfdbfe', paddingBottom: '0.5rem' }}>💎 Jewel Loan Schemes (Priority)</h3>

                                        <div className="groups-list">
                                            {schemeGroups.filter(g => g.type === 'Jewel Loan').length === 0 ? (
                                                <div className="empty-sub">No Jewel Loan schemes uploaded.</div>
                                            ) : (
                                                schemeGroups.filter(g => g.type === 'Jewel Loan').map(group => (
                                                    <div key={group.id} className="group-card jewel-card">
                                                        <div className="group-info">
                                                            <div className="group-name">{group.name}</div>
                                                            <div className="group-meta">
                                                                <span className="badge jewel-loan">Jewel Loan</span>
                                                                <span className="count"> • {group.sector || 'Agri'}</span>
                                                                <span className="count"> • {group.data.length} codes</span>
                                                            </div>
                                                            <div className="file-name">📄 {group.fileName || 'Legacy'}</div>
                                                        </div>
                                                        <div className="card-actions">
                                                            <button onClick={() => handleEditClick(group)} className="btn-icon">✏️</button>
                                                            <button onClick={() => handleDeleteGroup(group.id)} className="btn-icon delete">🗑️</button>
                                                        </div>
                                                    </div>
                                                ))
                                            )}
                                        </div>

                                        <div className="add-group-section jewel-add">
                                            <h4>Upload New Jewel Loan File</h4>
                                            <div className="form-row">
                                                <div className="input-group">
                                                    <label>Group Name</label>
                                                    <input
                                                        value={jlGroupName}
                                                        onChange={(e) => setJlGroupName(e.target.value)}
                                                        placeholder="e.g. Gold Loans 2024"
                                                    />
                                                </div>
                                            </div>
                                            <div className="form-row" style={{ alignItems: 'flex-end' }}>
                                                <div className="input-group">
                                                    <label>Sector</label>
                                                    <select
                                                        value={jlSector}
                                                        onChange={(e) => setJlSector(e.target.value)}
                                                    >
                                                        <option value="Agri">Agri</option>
                                                        <option value="Retail">Retail</option>
                                                        <option value="MSME">MSME</option>
                                                    </select>
                                                </div>
                                                <div className="input-group" style={{ flex: 1 }}>
                                                    <label>Select File</label>
                                                    <input
                                                        id="jl-file-input"
                                                        type="file"
                                                        accept=".xlsx,.csv"
                                                        onChange={(e) => handleFileChange(e, 'jl')}
                                                    />
                                                </div>
                                                <button onClick={handleAddJewelGroup} className="btn-add-group btn-jewel">
                                                    Upload JL
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    {/* General Schemes Section */}
                                    <div className="section-block">
                                        <h3 style={{ color: '#374151', borderBottom: '2px solid #e5e7eb', paddingBottom: '0.5rem' }}>📂 Other Schemes</h3>

                                        <div className="groups-list">
                                            {schemeGroups.filter(g => g.type !== 'Jewel Loan').length === 0 ? (
                                                <div className="empty-sub">No other schemes uploaded.</div>
                                            ) : (
                                                schemeGroups.filter(g => g.type !== 'Jewel Loan').map(group => (
                                                    <div key={group.id} className="group-card">
                                                        <div className="group-info">
                                                            <div className="group-name">{group.name}</div>
                                                            <div className="group-meta">
                                                                <span className={`badge ${String(group.type).toLowerCase().replace(' ', '-')}`}>{group.type}</span>
                                                                <span className="count">{group.data.length} codes</span>
                                                            </div>
                                                            <div className="file-name">📄 {group.fileName || 'Legacy'}</div>
                                                        </div>
                                                        <div className="card-actions">
                                                            <button onClick={() => handleEditClick(group)} className="btn-icon">✏️</button>
                                                            <button onClick={() => handleDeleteGroup(group.id)} className="btn-icon delete">🗑️</button>
                                                        </div>
                                                    </div>
                                                ))
                                            )}
                                        </div>

                                        <div className="add-group-section">
                                            <h4>Add General Scheme Group</h4>
                                            <div className="form-row">
                                                <div className="input-group">
                                                    <label>Group Name</label>
                                                    <input
                                                        value={newGroupName}
                                                        onChange={(e) => setNewGroupName(e.target.value)}
                                                        placeholder="e.g. Retail Housing"
                                                    />
                                                </div>
                                                <div className="input-group">
                                                    <label>Type</label>
                                                    <select
                                                        value={newGroupType}
                                                        onChange={(e) => setNewGroupType(e.target.value)}
                                                    >
                                                        <option value="Retail">Retail</option>
                                                        <option value="Agri">Agri</option>
                                                        <option value="MSME">MSME</option>
                                                        <option value="Corporate">Corporate</option>
                                                        <option value="Others">Others</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div className="form-row" style={{ alignItems: 'flex-end' }}>
                                                <div className="input-group" style={{ flex: 1 }}>
                                                    <label>Upload File</label>
                                                    <input
                                                        id="group-file-input"
                                                        type="file"
                                                        accept=".xlsx,.csv"
                                                        onChange={(e) => handleFileChange(e, 'generic')}
                                                    />
                                                </div>
                                                <button onClick={handleAddGroup} className="btn-add-group">
                                                    + Add Group
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                .performance-container { padding: 1.5rem; }
                .card {
                    background: white;
                    border-radius: 0.5rem;
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
                    border: 1px solid #e5e7eb;
                    overflow: hidden;
                }
                .card-header {
                    padding: 1.5rem;
                    border-bottom: 1px solid #e5e7eb;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #f9fafb;
                }
                .title { font-size: 1.5rem; font-weight: 700; color: #1f2937; margin: 0; }
                .header-actions { display: flex; align-items: center; gap: 1rem; }
                .last-updated { font-size: 0.875rem; color: #6b7280; font-style: italic; }
                .btn-update {
                    padding: 0.5rem 1rem;
                    border-radius: 0.375rem;
                    font-weight: 500;
                    color: white;
                    background-color: #2563eb;
                    border: none;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    transition: background-color 0.2s;
                }
                .btn-update:hover { background-color: #1d4ed8; }
                .btn-update:disabled { background-color: #93c5fd; cursor: not-allowed; }
                .btn-schemes { background-color: #16a34a; }
                .btn-schemes:hover { background-color: #15803d; }
                
                .tabs-header {
                    display: flex;
                    border-bottom: 1px solid #e5e7eb;
                    background: white;
                }
                .tab-btn {
                    padding: 0.75rem 1.5rem;
                    font-weight: 500;
                    font-size: 0.875rem;
                    border: none;
                    background: none;
                    cursor: pointer;
                    color: #6b7280;
                    border-bottom: 2px solid transparent;
                    transition: all 0.2s;
                }
                .tab-btn:hover { color: #374151; background-color: #f9fafb; }
                .tab-btn.active {
                    color: #2563eb;
                    border-bottom-color: #2563eb;
                    background-color: #eff6ff;
                }

                .tab-content { min-height: 400px; background: white; }
                .content-pane { padding: 1.5rem; }
                .stats-row { display: flex; gap: 1.5rem; margin-bottom: 1.5rem; }
                .stat-card {
                    padding: 1rem;
                    background: #f8fafc;
                    border-radius: 0.5rem;
                    border: 1px solid #e2e8f0;
                    flex: 1;
                    text-align: center;
                }
                .stat-val { font-size: 1.5rem; font-weight: 700; color: #0f172a; display: block; }
                .stat-lbl { font-size: 0.875rem; color: #64748b; }

                .table-wrapper { overflow-x: auto; border: 1px solid #e5e7eb; border-radius: 0.5rem; }
                .data-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
                .data-table th, .data-table td {
                    padding: 0.75rem 1rem;
                    border-bottom: 1px solid #e5e7eb;
                    text-align: left;
                }
                .data-table th { background-color: #f9fafb; font-weight: 600; color: #374151; }
                .data-table tr:hover { background-color: #f9fafb; }
                .text-red { color: #dc2626; font-weight: 500; }
                .badge {
                    display: inline-block;
                    padding: 0.25rem 0.5rem;
                    border-radius: 9999px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    background-color: #f3f4f6;
                    color: #374151;
                }
                .badge.jewel-loan { background-color: #dbeafe; color: #1e40af; }
                .badge.generic { background-color: #f3f4f6; color: #4b5563; }
                .badge.sme { background-color: #fae8ff; color: #86198f; }
                .badge.agri { background-color: #dcfce7; color: #166534; }
                .badge.retail { background-color: #ffedd5; color: #9a3412; }

                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 1.5rem;
                    padding: 1.5rem;
                }
                .dash-card {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 0.75rem;
                    padding: 1.25rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                .dash-header { display: flex; justify-content: space-between; align-items: center; }
                .dash-icon { font-size: 2rem; background: #f8fafc; padding: 0.5rem; border-radius: 0.5rem; width: fit-content; }
                .dash-title { font-size: 1.125rem; font-weight: 600; color: #1e293b; }
                .dash-stats { display: flex; gap: 1rem; margin-top: 0.5rem; }
                .stat-box { flex: 1; background: #f1f5f9; padding: 0.75rem; border-radius: 0.5rem; }
                .stat-box .lbl { display: block; font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem; }
                .stat-box .val { display: block; font-size: 1.125rem; font-weight: 700; color: #0f172a; }
                .dash-alert {
                    margin-top: auto;
                    background: #fef2f2;
                    border: 1px solid #fee2e2;
                    border-radius: 0.5rem;
                    padding: 0.75rem;
                }
                .alert-header { font-size: 0.875rem; font-weight: 600; color: #991b1b; margin-bottom: 0.5rem; }
                .alert-list { list-style: none; padding: 0; margin: 0; font-size: 0.75rem; color: #7f1d1d; }
                .alert-list li { margin-bottom: 0.25rem; padding-bottom: 0.25rem; border-bottom: 1px dashed #fca5a5; }
                .alert-list li:last-child { border-bottom: none; margin-bottom: 0; }

                /* Modal Styles */
                .modal-overlay {
                    position: fixed;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 50;
                }
                .modal-content {
                    background: white;
                    border-radius: 0.75rem;
                    width: 90%;
                    max-width: 500px;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                }
                .large-modal { max-width: 800px; }
                .modal-header {
                    padding: 1.25rem 1.5rem;
                    border-bottom: 1px solid #e5e7eb;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .modal-header h2 { margin: 0; font-size: 1.25rem; }
                .close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; }
                .modal-body { padding: 1.5rem; }

                .groups-list { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; }
                .group-card {
                    border: 1px solid #e5e7eb;
                    border-radius: 0.5rem;
                    padding: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #f9fafb;
                }
                .jewel-card { border-color: #bfdbfe; background: #eff6ff; }
                .group-info { display: flex; flex-direction: column; gap: 0.25rem; }
                .group-name { font-weight: 600; color: #1f2937; }
                .group-meta { display: flex; gap: 0.5rem; align-items: center; font-size: 0.875rem; color: #6b7280; }
                .file-name { font-size: 0.75rem; color: #9ca3af; font-style: italic; }

                .section-block { margin-bottom: 2rem; }
                .add-group-section { background: #f3f4f6; padding: 1.25rem; border-radius: 0.5rem; }
                .jewel-add { background: #dbeafe; }
                .form-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
                .input-group { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
                .input-group label { font-size: 0.875rem; font-weight: 500; color: #374151; }
                .input-group input, .input-group select {
                    padding: 0.5rem;
                    border: 1px solid #d1d5db;
                    border-radius: 0.375rem;
                }
                .btn-add-group {
                    padding: 0.5rem 1rem;
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 0.375rem;
                    font-weight: 500;
                    cursor: pointer;
                    height: 38px;
                }
                .btn-jewel { background: #1e40af; }
                .empty-sub { text-align: center; color: #9ca3af; padding: 1rem; border: 1px dashed #e5e7eb; border-radius: 0.5rem; }

                .editor-view { background: #f8fafc; border-radius: 8px; overflow: hidden; }
                .editor-header { padding: 1rem; background: #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
                .editor-header h3 { margin: 0; font-size: 1.1rem; }
                .btn-save { background: #16a34a; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin-right: 0.5rem; }
                .btn-cancel { background: #64748b; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
                .editor-add-row { padding: 1rem; background: #fff; border-bottom: 1px solid #e2e8f0; display: flex; gap: 0.5rem; }
                .editor-add-row input { flex: 1; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px; }
                .btn-add-scheme { background: #2563eb; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
                .scheme-list-container { max-height: 400px; overflow-y: auto; padding: 0; }
                .editor-table { width: 100%; border-collapse: collapse; }
                .editor-table th { position: sticky; top: 0; background: #f1f5f9; padding: 0.5rem; text-align: left; font-size: 0.85rem; }
                .editor-table td { padding: 0.5rem; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
                .btn-del-scheme { background: #ef4444; color: white; border: none; width: 24px; height: 24px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
                .card-actions { display: flex; gap: 0.5rem; }
                .btn-icon { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 0.2rem; }
                .btn-icon:hover { background: rgba(0,0,0,0.05); border-radius: 4px; }
                .btn-icon.delete:hover { background: #fee2e2; }

                /* Risk Summary Styles */
                .risk-summary { margin-top: 1rem; border-top: 1px solid #e5e7eb; padding-top: 0.5rem; font-size: 0.75rem; }
                .risk-row { display: grid; grid-template-columns: 1fr 0.8fr 1.5fr; gap: 0.5rem; padding: 0.15rem 0; color: #4b5563; }
                .risk-row.header { font-weight: 600; color: #6b7280; border-bottom: 1px dashed #e5e7eb; margin-bottom: 0.25rem; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; }
                .row-npa { color: #dc2626; font-weight: 600; background: #fef2f2; border-radius: 2px; }
            `}</style>
        </div>
    );
};

export default BranchPerformance;
