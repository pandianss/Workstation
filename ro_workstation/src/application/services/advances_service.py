import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

class AdvancesService:
    """
    Service for processing and analyzing Bank Advances data (Loans).
    Incorporate logic from React sample: BranchPerformance.jsx
    """
    
    def __init__(self, config_path="data/scheme_config.json"):
        self.config_path = config_path
        self.scheme_map = self._load_scheme_map()
        
    def _load_scheme_map(self):
        """Load 3-level classification map (Scheme Code -> Category/Sector/Name)"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def process_excel(self, file_path_or_buffer):
        """Parse Excel file and enrich with banking metadata"""
        df = pd.read_excel(file_path_or_buffer)
        
        # 1. Normalize Column Names (Stripping whitespace and case-insensitive)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 2. Smart Column Detection
        col_map = {
            'SCHM_CODE': ['SCHEME CODE', 'SCHM_CODE', 'CODE', 'SCHEME', 'SCHEME_CODE'],
            'OPEN_DT': ['OPEN_DT', 'OPEN DATE', 'DATE_OPENED'],
            'NET_BALANCE': ['NET_BALANCE', 'BALANCE', 'CLEAR BALANCE', 'OUTSTANDING'],
            'DOC_AMOUNT': ['DOC_AMOUNT', 'SANCTION LIMIT', 'SANCTION_AMT', 'LIMIT'],
            'PRIORITY_TYPE': ['PRIORITY_TYPE', 'PRIORITY TYPE', 'SEGMENT', 'SECTOR'],
            'GL_SUB_CD': ['GL_SUB_CD', 'GL CODE', 'GL_CODE'],
            'SMA_TYPE': ['SMA_TYPE', 'SMA TYPE', 'SMA_CLASS']
        }
        
        normalized_df = pd.DataFrame()
        for target, aliases in col_map.items():
            found = False
            for alias in aliases:
                if alias.upper() in df.columns:
                    normalized_df[target] = df[alias.upper()]
                    found = True
                    break
            if not found:
                normalized_df[target] = None

        # Add remaining columns
        for col in df.columns:
            if col not in normalized_df.columns:
                normalized_df[col] = df[col]

        # 3. Data Normalization & Enrichment
        return self._enrich_data(normalized_df)

    def _enrich_data(self, df):
        """Apply business logic for classification and risk"""
        
        # Normalize Priority Type (SME, Retail, etc.)
        def normalize_priority(val):
            val = str(val or '').strip().upper()
            if any(x in val for x in ['SME', 'MSME']): return 'SME'
            if 'RETAIL' in val: return 'RETAIL'
            if 'AGRI' in val: return 'AGRI'
            if any(x in val for x in ['CORP', 'COMMERCIAL']): return 'CORPORATE'
            return 'OTHERS'
        
        df['PRIORITY_TYPE_NORM'] = df['PRIORITY_TYPE'].apply(normalize_priority)

        # Date Parsing & FY Calculation
        def parse_date_and_fy(val):
            if pd.isna(val): return None, None
            val = str(val).strip()
            dt = None
            try:
                if len(val) == 8 and val.isdigit(): # YYYYMMDD
                    dt = datetime.strptime(val, '%Y%m%d')
                else: # Try DD-MM-YYYY or other formats
                    dt = pd.to_datetime(val, dayfirst=True)
            except:
                return None, None
            
            if dt:
                # FY logic: April to March
                fy_start = dt.year if dt.month >= 4 else dt.year - 1
                fy_str = f"FY {fy_start}-{fy_start + 1}"
                return dt, fy_str
            return None, None

        dates_fys = df['OPEN_DT'].apply(parse_date_and_fy)
        df['OPEN_DT_NORM'] = [d[0] for d in dates_fys]
        df['FY'] = [d[1] for d in dates_fys]

        # Balance Normalization (Crores, Absolute)
        df['BALANCE_CR'] = df['NET_BALANCE'].apply(lambda x: abs(float(x or 0)) / 10000000)
        df['LIMIT_CR'] = df['DOC_AMOUNT'].apply(lambda x: abs(float(x or 0)) / 10000000)

        # 4. 3-Level Classification
        def classify_scheme(row):
            code = str(row['SCHM_CODE'] or '').strip().lower()
            match = self.scheme_map.get(code)
            
            if match:
                return match.get('l1', 'Others'), match.get('l2', 'Others'), match.get('l3', 'Others')
            
            # Fallback based on Priority Type
            p_type = row['PRIORITY_TYPE_NORM']
            if p_type == 'RETAIL': return 'Non-Jewel Loan', 'Core Retail', 'Other Retail'
            if p_type == 'SME': return 'Non-Jewel Loan', 'Core MSME', 'Other SME'
            if p_type == 'AGRI': return 'Non-Jewel Loan', 'Core Agri', 'Other Agri'
            
            return 'Others', 'Others', 'Unclassified'

        classification = df.apply(classify_scheme, axis=1, result_type='expand')
        df['L1_CATEGORY'] = classification[0]
        df['L2_SECTOR'] = classification[1]
        df['L3_SCHEME'] = classification[2]

        # 5. Risk Mapping (NPA/SMA)
        npa_gls = ['33750', '33850', '33950', '33999']
        def map_risk(row):
            gl = str(row['GL_SUB_CD'] or '').strip()
            sma = str(row['SMA_TYPE'] or '').strip().upper()
            
            if gl in npa_gls: return 'NPA'
            if '0' in sma: return 'SMA-0'
            if '1' in sma: return 'SMA-1'
            if '2' in sma: return 'SMA-2'
            return 'REGULAR'

        df['RISK_CATEGORY'] = df.apply(map_risk, axis=1)
        
        return df

    def get_summary_stats(self, df):
        """Calculate dashboard-ready metrics"""
        if df.empty: return {}
        
        summary = {
            'total_count': len(df),
            'total_balance_cr': df['BALANCE_CR'].sum(),
            'total_limit_cr': df['LIMIT_CR'].sum(),
            'by_category': df.groupby('L1_CATEGORY')['BALANCE_CR'].sum().to_dict(),
            'by_sector': df.groupby('L2_SECTOR')['BALANCE_CR'].agg(['count', 'sum']).to_dict('index'),
            'risk_summary': df.groupby('RISK_CATEGORY')['BALANCE_CR'].agg(['count', 'sum']).to_dict('index'),
            'fy_summary': df.groupby('FY')['BALANCE_CR'].sum().to_dict()
        }
        
        return summary
