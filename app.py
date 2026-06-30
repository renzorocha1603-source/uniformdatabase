import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from git import Repo

# --- COMPANY BRANDING & CONFIG ---
st.set_page_config(page_title="Indigo Uniforms Reimbursement Database", page_icon="👔", layout="centered")

# Custom UI styling tailored for Indigo Brand Identity
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 2px; }
    .subtitle { font-size: 13px; color: #6B7280; text-align: center; margin-bottom: 35px; letter-spacing: 0.5px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1E3A8A; }
    div[data-testid="stForm"] { border: 1px solid #E5E7EB; border-radius: 10px; padding: 25px; background-color: #FFFFFF; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Mandatory Interface Headers
st.markdown('<div class="main-title">Indigo uniforms reimbursement database</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">created by only solutions inc.</div>', unsafe_allow_html=True)

EXCEL_FILE = "database.xlsx"

# --- SYSTEM INITIALIZATION & DATABASE LAYER ---
def load_database():
    """Initializes and reads the multi-sheet Excel tracking matrix."""
    if os.path.exists(EXCEL_FILE):
        try:
            receipts_df = pd.read_excel(EXCEL_FILE, sheet_name="receipts")
        except Exception:
            receipts_df = pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])
        
        try:
            users_df = pd.read_excel(EXCEL_FILE, sheet_name="users")
        except Exception:
            users_df = pd.DataFrame(columns=["Username", "Password", "Name", "EmployeeID", "Type", "Limit"])
    else:
        receipts_df = pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])
        users_df = pd.DataFrame(columns=["Username", "Password", "Name", "EmployeeID", "Type", "Limit"])
        
    return receipts_df, users_df

def save_and_push_to_github(receipts_df, users_df):
    """Commits database changes and executes an automated upstream repository sync."""
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        receipts_df.to_excel(writer, sheet_name="receipts", index=False)
        users_df.to_excel(writer, sheet_name="users", index=False)
    
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
        repo.index.commit("Automated secure database update [Only Solutions System]")
        origin.push("main")
        return True
    except Exception as e:
        st.error(f"GitHub Repository Write Error: {e}")
        return False

