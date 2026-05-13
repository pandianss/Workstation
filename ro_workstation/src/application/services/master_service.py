from __future__ import annotations

import pandas as pd
import datetime
import os
import json
from src.infrastructure.persistence.master_repository import MasterRepository
from src.domain.models.master import MasterRecord

class SalutationMapper:
    """Helper to map gender to trilingual salutations."""
    MAPPINGS = {
        "M": {"en": "Shri.", "hi": "श्री", "ta": "திரு"},
        "F": {"en": "Smt.", "hi": "श्रीमती", "ta": "திருமதி"},
        "O": {"en": "Ms.", "hi": "सुश्री", "ta": "செல்வி"}
    }

    @classmethod
    def get_trilingual(cls, gender: str) -> dict:
        """Get dict with en, hi, ta salutations."""
        g = str(gender).upper().strip() if gender else "M"
        return cls.MAPPINGS.get(g, cls.MAPPINGS["M"])

class DesignationMapper:
    """Helper to map English designations to Hindi and Tamil."""
    MAPPINGS = {
        "SENIOR REGIONAL MANAGER": {"hi": "वरिष्ठ क्षेत्रीय प्रबंधक", "ta": "முதன்மை மண்டல மேலாளர்"},
        "CHIEF REGIONAL MANAGER": {"hi": "मुख्य क्षेत्रीय प्रबंधक", "ta": "தலைமை மண்டல மேலாளர்"},
        "REGIONAL MANAGER": {"hi": "क्षेत्रीय प्रबंधक", "ta": "மண்டல மேலாளர்"},
        "CHIEF MANAGER": {"hi": "मुख्य प्रबंधक", "ta": "முதன்மை மேலாளர்"},
        "SENIOR MANAGER": {"hi": "वरिष्ठ प्रबंधक", "ta": "மூத்த மேலாளர்"},
        "ASST MANAGER": {"hi": "सहायक प्रबंधक", "ta": "உதவி மேலாளர்"},
        "ASSISTANT MANAGER": {"hi": "सहायक प्रबंधक", "ta": "உதவி மேலாளர்"},
        "MANAGER": {"hi": "प्रबंधक", "ta": "மேலாளர்"},
        "OFFICER": {"hi": "अधिकारी", "ta": "அதிகாரி"},
        "CUSTOMER SERVICE ASSOCIATE": {"hi": "ग्राहक सेवा सहयोगी", "ta": "வாடிக்கையாளர் சேவை உதவியாளர்"},
        "CSA": {"hi": "ग्राहक सेवा सहयोगी", "ta": "வாடிக்கையாளர் சேவை உதவியாளர்"},
        "PART TIME HOUSE KEEPER": {"hi": "अंशकालिक हाउस कीपर", "ta": "பகுதி நேர தூய்மை பணியாளர்"},
        "PTHK": {"hi": "अंशकालिक हाउस कीपर", "ta": "பகுதி நேர தூய்மை பணியாளர்"},
        "SWEEPER": {"hi": "सफाई कर्मचारी", "ta": "தூய்மை பணியாளர்"}
    }

    @classmethod
    def get_trilingual(cls, desig_en: str) -> dict:
        """Get dict with en, hi, ta designations with longest-match priority."""
        d_up = str(desig_en).upper().strip()
        
        # Sort keys by length descending to ensure longest match (e.g. SENIOR REGIONAL MANAGER) 
        # is checked before shorter substrings (e.g. REGIONAL MANAGER)
        sorted_keys = sorted(cls.MAPPINGS.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            if key in d_up:
                trans = cls.MAPPINGS[key]
                return {"en": desig_en, "hi": trans["hi"], "ta": trans["ta"]}
        
        # Default fallback
        return {"en": desig_en, "hi": desig_en, "ta": desig_en}
class MasterService:
    def __init__(self) -> None:
        self.repo = MasterRepository()

    def get_units_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("UNIT")
        staff = {s.code: s.name_en for s in self.repo.get_by_category("STAFF")}
        
        cols = ["Code", "Name", "Type", "District", "Population Group", "Head", "2nd Line", "Effective From", "Open Date", "Active"]
        data = []
        for r in records:
            meta = r.metadata or {}
            h_id = meta.get("headUserId")
            s_id = meta.get("secondLineUserId")
            
            data.append({
                "Code": str(r.code),
                "Name": r.name_en,
                "Type": meta.get("type"),
                "District": meta.get("district"),
                "Population Group": meta.get("populationGroup"),
                "Head": staff.get(str(h_id), "None") if h_id else "None",
                "2nd Line": staff.get(str(s_id), "None") if s_id else "None",
                "Effective From": pd.to_datetime(meta.get("authority_from"), errors='coerce'),
                "Open Date": pd.to_datetime(meta.get("openDate"), errors='coerce'),
                "Active": r.is_active
            })
        return pd.DataFrame(data, columns=cols)

    def get_departments_frame(self) -> pd.DataFrame:
        records = self.repo.get_by_category("DEPT")
        cols = ["Code", "Name (En)", "Name (Hi)", "Name (Ta)", "Email", "Active"]
        data = []
        for r in records:
            meta = r.metadata or {}
            data.append({
                "Code": r.code,
                "Name (En)": r.name_en,
                "Name (Hi)": r.name_hi or "",
                "Name (Ta)": r.name_local or "",
                "Email": meta.get("email", ""),
                "Active": r.is_active
            })
        return pd.DataFrame(data, columns=cols)

    def get_staff_frame(self) -> pd.DataFrame:
        """Return staff as a DataFrame for UI display."""
        staff = self.repo.get_by_category("STAFF")
        cols = [
            "Roll No", "Name (En)", "Name (Hi)", "Name (Ta)", 
            "Branch SOL", "Designation", "Designation (Hi)", "Designation (Ta)",
            "Posting From", "Posting To", "DOB", "DOJ", "DOR", "Grade WEF", "Branch WEF", "Active"
        ]
        data = []
        for s in staff:
            meta = s.metadata or {}
            data.append({
                "Roll No": s.code,
                "Name (En)": s.name_en,
                "Name (Hi)": s.name_hi or "",
                "Name (Ta)": s.name_local or "",
                "Branch SOL": meta.get("sol", ""),
                "Designation": meta.get("designation", ""),
                "Designation (Hi)": meta.get("desig_hi", ""),
                "Designation (Ta)": meta.get("desig_ta", ""),
                "Grade": meta.get("grade", ""),
                "Mobile": meta.get("mobile", ""),
                "Gender": meta.get("gender", "M"),
                "Departments": ", ".join(meta.get("departments", [])) if isinstance(meta.get("departments"), list) else "",
                "Posting From": pd.to_datetime(meta.get("posting_from"), errors='coerce'),
                "Posting To": pd.to_datetime(meta.get("posting_to"), errors='coerce'),
                "DOB": pd.to_datetime(meta.get("dob"), errors='coerce'),
                "DOJ": pd.to_datetime(meta.get("doj"), errors='coerce'),
                "DOR": pd.to_datetime(meta.get("dor"), errors='coerce'),
                "Grade WEF": pd.to_datetime(meta.get("grade_wef"), errors='coerce'),
                "Branch WEF": pd.to_datetime(meta.get("branch_wef"), errors='coerce'),
                "Active": s.is_active
            })
        return pd.DataFrame(data, columns=cols)

    def sync_staff_from_csv(self) -> None:
        """Ingest staff from CSV or Excel files, including seeding files."""
        from src.core.paths import project_path
        import pandas as pd
        import os
        
        # 1. Base Staff Data (CSV or Excel)
        # Try finding Excel first in root
        project_root = project_path("files")
        excel_path = next(project_root.glob("Staff Details*.xlsx"), None)
        
        print(f"Sync: Scanning for staff data in {project_root}")
        if excel_path and excel_path.exists():
            print(f"Sync: Found Excel source at {excel_path.name}")
            df = pd.read_excel(excel_path)
        else:
            # Try files/Staff.csv
            csv_path = project_path("files", "Staff.csv")
            df = pd.read_csv(csv_path) if csv_path.exists() else pd.DataFrame()
            
        if df.empty:
            print("No base staff data found. Skipping sync to prevent deactivation.")
            return
            
        # 2. Supplementary Date Seeding (StfData.csv)
        seed_path = project_path("files", "StfData.csv")
        seed_df = pd.read_csv(seed_path) if seed_path.exists() else pd.DataFrame()
        
        df.columns = [str(c).strip() for c in df.columns]
        if not seed_df.empty:
            seed_df.columns = [str(c).strip() for c in seed_df.columns]
            # Normalize Seed Roll
            s_roll_col = next((c for c in seed_df.columns if c.lower() in ["roll", "rollno", "roll no"]), None)
            if s_roll_col:
                seed_df[s_roll_col] = seed_df[s_roll_col].apply(lambda x: str(int(float(x))).lstrip('0') if pd.notna(x) else "")
                seed_df = seed_df.set_index(s_roll_col)
        
        # Load everything up front - Normalize keys by stripping leading zeros
        staff_records = {str(r.code).lstrip('0'): r for r in self.repo.get_by_category("STAFF")}
        unit_records = {str(u.code).zfill(4): u for u in self.repo.get_by_category("UNIT")}
        
        to_save_staff = []
        to_save_units = {} # Use a dict indexed by code to handle unhashable MasterRecord
        incoming_rolls = set()
        
        for _, row in df.iterrows():
            try:
                # Case-insensitive robust mapping with space stripping
                r_map = {str(k).strip().lower(): v for k, v in row.items()}
                
                # Support both Bank Format and UI Export Format
                raw_roll = r_map.get("roll", 
                           r_map.get("roll no", 
                           r_map.get("rollno", "")))
                if not raw_roll: continue
                
                # Robust Roll parsing (handle 48243.0 and leading zeros)
                try:
                    roll_clean = str(int(float(str(raw_roll).strip()))).lstrip('0')
                    # Keep original code format but use clean for matching
                    match_key = roll_clean
                except:
                    match_key = str(raw_roll).strip().lstrip('0')
                
                if not match_key: continue
                
                raw_sol = str(r_map.get("br cd", 
                              r_map.get("br code", 
                              r_map.get("branch sol", 
                              r_map.get("sol", ""))))).strip()
                if not raw_sol or raw_sol.lower() == "nan": continue
                
                # Robust SOL parsing
                try:
                    sol = str(int(float(raw_sol))).zfill(4)
                except:
                    sol = str(raw_sol).zfill(4)
                
                name_en = str(r_map.get("name", r_map.get("name (en)", ""))).strip()
                name_hi = str(r_map.get("name (hi)", "")).strip()
                name_ta = str(r_map.get("name (ta)", "")).strip()
                
                desig = str(r_map.get("designation", "")).strip()
                grade = str(r_map.get("grade", "")).strip()
                mobile = str(r_map.get("mobile number", r_map.get("mobile", ""))).strip()
                status = str(r_map.get("status", "")).strip()
                effective = str(r_map.get("effective", "")).strip()
                gender = str(r_map.get("gender", "M")).strip()
                
                # Clean date parsing for Excel and DD.MM.YYYY
                def clean_date(val):
                    if pd.isna(val) or str(val).lower() == "nat" or not str(val).strip(): return ""
                    if isinstance(val, (datetime.datetime, datetime.date)):
                        return val.strftime("%d.%m.%Y")
                    # Handle DD.MM.YYYY
                    s_val = str(val).strip()
                    if "." in s_val and len(s_val.split(".")) == 3:
                        try:
                            d, m, y = s_val.split(".")
                            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                        except: pass
                    return s_val.split(" ")[0] # Remove time part if present

                dob = clean_date(r_map.get("date of birth", r_map.get("dob", "")))
                doj = clean_date(r_map.get("date of joining", r_map.get("doj", "")))
                dor = clean_date(r_map.get("date of retirement", r_map.get("dor", "")))
                
                # Override with seed data if available
                if not seed_df.empty and match_key in seed_df.index:
                    s_row = seed_df.loc[match_key]
                    s_map = {str(k).strip().lower(): v for k, v in s_row.to_dict().items()}
                    s_dob = clean_date(s_map.get("dob", ""))
                    s_dor = clean_date(s_map.get("dor", ""))
                    if s_dob: dob = s_dob
                    if s_dor: dor = s_dor

                # Support shorthand from regional Excel files
                grade_wef = clean_date(r_map.get("current grade with effect from", 
                                       r_map.get("grade wef", 
                                       r_map.get("cugrwef", ""))))
                branch_wef = clean_date(r_map.get("current branch with effect from", 
                                        r_map.get("branch wef", 
                                        r_map.get("curbrwef", ""))))
                region_wef = clean_date(r_map.get("region with effect from", 
                                        r_map.get("region wef", 
                                        r_map.get("regwef", ""))))

                incoming_rolls.add(match_key)
                # Debug first few rows
                if len(incoming_rolls) < 5:
                    print(f"Sync Trace: MatchKey={match_key}, Name={name_en}, DOB={dob}")
                
                # Designation Mapping
                trilingual_desig = DesignationMapper.get_trilingual(desig)
                
                # Staff Update
                if match_key in staff_records:
                    staff = staff_records[match_key]
                    meta = dict(staff.metadata or {})
                    meta.update({
                        "sol": sol, 
                        "designation": desig,
                        "desig_en": trilingual_desig["en"],
                        "desig_hi": trilingual_desig["hi"],
                        "desig_ta": trilingual_desig["ta"],
                        "grade": grade, 
                        "mobile": mobile,
                        "status": status,
                        "gender": gender,
                        "dob": dob,
                        "doj": doj,
                        "dor": dor,
                        "grade_wef": grade_wef,
                        "branch_wef": branch_wef,
                        "region_wef": region_wef
                    })
                    staff.metadata = meta
                    staff.name_en = name_en
                    staff.name_hi = name_hi
                    staff.name_local = name_ta
                    staff.is_active = True
                    to_save_staff.append(staff)
                else:
                    new_staff = MasterRecord(
                        category="STAFF", code=str(raw_roll).strip(), 
                        name_en=name_en, 
                        name_hi=name_hi,
                        name_local=name_ta,
                        is_active=True,
                        metadata={
                            "sol": sol, 
                            "designation": desig,
                            "desig_en": trilingual_desig["en"],
                            "desig_hi": trilingual_desig["hi"],
                            "desig_ta": trilingual_desig["ta"],
                            "grade": grade, 
                            "mobile": mobile, 
                            "status": status,
                            "gender": gender,
                            "dob": dob,
                            "doj": doj,
                            "dor": dor,
                            "grade_wef": grade_wef,
                            "branch_wef": branch_wef,
                            "region_wef": region_wef,
                            "postings": []
                        }
                    )
                    to_save_staff.append(new_staff)
                
                # Authority Update
                if sol in unit_records:
                    unit = unit_records[sol]
                    u_meta = dict(unit.metadata or {})
                    
                    assigned = False
                    if "BH" in status:
                        u_meta["headUserId"] = roll
                        if effective and str(effective).lower() != "nan":
                            u_meta["authority_from"] = effective
                        assigned = True
                    elif "2nd" in status:
                        u_meta["secondLineUserId"] = roll
                        assigned = True
                    
                    if assigned:
                        unit.metadata = u_meta
                        to_save_units[sol] = unit
            except Exception as e:
                print(f"Error processing staff row: {e}")
                continue
        
        # Deactivate missing staff - ONLY if we have a healthy amount of incoming data
        if len(incoming_rolls) > (len(staff_records) * 0.5):
            for roll_match, staff in staff_records.items():
                if roll_match not in incoming_rolls:
                    staff.is_active = False
                    to_save_staff.append(staff)
        else:
            print(f"Suspiciously low staff count ({len(incoming_rolls)} vs {len(staff_records)}). Skipping deactivation safety check.")
        
        # Bulk Save
        if to_save_staff:
            self.repo.save_all(to_save_staff)
        if to_save_units:
            self.repo.save_all(list(to_save_units.values()))

        # Mark as synced
        sync_file = project_path("data", "master_sync.json")
        sync_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sync_file, 'w') as f:
            json.dump({"last_sync": str(datetime.datetime.now())}, f)

        # Clear Anniversary Cache to reflect new dates immediately
        try:
            import streamlit as st
            st.cache_data.clear()
            print("Sync: Streamlit cache invalidated successfully.")
        except: pass

    def sync_units_from_csv(self) -> None:
        """Fast synchronization of regional units."""
        from src.core.paths import project_path
        csv_path = project_path("files", "branches.csv")
        if not csv_path.exists(): return
        
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        db_units = {str(u.code).zfill(4): u for u in self.repo.get_by_category("UNIT")}
        to_save = []
        incoming_codes = set()
        
        for _, row in df.iterrows():
            code = str(row["code"]).zfill(4)
            incoming_codes.add(code)
            
            meta = {
                "type": str(row["type"]),
                "district": str(row["district"]),
                "populationGroup": str(row["populationGroup"]),
                "address": str(row["address"]),
                "size": str(row.get("size", "MEDIUM")),
                "openDate": str(row.get("openDate", ""))
            }
            # Only include head/2nd if they exist in CSV to avoid wiping staff sync
            if pd.notna(row.get("headUserId")): meta["headUserId"] = str(row["headUserId"])
            if pd.notna(row.get("secondLineUserId")): meta["secondLineUserId"] = str(row["secondLineUserId"])
            
            if code in db_units:
                unit = db_units[code]
                unit.name_en = str(row["nameEn"])
                old_meta = unit.metadata or {}
                old_meta.update(meta)
                unit.metadata = old_meta
                unit.is_active = True
                to_save.append(unit)
            else:
                new_unit = MasterRecord(
                    category="UNIT", code=code, name_en=str(row["nameEn"]),
                    is_active=True, metadata=meta
                )
                to_save.append(new_unit)
                
        # Deactivate missing
        for code, unit in db_units.items():
            if code not in incoming_codes:
                unit.is_active = False
                to_save.append(unit)
                
        if to_save:
            self.repo.save_all(to_save)

    def sync_departments_from_csv(self) -> None:
        """Fast synchronization of regional departments."""
        from src.core.paths import project_path
        csv_path = project_path("files", "departments.csv")
        if not csv_path.exists(): return
        
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        db_depts = {r.code: r for r in self.repo.get_by_category("DEPT")}
        to_save = []
        incoming_codes = set()
        
        for _, row in df.iterrows():
            code = str(row["dept_code"]).strip()
            incoming_codes.add(code)
            
            if code in db_depts:
                dept = db_depts[code]
                dept.name_en = str(row["dept_en"])
                dept.name_hi = str(row["dept_hi"])
                dept.name_local = str(row["dept_ta"])
                dept.metadata = {"email": str(row["email"])}
                dept.is_active = True
                to_save.append(dept)
            else:
                new_dept = MasterRecord(
                    category="DEPT", code=code, 
                    name_en=str(row["dept_en"]),
                    name_hi=str(row["dept_hi"]),
                    name_local=str(row["dept_ta"]),
                    is_active=True, 
                    metadata={"email": str(row["email"])}
                )
                to_save.append(new_dept)
        
        # Deactivate missing
        for code, dept in db_depts.items():
            if code not in incoming_codes:
                dept.is_active = False
                to_save.append(dept)
                
        if to_save:
            self.repo.save_all(to_save)

    def get_ro_executives(self) -> list[dict[str, str]]:
        """Get staff members at RO (3933) who are executives (Scale II+)."""
        staff = self.repo.get_by_category("STAFF")
        execs = []
        for s in staff:
            meta = s.metadata or {}
            # Match SOL 3933 specifically
            if str(meta.get("sol")) == "3933":
                grade = meta.get("grade", "")
                # Scale II (MM II) and above are usually eligible for signing authority
                if any(g in grade for g in ["MM II", "MM III", "SM IV", "SM V", "TEG VI", "TEG VII"]):
                    execs.append({
                        "roll": s.code,
                        "name": s.name_en
                    })
        # Sort by name for better UI selection
        return sorted(execs, key=lambda x: x["name"])

    def allot_staff_to_departments(self, roll: str, dept_codes: list[str]) -> bool:
        """Allot staff to one or more departments."""
        staff = next((r for r in self.repo.get_by_category("STAFF") if r.code == roll), None)
        if not staff: return False
        
        meta = staff.metadata or {}
        meta["departments"] = dept_codes
        staff.metadata = meta
        self.repo.save(staff)
        return True

    def update_staff_details(self, roll: str, name_hi: str, name_ta: str, sol: str, desig: str, gender: str, p_from: str, p_to: str) -> bool:
        """Update staff profile and archive history if SOL/Desig changes."""
        staff_list = self.repo.get_by_category("STAFF")
        staff = next((s for s in staff_list if s.code == roll), None)
        if not staff: return False
        
        staff.name_hi = name_hi
        staff.name_local = name_ta
        
        meta = staff.metadata or {}
        # Archive history if sol or desig changed
        if meta.get("sol") != sol or meta.get("designation") != desig:
            history = meta.get("postings", [])
            history.append({
                "sol": meta.get("sol"),
                "designation": meta.get("designation"),
                "from": meta.get("posting_from"),
                "to": datetime.date.today().strftime("%d.%m.%Y")
            })
            meta["postings"] = history
            
        trilingual_desig = DesignationMapper.get_trilingual(desig)
        meta["sol"] = sol
        meta["designation"] = desig
        meta["desig_en"] = trilingual_desig["en"]
        meta["desig_hi"] = trilingual_desig["hi"]
        meta["desig_ta"] = trilingual_desig["ta"]
        meta["posting_from"] = p_from
        meta["posting_to"] = p_to
        meta["gender"] = gender
        
        staff.metadata = meta
        self.repo.save(staff)
        
        # Update Staff.csv to reflect manual change (prevents sync regression)
        try:
            self._write_back_to_staff_csv()
        except Exception as e:
            print(f"Warning: Failed to update Staff.csv: {e}")
            
        return True

    def _write_back_to_staff_csv(self) -> None:
        """Write current staff records back to Staff.csv to keep them in sync with manual UI edits."""
        from src.core.paths import project_path
        csv_path = project_path("files", "Staff.csv")
        df = self.get_staff_frame()
        # Ensure we save in a format compatible with our sync logic
        df.to_csv(csv_path, index=False)
        # Update sync state to prevent immediate re-sync
        state_path = project_path("data", "master_sync.json")
        if state_path.exists():
            with open(state_path, "r") as f: state = json.load(f)
            state["staff"] = os.path.getmtime(csv_path)
            with open(state_path, "w") as f: json.dump(state, f)

    def sync_if_needed(self, force: bool = False) -> None:
        from src.core.paths import project_path
        import json
        state_path = project_path("data", "master_sync.json")
        state = {}
        if state_path.exists():
            try:
                with open(state_path, "r") as f: state = json.load(f)
            except: state = {}
        
        files = {
            "staff_csv": project_path().parent / "files" / "Staff.csv",
            "branches": project_path().parent / "files" / "branches.csv",
            "departments": project_path().parent / "files" / "departments.csv"
        }
        
        # Add Excel check if present
        for p in project_path().glob("Staff Details*.xlsx"):
            files["staff_excel"] = p
            break
        
        # Add Seed CSV check
        seed_p = project_path("StfData.csv")
        if seed_p.exists(): files["staff_seed"] = seed_p
        
        needs_sync = force or not state_path.exists()
        for key, path in files.items():
            if not path.exists(): continue
            mtime = os.path.getmtime(path)
            if state.get(key) != mtime:
                needs_sync = True
                state[key] = mtime
        
        if needs_sync:
            self.sync_units_from_csv()
            self.sync_staff_from_csv()
            self.sync_departments_from_csv()
            # Update state with current timestamps
            for key, path in files.items():
                if path.exists(): state[key] = os.path.getmtime(path)
            with open(state_path, "w") as f: json.dump(state, f)

    def update_unit_authorities(self, code: str, head_roll: str, second_roll: str, eff_date: str) -> bool:
        units = self.repo.get_by_category("UNIT")
        target = next((u for u in units if u.code == code), None)
        if not target: return False
        
        meta = target.metadata or {}
        meta["headUserId"] = head_roll
        meta["secondLineUserId"] = second_roll
        meta["authority_from"] = eff_date
        target.metadata = meta
        self.repo.save(target)
        return True
    def get_branch_manager(self, sol: str) -> dict:
        """Find the branch head (BH) for a given SOL with trilingual details."""
        staff = self.repo.get_by_category("STAFF")
        units = self.repo.get_by_category("UNIT")
        target_sol = str(sol).zfill(4)
        
        manager = None
        
        # Priority 1: Check UNIT Master metadata for explicitly assigned Unit Head
        unit = next((u for u in units if str(u.code).zfill(4) == target_sol), None)
        if unit:
            u_meta = unit.metadata or {}
            head_roll = u_meta.get("headUserId")
            if head_roll:
                manager = next((s for s in staff if str(s.code) == str(head_roll)), None)

        # Priority 2: Fallback to explicitly flagged staff in Registry (BH status)
        if not manager:
            for s in staff:
                meta = s.metadata or {}
                if str(meta.get("sol")).zfill(4) == target_sol and meta.get("status") == "BH":
                    manager = s
                    break
        
        # Priority 3: Fallback to highest grade staff whose designation contains "MANAGER"
        if not manager:
            branch_staff = [s for s in staff if str((s.metadata or {}).get("sol")).zfill(4) == target_sol]
            managerial_staff = [
                s for s in branch_staff 
                if "MANAGER" in str((s.metadata or {}).get("designation", "")).upper()
            ]
            
            if managerial_staff:
                managerial_staff.sort(key=lambda x: str((x.metadata or {}).get("grade", "")), reverse=True)
                manager = managerial_staff[0]
            elif branch_staff:
                branch_staff.sort(key=lambda x: str((x.metadata or {}).get("grade", "")), reverse=True)
                manager = branch_staff[0]
        
        if manager:
            meta = manager.metadata or {}
            gender = meta.get("gender", "M")
            sal = SalutationMapper.get_trilingual(gender)
            desig = meta.get("designation", "Branch Manager")
            tr_desig = DesignationMapper.get_trilingual(desig)
            
            return {
                "name": manager.name_en,
                "name_hi": manager.name_hi or manager.name_en,
                "name_ta": manager.name_local or manager.name_en,
                "sal_en": sal["en"],
                "sal_hi": sal["hi"],
                "sal_ta": sal["ta"],
                "designation": tr_desig["en"],
                "desig_en": tr_desig["en"],
                "desig_hi": tr_desig["hi"],
                "desig_ta": tr_desig["ta"],
                "grade": meta.get("grade"),
                "roll": manager.code
            }
        
        # Priority 4: Absolute Generic Fallback
        return {
            "name": "The Branch Manager",
            "name_hi": "शाखा प्रबंधक",
            "name_ta": "கிளை மேலாளர்",
            "sal_en": "The",
            "sal_hi": "माननीय",
            "sal_ta": "மதிப்பிற்குரிய",
            "designation": "Branch Manager",
            "desig_en": "Branch Manager",
            "desig_hi": "शाखा प्रबंधक",
            "desig_ta": "கிளை மேலாளர்",
            "grade": "N/A",
            "roll": "00000"
        }
