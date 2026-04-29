import pandas as pd
import numpy as np
import streamlit as st
import shutil
from modules.utils.paths import project_path
from modules.mis.engine import (
    get_all_mis_data,
    is_file_ingested,
    mark_file_ingested,
    save_mis_records,
)

MIS_DIR = project_path("mis")
ARCHIVE_DIR = MIS_DIR / "archive"


def _ingest_new_files():
    if not MIS_DIR.exists():
        MIS_DIR.mkdir(parents=True, exist_ok=True)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    file_paths = list(MIS_DIR.glob("*.xlsx"))
    if not file_paths:
        return

    for f_path in file_paths:
        if is_file_ingested(f_path.name):
            continue

        try:
            df = pd.read_excel(f_path)
            
            # Date conversion for storage
            if "DATE" in df.columns:
                df["DATE"] = pd.to_datetime(
                    df["DATE"].astype(str).str.split(".").str[0],
                    format="%Y%m%d",
                    errors="coerce",
                )

            records = df.to_dict("records")
            save_mis_records(records)
            mark_file_ingested(f_path.name)

            # Archive the file to keep the ingestion zone clean
            shutil.move(str(f_path), str(ARCHIVE_DIR / f_path.name))

        except Exception as e:
            st.error(f"Error ingesting {f_path.name}: {e}")


@st.cache_data
def load_mis_data():
    _ingest_new_files()
    master_df = get_all_mis_data()

    if master_df.empty:
        return master_df

    # Standardize column names to UPPERCASE for the rest of the app logic
    # SQL Columns: sb, cd, td, bulk_dep -> SB, CD, TD, BULK DEP
    master_df.columns = [c.upper().replace("_", " ") for c in master_df.columns]

    # Ensure DATE is datetime
    master_df["DATE"] = pd.to_datetime(master_df["DATE"])

    def safe_sum(df, cols):
        existing_cols = [c for c in cols if c in df.columns]
        return df[existing_cols].fillna(0).sum(axis=1)

    master_df["CORE RETAIL"] = safe_sum(
        master_df,
        ["HOUSING", "VEHICLE", "PERSONAL", "MORTGAGE", "EDUCATION", "LIQUIRENT", "OTHER RETAIL"],
    )
    master_df["Total Advances"] = safe_sum(master_df, ["CORE AGRI", "GOLD", "MSME", "CORE RETAIL"])
    master_df["CASA"] = safe_sum(master_df, ["SB", "CD"])

    td = master_df["TD"].fillna(0) if "TD" in master_df.columns else 0
    bulk = master_df["BULK DEP"].fillna(0) if "BULK DEP" in master_df.columns else 0
    master_df["Ret TD"] = td - bulk
    master_df["Total Deposits"] = safe_sum(master_df, ["SB", "CD", "TD"])

    master_df["CD Ratio"] = np.where(
        master_df["Total Deposits"] > 0,
        (master_df["Total Advances"] / master_df["Total Deposits"] * 100),
        0,
    )
    master_df["CD Ratio"] = master_df["CD Ratio"].round(2)

    master_df["Total Cash"] = safe_sum(master_df, ["CASH ON HAND", "ATM CASH", "BC CASH", "BNA CASH"])
    crl = master_df["CRL"].fillna(0) if "CRL" in master_df.columns else 0
    master_df["Cash vs CRL"] = master_df["Total Cash"] - crl

    master_df["Total Recovery"] = safe_sum(master_df, ["REC Q1", "REC Q2", "REC Q3", "REC Q4"])

    npa = master_df["NPA"].fillna(0) if "NPA" in master_df.columns else 0
    master_df["NPA %"] = np.where(
        master_df["Total Advances"] > 0,
        (npa / master_df["Total Advances"] * 100),
        0,
    )
    master_df["NPA %"] = master_df["NPA %"].round(2)

    return master_df