# --- FINANCE EMAIL SYSTEM ---
def send_finance_email(user_info, store, amount, approved, uploaded_file):
    """Routes comprehensive breakdown files directly to the core finance email target."""
    try:
        cfg = st.secrets["email"]
        
        # Structure payload package
        msg = MIMEMultipart()
        msg['From'] = cfg["sender_email"]
        msg['To'] = cfg["finance_email"]
        msg['Subject'] = f"New Uniform Reimbursement Claim - {user_info['Name']} ({user_info['EmployeeID']})"
        
        body = f"""
        Hello Finance Team,
        
        A new uniform reimbursement claim has been logged in the system.
        
        Employee Details:
        - Name: {user_info['Name']}
        - Employee ID: {user_info['EmployeeID']}
        - Profile Status: {user_info['Type']}
        
        Transaction Breakdown:
        - Store/Merchant: {store}
        - Total Receipt Amount: ${amount:.2f}
        - Maximum Approved System Reimbursement: ${approved:.2f}
        - Date Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        The verified receipt image is attached to this transmission message.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Process attachment image asset conversion
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(uploaded_file.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{uploaded_file.name}"')
        msg.attach(part)
        
        # Dispatch session execution
        server = smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"])
        server.starttls()
        server.login(cfg["sender_email"], cfg["sender_password"])
        server.sendmail(cfg["sender_email"], cfg["finance_email"], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Finance Email Dispatch Warning: {e}")
        return False

# Load current session storage state
receipts_df, users_df = load_database()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""

# --- PHASE 1: AUTHENTICATION ROUTING SCREEN ---
if not st.session_state["logged_in"]:
    st.write("### 🔒 System Portal Authentication")
    with st.form("login_form"):
        username_input = st.text_input("Portal Username:").strip().lower()
        password_input = st.text_input("Secure Password:", type="password").strip()
        login_submit = st.form_submit_button("Access Portal Account")
        
        if login_submit:
            # Check master administrative bypass rule
            if username_input == "admin" and password_input == "12345":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "admin"
                st.session_state["username"] = "admin"
                st.rerun()
            # Dynamic lookup for employee records via users data sheet
            elif not users_df.empty and username_input in users_df["Username"].values:
                user_record = users_df[users_df["Username"] == username_input].iloc[0]
                if str(user_record["Password"]) == password_input:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "employee"
                    st.session_state["username"] = username_input
                    st.rerun()
                else:
                    st.error("❌ Invalid password validation provided.")
            else:
                st.error("❌ Credentials unrecognized by system core registries.")

# --- PHASE 2: ADMIN MANAGEMENT INTERFACE ---
elif st.session_state["user_role"] == "admin":
    st.sidebar.title("Admin Workspace")
    if st.sidebar.button("🚪 Log Out of System"):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = ""
        st.session_state["username"] = ""
        st.rerun()
        
    st.write("### 🛠️ Administrative Control Console")
    
    with st.form("create_user_form", clear_on_submit=True):
        st.write("#### Create/Register New Staff Profile")
        new_user = st.text_input("Assigned Username (lowercase, no spaces):").strip().lower()
        new_pass = st.text_input("Temporary Profile Password:").strip()
        new_name = st.text_input("Full Employee Name:").strip()
        new_id = st.text_input("Unique Employee ID (e.g., OS005):").strip().upper()
        new_type = st.selectbox("Employment Designation:", ["Part-Time", "Full-Time"])
        
        create_btn = st.form_submit_button("Register & Save Profile")
        
        if create_btn:
            if not (new_user and new_pass and new_name and new_id):
                st.error("❌ All registration payload parameter fields must be structurally satisfied.")
            elif not users_df.empty and new_user in users_df["Username"].values:
                st.error("❌ Account profile username conflict encountered.")
            else:
                limit_allocation = 175.00 if new_type == "Full-Time" else 100.00
                new_profile = pd.DataFrame([{
                    "Username": new_user,
                    "Password": new_pass,
                    "Name": new_name,
                    "EmployeeID": new_id,
                    "Type": new_type,
                    "Limit": limit_allocation
                }])
                
                users_df = pd.concat([users_df, new_profile], ignore_index=True)
                with st.spinner("Writing metadata schemas directly to files..."):
                    if save_and_push_to_github(receipts_df, users_df):
                        st.success(f"✅ Secure account profile successfully mapped for {new_name}!")
                        st.rerun()

    st.write("#### Active Registered Staff Roster")
    if not users_df.empty:
        st.dataframe(users_df[["EmployeeID", "Name", "Type", "Limit", "Username"]], use_container_width=True)
    else:
        st.info("No active employee registries loaded in database sheets.")

# --- PHASE 3: EMPLOYEE REIMBURSEMENT PORTAL ---
else:
    user_record = users_df[users_df["Username"] == st.session_state["username"]].iloc[0]
    emp_id = user_record["EmployeeID"]
    max_limit = float(user_record["Limit"])
    
    if st.sidebar.button("🚪 System Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = ""
        st.session_state["username"] = ""
        st.rerun()
        
    # Calculate operational metrics allocations
    if not receipts_df.empty:
        receipts_df["EmployeeID"] = receipts_df["EmployeeID"].astype(str).str.strip().str.upper()
        receipts_df["ReimbursedAmount"] = pd.to_numeric(receipts_df["ReimbursedAmount"], errors='coerce').fillna(0.0)
        emp_history = receipts_df[receipts_df["EmployeeID"] == emp_id]
        total_spent = emp_history["ReimbursedAmount"].sum()
    else:
        total_spent = 0.0
        
    remaining_credit = max_limit - total_spent
    
    st.markdown(f"""
    <div class="card">
        <h3>Welcome back, {user_record['Name']}</h3>
        <p><strong>Employee Identifier Code:</strong> {emp_id}</p>
        <p><strong>Designated Status Assignment:</strong> {user_record['Type']}</p>
        <p><strong>Annual Uniform Allocation limit:</strong> ${max_limit:.2f}</p>
        <p><strong>Total Reimbursed to Date:</strong> ${total_spent:.2f}</p>
        <h4 style="color: {'#DC2626' if remaining_credit <= 0 else '#10B981'};">
            Available Credit Balance Remaining: ${remaining_credit:.2f}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### 📝 Apply for a Reimbursement")
    with st.form("claim_submission", clear_on_submit=True):
        store_name = st.text_input("Store Name / Merchant:")
        receipt_amount = st.number_input("Receipt Grand Total ($):", min_value=0.0, step=0.01, format="%.2f")
        uploaded_file = st.file_uploader("📷 Upload Image Copy of Receipt", type=["png", "jpg", "jpeg"])
        
        submit_claim = st.form_submit_button("Submit Reimbursement Request")
        
        if submit_claim:
            if receipt_amount <= 0:
                st.error("❌ Claim registration error: Invalid numeric calculation payload.")
            elif uploaded_file is None:
                st.error("❌ Verification asset failure: Receipt image attachment is strictly mandatory.")
            elif remaining_credit <= 0:
                st.error("❌ Allocation Limit Overflow: Your global calendar limit parameters are entirely fully utilized.")
            else:
                # Allocation clamp tracking calculations ("Burst" optimization verification rules)
                if receipt_amount > remaining_credit:
                    reimbursed_amount = remaining_credit
                    st.warning(f"⚠️ Allocation Cap Notification: This submission balancing parameters cross over your coverage. "
                               f"The system automatically scaled down approved disbursement execution payload to: **${reimbursed_amount:.2f}**.")
                else:
                    reimbursed_amount = receipt_amount
                    st.success(f"✅ Reimbursement validation request initialized. System approved amount: **${reimbursed_amount:.2f}**.")
                
                # Append log index structure
                new_receipt = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "EmployeeID": emp_id,
                    "Name": user_record["Name"],
                    "Type": user_record["Type"],
                    "Store": store_name,
                    "ReceiptAmount": receipt_amount,
                    "ReimbursedAmount": reimbursed_amount
                }])
                
                receipts_df = pd.concat([receipts_df, new_receipt], ignore_index=True)
                
                with st.spinner("Processing dispatch notification logs for Finance validation..."):
                    # Step A: Route transaction documents straight to corporate emails matrix
                    email_success = send_finance_email(user_record, store_name, receipt_amount, reimbursed_amount, uploaded_file)
                    
                    # Step B: Record structural ledger alterations to permanent repository sheet storage
                    db_success = save_and_push_to_github(receipts_df, users_df)
                    
                    if db_success:
                        st.toast("System synchronized successfully!", icon="💾")
                        st.rerun()

    st.write("### 📜 Your Submission Ledger History")
    if not receipts_df.empty:
        personal_logs = receipts_df[receipts_df["EmployeeID"] == emp_id]
        if not personal_logs.empty:
            st.dataframe(personal_logs[["Timestamp", "Store", "ReceiptAmount", "ReimbursedAmount"]], use_container_width=True)
        else:
            st.info("No recorded transactions linked to this profile index.")
    else:
        st.info("No recorded transactions linked to this profile index.")
