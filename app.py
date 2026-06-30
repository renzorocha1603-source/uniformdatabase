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

# Visual Branding Setup (Tailored Interface styling)
st.markdown("""
    <style>
    .header-container { display: flex; align-items: center; justify-content: space-between; padding-bottom: 20px; border-bottom: 1px solid #E5E7EB; margin-bottom: 25px; }
    .logo-img { max-height: 50px; width: auto; }
    .main-title { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 2px; }
    .subtitle { font-size: 13px; color: #6B7280; margin-bottom: 0px; letter-spacing: 0.5px; }
    .title-box { flex-grow: 1; text-align: left; margin-left: 20px; }
    .lang-box { text-align: right; min-width: 120px; }
    
    /* Input Form and Card Styling */
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1E3A8A; }
    div[data-testid="stForm"] { border: 1px solid #E5E7EB; border-radius: 10px; padding: 25px; background-color: #FFFFFF; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Define official Indigo logo URL provided via ImgBB
LOGO_URL = "https://i.ibb.co/mVRXHXpx/indigo-park-canada-logo.jpg"

# Initialize language session state parameter
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

# --- RENDER TOP HEADER BLOCK (Logo + Title + Language Switcher) ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# 1. Render Official Logo Asset
col_logo, col_titles, col_lang = st.columns([1, 4, 1.5])
with col_logo:
    st.image(LOGO_URL, use_container_width=True)

# 2. Definition of Bilingual Translation Dictionaries
TXT = {
    "English": {
        "title": "Indigo uniforms reimbursement database",
        "created_by": "created by only solutions inc.",
        "auth": "🔒 System Portal Authentication",
        "username": "Portal Username:",
        "password": "Secure Password:",
        "login_btn": "Access Portal Account",
        "invalid_pass": "❌ Invalid password validation provided.",
        "invalid_user": "❌ Credentials unrecognized by system core registries.",
        "logout": "🚪 Log Out",
        "admin_title": "🛠️ Administrative Control Console",
        "create_title": "Create/Register New Staff Profile",
        "form_user": "Assigned Username (lowercase, no spaces):",
        "form_pass": "Temporary Password:",
        "form_name": "Full Employee Name:",
        "form_id": "Unique Employee ID (e.g., OS005):",
        "form_type": "Employment Designation:",
        "pt": "Part-Time", "ft": "Full-Time",
        "save_btn": "Register & Save Profile",
        "err_fields": "❌ All form payload parameters must be functionally satisfied.",
        "err_conflict": "❌ Account profile username conflict encountered.",
        "success_reg": "✅ Secure profile successfully mapped for",
        "roster": "Active Registered Staff Roster",
        "welcome": "Welcome back",
        "emp_code": "Employee Identifier Code:",
        "status_assign": "Designated Status Assignment:",
        "ann_limit": "Annual Uniform Allocation limit:",
        "tot_reimb": "Total Reimbursed to Date:",
        "avail_credit": "Available Credit Balance Remaining:",
        "sub_title": "📝 Apply for a Reimbursement",
        "store": "Store Name / Merchant:",
        "total_rec": "Receipt Grand Total ($):",
        "upload_img": "📷 Upload Image Copy of Receipt",
        "sub_btn": "Submit Reimbursement Request",
        "err_amt": "❌ Claim validation error: Invalid numeric payload.",
        "err_file": "❌ Verification asset failure: Receipt image attachment is strictly mandatory.",
        "err_maxed": "❌ Allocation Limit Overflow: Individual limits are fully utilized.",
        "warn_clamp": "⚠️ Limit Adjustment: This receipt cross over your coverage. System scaled down approved reimbursement execution payload to:",
        "success_claim": "✅ Reimbursement request initialized. System approved amount:",
        "ledger_title": "### 📜 Your Submission Ledger History",
        "no_logs": "No recorded transactions linked to this profile index.",
        "syncing": "Processing dispatch notification logs for Finance validation...",
        "email_subject": "New Uniform Reimbursement Claim"
    },
    "Français": {
        "title": "Base de données de remboursement des uniformes Indigo",
        "created_by": "créé par only solutions inc.",
        "auth": "🔒 Authentification au portail système",
        "username": "Nom d'utilisateur :",
        "password": "Mot de passe sécurisé :",
        "login_btn": "Accéder au compte du portail",
        "invalid_pass": "❌ Validation du mot de passe fournie non valide.",
        "invalid_user": "❌ Identifiants non reconnus par les registres du système.",
        "logout": "🚪 Se déconnecter",
        "admin_title": "🛠️ Console de contrôle administratif",
        "create_title": "Créer/Enregistrer un nouveau profil d'employé",
        "form_user": "Nom d'utilisateur assigné (minuscules, sans espace) :",
        "form_pass": "Mot de passe temporaire :",
        "form_name": "Nom complet de l'employé :",
        "form_id": "Identifiant d'employé unique (ex: OS005) :",
        "form_type": "Désignation de l'emploi :",
        "pt": "Temps partiel", "ft": "Temps plein",
        "save_btn": "Enregistrer et sauvegarder le profil",
        "err_fields": "❌ Tous les champs du formulaire doivent être remplis.",
        "err_conflict": "❌ Conflit de nom d'utilisateur rencontré.",
        "success_reg": "✅ Profil de compte sécurisé configuré avec succès pour",
        "roster": "Roster du personnel actif enregistré",
        "welcome": "Bon retour",
        "emp_code": "Code d'identification de l'employé :",
        "status_assign": "Statut d'emploi assigné :",
        "ann_limit": "Limite d'allocation annuelle pour uniforme :",
        "tot_reimb": "Total remboursé à ce jour :",
        "avail_credit": "Solde de crédit disponible restant :",
        "sub_title": "📝 Demander un remboursement",
        "store": "Nom du magasin / Marchand :",
        "total_rec": "Montant total du reçu ($) :",
        "upload_img": "📷 Téléverser une photo du reçu",
        "sub_btn": "Soumettre la demande de remboursement",
        "err_amt": "❌ Erreur d'enregistrement : Le montant saisi n'est pas valide.",
        "err_file": "❌ Échec de vérification : La photo du reçu est strictement obligatoire.",
        "err_maxed": "❌ Limite atteinte : Vos paramètres de limite annuelle sont entièrement utilisés.",
        "warn_clamp": "⚠️ Avis de plafonnement : Cette soumission dépasse votre couverture. Le système a automatiquement réduit le montant approuvé à :",
        "success_claim": "✅ Demande de remboursement initialisée. Montant approuvé par le système :",
        "ledger_title": "### 📜 Historique de vos soumissions",
        "no_logs": "Aucune transaction enregistrée liée à ce profil.",
        "syncing": "Traitement des journaux de notification pour validation par les Finances...",
        "email_subject": "Nouvelle demande de remboursement d'uniforme"
    }
}

# 3. Render Dynamic Titles based on active selection
with col_titles:
    st.markdown(f'<div class="main-title">{TXT[st.session_state["lang"]]["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{TXT[st.session_state["lang"]]["created_by"]}</div>', unsafe_allow_html=True)

# 4. Render Language Toggle switch in top-right corner
with col_lang:
    lang_toggle = st.radio("🌐", ["Français", "English"], index=0 if st.session_state["lang"] == "Français" else 1, horizontal=True, label_visibility="collapsed")
    if lang_toggle != st.session_state["lang"]:
        st.session_state["lang"] = lang_toggle
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # End of Header container block

# --- SYSTEM INITIALIZATION & DATABASE LAYER ---
EXCEL_FILE = "database.xlsx"

def load_database():
    """Reads structural matrix from multi-sheet Excel repository ledger."""
    if os.path.exists(EXCEL_FILE):
        try: receipts_df = pd.read_excel(EXCEL_FILE, sheet_name="receipts")
        except: receipts_df = pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])
        try: users_df = pd.read_excel(EXCEL_FILE, sheet_name="users")
        except: users_df = pd.DataFrame(columns=["Username", "Password", "Name", "EmployeeID", "Type", "Limit"])
    else:
        receipts_df = pd.DataFrame(columns=["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount"])
        users_df = pd.DataFrame(columns=["Username", "Password", "Name", "EmployeeID", "Type", "Limit"])
    return receipts_df, users_df

def save_and_push_to_github(receipts_df, users_df):
    """Commits database alterations and executes upstream repository push."""
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        receipts_df.to_excel(writer, sheet_name="receipts", index=False)
        users_df.to_excel(writer, sheet_name="users", index=False)
    try:
        token = st.secrets["github"]["token"]
        repo_url = st.secrets["github"]["repo_url"]
        authenticated_url = repo_url.replace("https://", f"https://oauth2:{token}@")
        repo = Repo(".")
        try: origin = repo.remote(name="origin"); origin.set_url(authenticated_url)
        except: origin = repo.create_remote("origin", authenticated_url)
        repo.git.add(EXCEL_FILE)
        repo.index.commit("Automated secure database ledger sync [Only Solutions System]")
        origin.push("main")
        return True
    except Exception as e:
        st.error(f"GitHub Repository Write Failure: {e}")
        return False

# --- FINANCE EMAIL DISPATCH SYSTEM ---
def send_finance_email(user_info, store, amount, approved, uploaded_file, active_txt):
    """Routes comprehensive breakdown assets directly to finance team inbox target."""
    try:
        cfg = st.secrets["email"]
        msg = MIMEMultipart()
        msg['From'] = cfg["sender_email"]
        msg['To'] = cfg["finance_email"]
        msg['Subject'] = f"{active_txt['email_subject']} - {user_info['Name']} ({user_info['EmployeeID']})"
        
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
        
        # Convert uploaded file asset to attachable payload package
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(uploaded_file.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{uploaded_file.name}"')
        msg.attach(part)
        
        # Dispatch automation execution
        server = smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"])
        server.starttls()
        server.login(cfg["sender_email"], cfg["sender_password"])
        server.sendmail(cfg["sender_email"], cfg["finance_email"], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Finance Email Dispatch Warning: {e}")
        return False

# Load current session datasets
receipts_df, users_df = load_database()
active_txt = TXT[st.session_state["lang"]] # Lock in active translation dictionary

# Initialize user tracking parameters
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = ""
if "username" not in st.session_state: st.session_state["username"] = ""

# --- PHASE 1: AUTHENTICATION ROUTING SCREEN ---
if not st.session_state["logged_in"]:
    st.write(f"### {active_txt['auth']}")
    with st.form("login_form"):
        username_input = st.text_input(active_txt["username"]).strip().lower()
        password_input = st.text_input(active_txt["password"], type="password").strip()
        login_submit = st.form_submit_button(active_txt["login_btn"])
        
        if login_submit:
            # Check master administrative bypass rule matrix
            if username_input == "admin" and password_input == "12345":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "admin"
                st.session_state["username"] = "admin"
                st.rerun()
            # Dynamic lookup for employee record schemas via users datasheet
            elif not users_df.empty and username_input in users_df["Username"].values:
                user_record = users_df[users_df["Username"] == username_input].iloc[0]
                if str(user_record["Password"]) == password_input:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "employee"
                    st.session_state["username"] = username_input
                    st.rerun()
                else: st.error(active_txt["invalid_pass"])
            else: st.error(active_txt["invalid_user"])

# --- PHASE 2: ADMIN MANAGEMENT INTERFACE ---
elif st.session_state["user_role"] == "admin":
    st.sidebar.title("Admin")
    if st.sidebar.button(active_txt["logout"]):
        st.session_state["logged_in"] = False; st.session_state["user_role"] = ""; st.session_state["username"] = ""
        st.rerun()
        
    st.write(f"### {active_txt['admin_title']}")
    
    with st.form("create_user_form", clear_on_submit=True):
        st.write(f"#### {active_txt['create_title']}")
        new_user = st.text_input(active_txt["form_user"]).strip().lower()
        new_pass = st.text_input(active_txt["form_pass"]).strip()
        new_name = st.text_input(active_txt["form_name"]).strip()
        new_id = st.text_input(active_txt["form_id"]).strip().upper()
        
        # Process bilingual status selection conversion rules
        type_options = [active_txt["ft"], active_txt["pt"]]
        new_type_sel = st.selectbox(active_txt["form_type"], type_options)
        
        create_btn = st.form_submit_button(active_txt["save_btn"])
        
        if create_btn:
            if not (new_user and new_pass and new_name and new_id):
                st.error(active_txt["err_fields"])
            elif not users_df.empty and new_user in users_df["Username"].values:
                st.error(active_txt["err_conflict"])
            else:
                # Clamp raw data into standardized DB strings
                db_type_string = "Full-Time" if new_type_sel == active_txt["ft"] else "Part-Time"
                limit_allocation = 175.00 if db_type_string == "Full-Time" else 100.00
                new_profile = pd.DataFrame([{
                    "Username": new_user, "Password": new_pass, "Name": new_name,
                    "EmployeeID": new_id, "Type": db_type_string, "Limit": limit_allocation
                }])
                users_df = pd.concat([users_df, new_profile], ignore_index=True)
                with st.spinner("Writing structural schemas directly to Excel ledger..."):
                    if save_and_push_to_github(receipts_df, users_df):
                        st.success(f"{active_txt['success_reg']} {new_name}!")
                        st.rerun()

    st.write(f"#### {active_txt['roster']}")
    if not users_df.empty:
        st.dataframe(users_df[["EmployeeID", "Name", "Type", "Limit", "Username"]], use_container_width=True)

# --- PHASE 3: EMPLOYEE REIMBURSEMENT PORTAL ---
else:
    user_record = users_df[users_df["Username"] == st.session_state["username"]].iloc[0]
    emp_id = user_record["EmployeeID"]
    max_limit = float(user_record["Limit"])
    
    if st.sidebar.button(active_txt["logout"]):
        st.session_state["logged_in"] = False; st.session_state["user_role"] = ""; st.session_state["username"] = ""
        st.rerun()
        
    if not receipts_df.empty:
        receipts_df["EmployeeID"] = receipts_df["EmployeeID"].astype(str).str.strip().str.upper()
        receipts_df["ReimbursedAmount"] = pd.to_numeric(receipts_df["ReimbursedAmount"], errors='coerce').fillna(0.0)
        emp_history = receipts_df[receipts_df["EmployeeID"] == emp_id]
        total_spent = emp_history["ReimbursedAmount"].sum()
    else: total_spent = 0.0
        
    remaining_credit = max_limit - total_spent
    
    # Process DB designation string for active display
    translated_type_string = active_txt["ft"] if user_record["Type"] == "Full-Time" else active_txt["pt"]
    
    # Profiles display card metadata structure
    st.markdown(f"""
    <div class="card">
        <h3>{active_txt['welcome']}, {user_record['Name']}</h3>
        <p><strong>{active_txt['emp_code']}</strong> {emp_id}</p>
        <p><strong>{active_txt['status_assign']}</strong> {translated_type_string}</p>
        <p><strong>{active_txt['ann_limit']}</strong> ${max_limit:.2f}</p>
        <p><strong>{active_txt['tot_reimb']}</strong> ${total_spent:.2f}</p>
        <h4 style="color: {'#DC2626' if remaining_credit <= 0 else '#10B981'};">
            {active_txt['avail_credit']} ${remaining_credit:.2f}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"### {active_txt['sub_title']}")
    with st.form("claim_submission", clear_on_submit=True):
        store_name = st.text_input(active_txt["store"])
        receipt_amount = st.number_input(active_txt["total_rec"], min_value=0.0, step=0.01, format="%.2f")
        uploaded_file = st.file_uploader(active_txt["upload_img"], type=["png", "jpg", "jpeg"])
        submit_claim = st.form_submit_button(active_txt["sub_btn"])
        
        if submit_claim:
            if receipt_amount <= 0: st.error(active_txt["err_amt"])
            elif uploaded_file is None: st.error(active_txt["err_file"])
            elif remaining_credit <= 0: st.error(active_txt["err_maxed"])
            else:
                # Allocation clamp tracking calculations ("Burst" parameter validation rule)
                if receipt_amount > remaining_credit:
                    reimbursed_amount = remaining_credit
                    st.warning(f"{active_txt['warn_clamp']} **${reimbursed_amount:.2f}**.")
                else:
                    reimbursed_amount = receipt_amount
                    st.success(f"{active_txt['success_claim']} **${reimbursed_amount:.2f}**.")
                
                new_receipt = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "EmployeeID": emp_id,
                    "Name": user_record["Name"], "Type": user_record["Type"], "Store": store_name,
                    "ReceiptAmount": receipt_amount, "ReimbursedAmount": reimbursed_amount
                }])
                receipts_df = pd.concat([receipts_df, new_receipt], ignore_index=True)
                
                with st.spinner(active_txt["syncing"]):
                    # Step A: Route transaction documents straight to corporate emails matrix
                    email_success = send_finance_email(user_record, store_name, receipt_amount, reimbursed_amount, uploaded_file, active_txt)
                    
                    # Step B: Record ledger alterations to permanent repository sheet storage
                    db_success = save_and_push_to_github(receipts_df, users_df)
                    
                    if db_success:
                        st.toast("System synchronized successfully!", icon="💾")
                        st.rerun()

    st.write(active_txt["ledger_title"])
    if not receipts_df.empty:
        personal_logs = receipts_df[receipts_df["EmployeeID"] == emp_id]
        if not personal_logs.empty:
            st.dataframe(personal_logs[["Timestamp", "Store", "ReceiptAmount", "ReimbursedAmount"]], use_container_width=True)
        else: st.info(active_txt["no_logs"])
    else: st.info(active_txt["no_logs"])
