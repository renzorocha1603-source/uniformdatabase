import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- COMPANY BRANDING & CONFIG ---
st.set_page_config(page_title="OnlySolutions - Uniform Credit Tracker", page_icon="👔", layout="centered")

# Custom UI styling for OnlySolutions
st.markdown("""
    <style>
    .main-title { font-size: 34px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 18px; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">OnlySolutions</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Employee Uniform Credit Portal</div>', unsafe_allow_html=True)

# --- REPOSITORIES OF EMPLOYEES ---
# Defined business allowance architecture
EMPLOYEES = {
    "OS001": {"name": "John Doe", "type": "Full-Time", "limit": 175.00},
    "OS002": {"name": "Jane Smith", "type": "Part-Time", "limit": 100.00},
    "OS003": {"name": "Alex Rivera", "type": "Full-Time", "limit": 175.00},
    "OS004": {"name": "Sam Taylor", "type": "Part-Time", "limit": 100.00}
}

# --- DATABASE CONNECTION ---
# Establish connection with the configured Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def load_historical_data():
    try:
        df = conn.read(worksheet="receipts", ttl="0m")
        # Ensure correct formatting if sheet is completely empty except headers
        if df.empty:
            return pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount", "ReceiptLink"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount", "ReceiptLink"])

# Read latest state from Google Sheets
history_df = load_historical_data()

# --- APP INTERFACE AND LOGIC ---
emp_id = st.text_input("🔑 Enter your OnlySolutions Employee ID:", key="emp_id_entry").strip().upper()

if emp_id:
    if emp_id in EMPLOYEES:
        emp_info = EMPLOYEES[emp_id]
        max_limit = emp_info["limit"]
        
        # Calculate dynamic expenditures based on real-time sheet logs
        if not history_df.empty:
            # Clean data types to avoid calculation mismatches
            history_df["EmployeeID"] = history_df["EmployeeID"].astype(str).str.strip().str.upper()
            history_df["ReimbursedAmount"] = pd.to_numeric(history_df["ReimbursedAmount"], errors='coerce').fillna(0.0)
            
            emp_history = history_df[history_df["EmployeeID"] == emp_id]
            total_spent = emp_history["ReimbursedAmount"].sum()
        else:
            total_spent = 0.0
            
        remaining_credit = max_limit - total_spent
        
        # Render clean dashboard card
        st.markdown(f"""
        <div class="card">
            <h3>Welcome, {emp_info['name']}</h3>
            <p><strong>Employment Designation:</strong> {emp_info['type']}</p>
            <p><strong>Annual Uniform Allocation:</strong> ${max_limit:.2f}</p>
            <p><strong>Total Processed Reimbursements:</strong> ${total_spent:.2f}</p>
            <h4 style="color: {'#DC2626' if remaining_credit <= 0 else '#10B981'};">
                Available Credit Balance: ${remaining_credit:.2f}
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Form interface for claims submissions
        st.write("### 📝 Submit a New Receipt")
        with st.form("submission_form", clear_on_submit=True):
            store_name = st.text_input("Merchant/Store Name:")
            receipt_amount = st.number_input("Receipt Total ($):", min_value=0.0, step=0.01, format="%.2f")
            uploaded_file = st.file_uploader("📷 Upload Image of Receipt", type=["png", "jpg", "jpeg"])
            
            submit_action = st.form_submit_button("Submit Claim")
            
            if submit_action:
                if receipt_amount <= 0:
                    st.error("❌ Please declare a valid receipt total amount.")
                elif uploaded_file is None:
                    st.error("❌ A digital copy or picture of the receipt is required.")
                elif remaining_credit <= 0:
                    st.error(f"❌ Transaction blocked. Your annual credit allowance (${max_limit:.2f}) has been entirely utilized.")
                else:
                    # Validate allocation threshold ("burst" control framework)
                    if receipt_amount > remaining_credit:
                        reimbursed_amount = remaining_credit
                        st.warning(f"⚠️ Limit Warning: This receipt execution balances above your coverage limit. "
                                   f"OnlySolutions will automatically cap this reimbursement to your remaining balance: **${reimbursed_amount:.2f}**.")
                    else:
                        reimbursed_amount = receipt_amount
                        st.success(f"✅ Claim authorized. Approved reimbursement payload: **${reimbursed_amount:.2f}**.")
                    
                    # Construct structural data record payload
                    new_entry = pd.DataFrame([{
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "EmployeeID": emp_id,
                        "Name": emp_info["name"],
                        "Type": emp_info["type"],
                        "Store": store_name,
                        "ReceiptAmount": receipt_amount,
                        "ReimbursedAmount": reimbursed_amount,
                        "ReceiptLink": f"Uploaded File: {uploaded_file.name}"  # Reference placeholder
                    }])
                    
                    # Concatenate with active memory frame and write directly to Google Sheets database
                    updated_df = pd.concat([history_df, new_entry], ignore_index=True)
                    conn.update(worksheet="receipts", data=updated_df)
                    
                    st.toast("Database updated successfully!", icon="💾")
                    st.rerun()
                    
        # History section populated directly from sheet
        st.write("### 📜 Your Submission Logs")
        if not history_df.empty:
            emp_logs = history_df[history_df["EmployeeID"] == emp_id]
            if not emp_logs.empty:
                st.dataframe(emp_logs[["Timestamp", "Store", "ReceiptAmount", "ReimbursedAmount"]], use_container_width=True)
            else:
                st.info("No logs registered for your Employee ID under the current calendar cycle.")
        else:
            st.info("No logs registered for your Employee ID under the current calendar cycle.")
            
    else:
        st.error("❌ Security Warning: Provided Employee ID is not authenticated under the OnlySolutions registry.")
