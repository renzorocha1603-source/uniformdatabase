import streamlit as st
import pandas as pd
import os
from datetime import datetime
from git import Repo

# --- COMPANY BRANDING & CONFIG ---
st.set_page_config(page_title="Indigo Uniforms Reimbursement Database", page_icon="👔", layout="centered")

# Custom UI styling tailored for Only Solutions Inc.
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 2px; }
    .subtitle { font-size: 13px; color: #6B7280; text-align: center; margin-bottom: 35px; letter-spacing: 0.5px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1E3A8A; }
    div[data-testid="stForm"] { border: 1px solid #E5E7EB; border-radius: 10px; padding: 25px; background-color: #FFFFFF; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Application Branding Headers
st.markdown('<div class="main-title">Indigo uniforms reimbursement database</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">created by only solutions inc.</div>', unsafe_allow_html=True)

EXCEL_FILE = "database.xlsx"

# --- SECURE ROSTER DATA (Usernames & Passwords) ---
EMPLOYEES = {
    "os_john": {"name": "John Doe", "id": "OS001", "type": "Full-Time", "limit": 175.00, "password": "solutions_john2026"},
    "os_jane": {"name": "Jane Smith", "id": "OS002", "type": "Part-Time", "limit": 100.00, "password": "solutions_jane2026"},
    "os_alex": {"name": "Alex Rivera", "id": "OS003", "type": "Full-Time", "limit": 175.00, "password": "solutions_alex2026"},
    "os_sam": {"name": "Sam Taylor", "id": "OS004", "type": "Part-Time", "limit": 100.00, "password": "solutions_sam2026"}
}

# --- DATABASE LOAD FUNCTIONS ---
def load_excel_data():
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE, sheet_name="receipts")
        except Exception:
            return pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])
    return pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])

def save_and_push_to_github(updated_df):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        updated_df.to_excel(writer, sheet_name="receipts", index=False)
    
    try:
        token = st.secrets["github"]["token"]
        repo_url = st.secrets["github"]["repo_url"]
        authenticated_url = repo_url.replace("https://", f"https://oauth2:{token}@")
        
        repo = Repo(".")
        try:
            origin = repo.remote(name="origin")
            origin.set_url(authenticated_url)
        except Exception:
            origin = repo.create_remote("origin", authenticated_url)
            
        repo.git.add(EXCEL_FILE)
        repo.index.commit("Automated database sheet synchronization [Only Solutions System]")
        origin.push("main")
        return True
    except Exception as e:
        st.error(f"GitHub Sync Error: {e}")
        return False

# Initialize session state tracking for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Load historical ledger
history_df = load_excel_data()

# --- STEP 1: AUTHENTICATION SCREEN ---
if not st.session_state["logged_in"]:
    st.write("### 🔒 System Authentication")
    with st.form("login_form"):
        username_input = st.text_input("Username:").strip().lower()
        password_input = st.text_input("Password:", type="password").strip()
        login_submit = st.form_submit_button("Access Portal")
        
        if login_submit:
            if username_input in EMPLOYEES and EMPLOYEES[username_input]["password"] == password_input:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_input
                st.success("Access Granted.")
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password. Please try again.")

# --- STEP 2: SECURED APPLICATION DASHBOARD ---
else:
    current_user = st.session_state["username"]
    emp_info = EMPLOYEES[current_user]
    emp_id = emp_info["id"]
    max_limit = emp_info["limit"]
    
    # Add a Log Out button in the sidebar
    if st.sidebar.button("🚪 Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()
        
    # Calculate spending balance logic
    if not history_df.empty:
        history_df["EmployeeID"] = history_df["EmployeeID"].astype(str).str.strip().str.upper()
        history_df["ReimbursedAmount"] = pd.to_numeric(history_df["ReimbursedAmount"], errors='coerce').fillna(0.0)
        emp_history = history_df[history_df["EmployeeID"] == emp_id]
        total_spent = emp_history["ReimbursedAmount"].sum()
    else:
        total_spent = 0.0
        
    remaining_credit = max_limit - total_spent
    
    # Profile display card
    st.markdown(f"""
    <div class="card">
        <h3>Welcome back, {emp_info['name']}</h3>
        <p><strong>Employee ID:</strong> {emp_id}</p>
        <p><strong>Employment Status:</strong> {emp_info['type']}</p>
        <p><strong>Annual Allocation Balance:</strong> ${max_limit:.2f}</p>
        <p><strong>Total Reimbursed YTD:</strong> ${total_spent:.2f}</p>
        <h4 style="color: {'#DC2626' if remaining_credit <= 0 else '#10B981'};">
            Available Credit Remaining: ${remaining_credit:.2f}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Claims management interface
    st.write("### 📝 Submit a New Receipt")
    with st.form("submission_form", clear_on_submit=True):
        store_name = st.text_input("Store Name:")
        receipt_amount = st.number_input("Receipt Total ($):", min_value=0.0, step=0.01, format="%.2f")
        uploaded_file = st.file_uploader("📷 Upload Image of Receipt", type=["png", "jpg", "jpeg"])
        
        submit_action = st.form_submit_button("Submit Claim")
        
        if submit_action:
            if receipt_amount <= 0:
                st.error("❌ Please declare a valid amount.")
            elif uploaded_file is None:
                st.error("❌ A digital image copy of the receipt is required.")
            elif remaining_credit <= 0:
                st.error(f"❌ Transaction blocked. Your individual balance limits are currently fully utilized.")
            else:
                # Allocation clamp validation threshold (burst control)
                if receipt_amount > remaining_credit:
                    reimbursed_amount = remaining_credit
                    st.warning(f"⚠️ Limit Warning: This receipt exceeds your coverage balance. "
                               f"OnlySolutions will automatically cap this reimbursement payout to: **${reimbursed_amount:.2f}**.")
                else:
                    reimbursed_amount = receipt_amount
                    st.success(f"✅ Claim Authorized! Approved reimbursement: **${reimbursed_amount:.2f}**.")
                
                # Format submission data array
                new_entry = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "EmployeeID": emp_id,
                    "Name": emp_info["name"],
                    "Type": emp_info["type"],
                    "Store": store_name,
                    "ReceiptAmount": receipt_amount,
                    "ReimbursedAmount": reimbursed_amount
                }])
                
                updated_df = pd.concat([history_df, new_entry], ignore_index=True)
                
                with st.spinner("Synchronizing secure database with repository..."):
                    success = save_and_push_to_github(updated_df)
                    if success:
                        st.toast("Excel repository database synced!", icon="💾")
                        st.rerun()
                        
    # History section populated directly from local cache sync
    st.write("### 📜 Your Submission Logs")
    if not history_df.empty:
        emp_logs = history_df[history_df["EmployeeID"] == emp_id]
        if not emp_logs.empty:
            st.dataframe(emp_logs[["Timestamp", "Store", "ReceiptAmount", "ReimbursedAmount"]], use_container_width=True)
        else:
            st.info("No recorded logs found under your account profile for this cycle.")
    else:
        st.info("No recorded logs found under your account profile for this cycle.")
