from __future__ import annotations
import streamlit as st
from io import BytesIO
from PIL import Image
from src.interface.streamlit.components.primitives import render_action_bar
from src.interface.streamlit.state.services import get_doc_service_v4, get_master_service
from src.application.services.translation_service import DesignationMapper

def render() -> None:
    render_action_bar("Visiting Card Wizard", ["Design", "Preview", "Bulk Export"])
    
    doc_service = get_doc_service_v4()
    master_svc = get_master_service()
    
    st.markdown("### Create Your Institutional Visiting Card")
    st.caption("Generate professional, trilingual visiting cards with automatic front and back side rendering.")
    
    # Step 1: Data Intake
    with st.expander("Step 1: Staff Details", expanded=True):
        mode = st.radio("Intake Mode", ["Search Master", "Manual Entry"], horizontal=True)
        
        staff_data_list = []
        
        if mode == "Search Master":
            staff_list = master_svc.get_by_category("STAFF")
            selected_staffs = st.multiselect(
                "Select Staff Member(s)",
                staff_list,
                format_func=lambda s: f"{s.name_en} ({s.code}) - {s.metadata.get('designation', '') if s.metadata else ''}"
            )
            
            for s in selected_staffs:
                trans = DesignationMapper.get_trilingual(s.metadata.get("designation", "") if s.metadata else "")
                staff_data_list.append({
                    "name_en": s.name_en,
                    "name_hi": s.name_hi or s.name_en,
                    "name_ta": s.name_local or s.name_en,
                    "designation_en": s.metadata.get("designation", "") if s.metadata else "",
                    "designation_hi": trans.get("hi", ""),
                    "designation_ta": trans.get("ta", ""),
                    "mobile": s.metadata.get("mobile", "") if s.metadata else "",
                    "email": s.metadata.get("email", "") if s.metadata else "",
                    "phone": "0451-2420000", # Default for RO
                    "web": "www.iob.in"
                })
        else:
            data = {}
            col1, col2 = st.columns(2)
            data["name_en"] = col1.text_input("Name (English)", "RAJEEV KUMAR")
            data["name_hi"] = col2.text_input("Name (Hindi)", "राजीव कुमार")
            data["name_ta"] = st.text_input("Name (Tamil)", "ராஜீவ் குமார்")
            
            col3, col4, col5 = st.columns(3)
            data["designation_en"] = col3.text_input("Designation (En)", "Manager")
            data["designation_hi"] = col4.text_input("Designation (Hi)", "प्रबंधक")
            data["designation_ta"] = col5.text_input("Designation (Ta)", "மேலாளர்")
            
            col6, col7 = st.columns(2)
            data["mobile"] = col6.text_input("Mobile", "+91 99999 99999")
            data["email"] = col7.text_input("Email", "staff@iob.in")
            
            data["phone"] = st.text_input("Office Phone", "0451-2420000")
            data["web"] = st.text_input("Website", "www.iob.in")
            
            staff_data_list.append(data)
            
        # Common address fields for all selected
        st.markdown("---")
        st.caption("Common Office Address")
        
        # Try to infer address from the first selected staff's unit
        default_addr_en = "Regional Office, Dindigul\nNo. 17-i, First Floor, Pensioner Street, Palani Road, Dindigul - 624001"
        default_addr_hi = "क्षेत्रीय कार्यालय, डिंडीगुल\n#17-i, पहली मंज़िल, पेंशनर स्ट्रीट, पलनी रोड, दिण्डुक्कल - 624001"
        default_addr_ta = "மண்டல அலுவலகம், திண்டுக்கல்\n#17-i, முதல் தளம், பென்ஷனர் வீதி, பழனி ரோடு, திண்டுக்கல் - 624001"

        if selected_staffs:
            sol = selected_staffs[0].metadata.get("sol")
            unit = next((u for u in master_svc.get_by_category("UNIT") if u.code == sol), None)
            if unit:
                u_meta = unit.metadata or {}
                addr1 = u_meta.get("address1", "")
                addr2 = u_meta.get("address2", "")
                dist = u_meta.get("district", "")
                pin = u_meta.get("pincode", "")
                
                # If we have granular data, use it
                if addr1 or addr2:
                    parts = [p for p in [addr1, addr2, dist, pin] if p]
                    default_addr_en = f"{unit.name_en}\n" + ", ".join(parts)
        
        addr_col1, addr_col2 = st.columns(2)
        common_addr_en = addr_col1.text_area("Address (English)", default_addr_en)
        common_addr_hi = addr_col2.text_area("Address (Hindi)", default_addr_hi)
        common_addr_ta = st.text_area("Address (Tamil)", default_addr_ta)

        for d in staff_data_list:
            d["address_en"] = common_addr_en
            d["address_hi"] = common_addr_hi
            d["address_ta"] = common_addr_ta

    # Step 2: Generation
    if st.button("Generate Cards", use_container_width=True, type="primary"):
        if not staff_data_list:
            st.warning("Please select at least one staff member.")
        else:
            all_pages = []
            with st.spinner(f"Rendering {len(staff_data_list)} Card(s)..."):
                for d in staff_data_list:
                    pages = doc_service.generate_visiting_card_image(d)
                    all_pages.extend(pages)
                st.session_state["vc_bulk_pages"] = all_pages
                st.session_state["vc_staff_count"] = len(staff_data_list)
            
    # Step 3: Display & Download
    if "vc_bulk_pages" in st.session_state:
        pages = st.session_state["vc_bulk_pages"]
        count = st.session_state["vc_staff_count"]
        
        st.markdown(f"### Preview ({count} Card(s) Generated)")
        
        # Show first card preview (Front & Back)
        if len(pages) >= 2:
            col_p1, col_p2 = st.columns(2)
            col_p1.image(pages[0], caption="Front Side (Trilingual)", use_container_width=True)
            col_p2.image(pages[1], caption="Back Side (Tamil)", use_container_width=True)
        
        st.markdown("---")
        col_dl1, col_dl2 = st.columns(2)
        
        # PNG Download (Zip or just first one)
        col_dl1.download_button(
            "Download First Card (PNG)",
            data=pages[0],
            file_name="VisitingCard_Front.png",
            mime="image/png",
            use_container_width=True
        )
        
        # PDF Generation (Multi-page)
        pdf_buf = BytesIO()
        pil_images = [Image.open(BytesIO(p)).convert("RGB") for p in pages]
        if pil_images:
            pil_images[0].save(
                pdf_buf, 
                format="PDF", 
                save_all=True, 
                append_images=pil_images[1:], 
                resolution=600.0
            )
            
            col_dl2.download_button(
                f"Download {count} Card(s) (PDF - {len(pages)} Pages)",
                data=pdf_buf.getvalue(),
                file_name="VisitingCards_Bulk.pdf",
                mime="application/pdf",
                use_container_width=True
            )
