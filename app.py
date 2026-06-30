import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from git import Repo

# --- MODERN WHITE THEME & BRAND STYLING ---
st.set_page_config(page_title="Indigo Uniforms Reimbursement Database", page_icon="👔", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #1E293B !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    .header-container { display: flex; align-items: center; justify-content: space-between; padding-bottom: 20px; border-bottom: 2px solid #F1F5F9; margin-bottom: 30px; }
    .main-title { font-size: 26px; font-weight: 700; color: #1E3A8A !important; margin-bottom: 2px; }
    .subtitle { font-size: 12px; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0px; }
    
    .metric-card { background: #FFFFFF; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .circle-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 20px 0; }
    .svg-item { max-width: 160px; margin: 0 auto; }
    
    div[data-testid="stForm"] { border: 1px solid #E2E8F0 !important; border-radius: 12px !important; padding: 30px !important; background-color: #FFFFFF !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important; }
    
    .stButton>button { background-color: #1E3A8A !important; color: #FFFFFF !important; border-radius: 6px !important; border: none !important; transition: all 0.2s ease; }
    .stButton>button:hover { background-color: #1D4ED8 !important; transform: translateY(-1px); }
    
    /* Custom button styling for deletion actions to signal warning */
    .delete-btn>div>button { background-color: #DC2626 !important; color: #FFFFFF !important; }
    .delete-btn>div>button:hover { background-color: #B91C1C !important; }
    
    /* Dynamic Tabs Styling Customization */
    button[data-baseweb="tab"] { color: #64748B !important; font-weight: 600 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #1E3A8A !important; border-bottom-color: #1E3A8A !important; }
    </style>
""", unsafe_allow_html=True)

LOGO_URL = "https://i.ibb.co/mVRXHXpx/indigo-park-canada-logo.jpg"

if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

st.markdown('<div class="header-container">', unsafe_allow_html=True)
col_logo, col_titles, col_lang = st.columns([1, 4, 1.5])

with col_logo:
    st.image(LOGO_URL, use_container_width=True)

TXT = {
    "English": {
        "title": "Indigo Uniforms Reimbursement Database",
        "created_by": "Created by Only Solutions Inc.",
        "auth": "🔒 System Portal Authentication",
        "username": "Portal Username:",
        "password": "Secure Password:",
        "login_btn": "Access Portal Account",
        "invalid_pass": "❌ Invalid password verification provided.",
        "invalid_user": "❌ Credentials unrecognized by system registries.",
        "logout": "🚪 Log Out",
        "admin_title": "🛠️ Administrative Control Console",
        "tab_receipts": "📋 Receipts Verification Ledger",
        "tab_staff": "👤 Staff Roster Management",
        "create_title": "Create/Register New Staff Profile",
        "delete_title": "❌ Delete Employee Profile",
        "delete_select": "Select Employee Profile to Purge:",
        "delete_btn": "Permanently Remove Account",
        "delete_success": "✅ Employee profile successfully deleted from ledger registries!",
        "delete_empty": "No active registered profiles available to remove.",
        "form_user": "Assigned Username (lowercase, no spaces):",
        "form_pass": "Temporary Password:",
        "form_name": "Full Employee Name:",
        "form_id": "Unique Employee ID:",
        "form_type": "Employment Designation:",
        "pt": "Part-Time", "ft": "Full-Time",
        "save_btn": "Register & Save Profile",
        "err_fields": "❌ All form parameters must be completed.",
        "err_conflict": "❌ Account profile username conflict encountered.",
        "success_reg": "✅ Secure profile successfully mapped for",
        "roster": "Active Registered Staff Roster",
        "pending_ledger": "⏳ Pending Audit Review (Action Required)",
        "processed_ledger": "✅ Fully Processed & Reimbursed Archive",
        "save_status_btn": "💾 Save Verification Changes",
        "status_success": "✅ Receipt verification status updated and synced to GitHub!",
        "welcome": "Welcome back",
        "emp_code": "Employee ID:",
        "status_assign": "Status Assignment:",
        "ann_limit": "Annual Allocation Limit:",
        "tot_reimb": "Total Used to Date:",
        "avail_credit": "Available Balance remaining:",
        "sub_title": "📝 Register a Receipt for Verification",
        "store": "Store Name / Merchant:",
        "total_rec": "Receipt Grand Total ($):",
        "upload_img": "📷 Upload Image Copy of Receipt (For Corroboration)",
        "sub_btn": "Log Receipt inside System",
        "err_amt": "❌ Claim validation error: Invalid numeric payload.",
        "err_file": "❌ Verification asset failure: Receipt image attachment is strictly mandatory.",
        "err_maxed": "❌ Allocation Limit Overflow: Individual limits are fully utilized.",
        "warn_clamp": "⚠️ Limit Adjustment: This receipt crosses over your remaining balance. System scaled down approved total to:",
        "success_claim": "✅ Receipt logged in system database. Approved system validation amount:",
        "ledger_title": "### 📜 Your Registered Receipts Ledger",
        "no_logs": "No recorded receipts linked to this profile index.",
        "no_pending": "No pending items requiring administrative audit review.",
        "no_processed": "No receipts have been processed or marked as reimbursed yet.",
        "syncing": "Writing transaction data securely to ledger...",
        "chart_label": "Used of Limit",
        "img_preview_title": "🔍 Secure Receipt Management & Preview Console",
        "img_preview_instruction": "Select a receipt record index to audit or manage:",
        "img_preview_empty": "No transaction image payload exists for this index profile.",
        "no_any_receipts": "No transactions have been recorded in the system yet.",
        "delete_tx_btn": "❌ Permanently Delete This Transaction Entry",
        "delete_tx_success": "✅ Transaction successfully purged from database and synced to GitHub!"
    },
    "Français": {
        "title": "Base de données de remboursement des uniformes Indigo",
        "created_by": "Créé par Only Solutions Inc.",
        "auth": "🔒 Authentification au portail système",
        "username": "Nom d'utilisateur :",
        "password": "Mot de passe sécurisé :",
        "login_btn": "Accéder au compte du portail",
        "invalid_pass": "❌ Validation du mot de passe fournie non valide.",
        "invalid_user": "❌ Identifiants non reconnus par les registres du système.",
        "logout": "🚪 Se déconnecter",
        "admin_title": "🛠️ Console de contrôle administratif",
        "tab_receipts": "📋 Vérification des reçus",
        "tab_staff": "👤 Gestion du personnel",
        "create_title": "Créer/Enregistrer un nouveau profil d'employé",
        "delete_title": "❌ Supprimer un profil d'employé",
        "delete_select": "Sélectionner le profil d'employé à supprimer :",
        "delete_btn": "Supprimer définitivement le compte",
        "delete_success": "✅ Le profil de l'employé a été supprimé avec succès des registres !",
        "delete_empty": "Aucun profil enregistré disponible pour la suppression.",
        "form_user": "Nom d'utilisateur assigné (minuscules, sans espace) :",
        "form_pass": "Mot de passe temporaire :",
        "form_name": "Nom complet de l'employé :",
        "form_id": "Identifiant d'employé unique :",
        "form_type": "Désignation de l'emploi :",
        "pt": "Temps partiel", "ft": "Temps plein",
        "save_btn": "Enregistrer et sauvegarder le profil",
        "err_fields": "❌ Tous les champs du formulaire doivent être remplis.",
        "err_conflict": "❌ Conflit de nom d'utilisateur rencontré.",
        "success_reg": "✅ Profil de compte sécurisé configuré avec succès pour",
        "roster": "Roster du personnel actif enregistré",
        "pending_ledger": "⏳ En attente de vérification (Action requise)",
        "processed_ledger": "✅ Archive des reçus traités et remboursés",
        "save_status_btn": "💾 Sauvegarder les vérifications",
        "status_success": "✅ Statut de vérification mis à jour et synchronisé sur GitHub !",
        "welcome": "Bon retour",
        "emp_code": "ID de l'employé :",
        "status_assign": "Statut d'emploi :",
        "ann_limit": "Limite d'allocation annuelle :",
        "tot_reimb": "Total utilisé à ce jour :",
        "avail_credit": "Solde de crédit restant :",
        "sub_title": "📝 Enregistrer un reçu pour vérification",
        "store": "Nom du magasin / Marchand :",
        "total_rec": "Montant total du reçu ($) :",
        "upload_img": "📷 Téléverser une photo du reçu (Pour corroboration)",
        "sub_btn": "Enregistrer le reçu dans le système",
        "err_amt": "❌ Erreur d'enregistrement : Le montant saisi n'est pas valide.",
        "err_file": "❌ Échec de vérification : La photo du reçu est strictement obligatoire.",
        "err_maxed": "❌ Limite atteinte : Vos paramètres de limite annuelle sont entièrement utilisés.",
        "warn_clamp": "⚠️ Avis de plafonnement : Cette soumission dépasse votre couverture. Le système a automatiquement réduit le montant approuvé à :",
        "success_claim": "✅ Reçu enregistré dans la base de données. Montant approuvé pour corroboration :",
        "ledger_title": "### 📜 Historique de vos reçus enregistrés",
        "no_logs": "Aucune transaction enregistrée liée à ce profil.",
        "no_pending": "Aucun reçu en attente d'approbation pour le moment.",
        "no_processed": "Aucun reçu n'a encore été marqué comme remboursé.",
        "syncing": "Écriture sécurisée des données dans le registre...",
        "chart_label": "Utilisé de la limite",
        "img_preview_title": "🔍 Console de gestion et d'aperçu des transactions",
        "img_preview_instruction": "Sélectionnez une transaction pour l'analyser ou la supprimer :",
        "img_preview_empty": "Aucune image de reçu attachée à cette transaction.",
        "no_any_receipts": "Aucun reçu n'a été enregistré dans le système pour le moment.",
        "delete_tx_btn": "❌ Supprimer définitivement cette transaction",
        "delete_tx_success": "✅ Transaction supprimée avec succès du registre et synchronisée sur GitHub !"
    }
}

with col_titles:
    st.markdown(f'<div class="main-title">{TXT[st.session_state["lang"]]["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{TXT[st.session_state["lang"]]["created_by"]}</div>', unsafe_allow_html=True)

with col_lang:
    lang_toggle = st.radio("🌐", ["Français", "English"], index=0 if st.session_state["lang"] == "Français" else 1, horizontal=True, label_visibility="collapsed")
    if lang_toggle != st.session_state["lang"]:
        st.session_state["lang"] = lang_toggle
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- DATABASE CONTROL LAYER (SELF-HEALING) ---
EXCEL_FILE = "database.xlsx"

def load_database():
    req_receipts = ["Timestamp", "EmployeeID", "Name", "Type", "Store", "ReceiptAmount", "ReimbursedAmount", "Reimbursed", "ReceiptImage"]
    req_users = ["Username", "Password", "Name", "EmployeeID", "Type", "Limit"]
    
    if os.path.exists(EXCEL_FILE):
        try: 
            receipts_df = pd.read_excel(EXCEL_FILE, sheet_name="receipts")
            for col in req_receipts:
                if col not in receipts_df.columns: 
                    receipts_df[col] = False if col == "Reimbursed" else ""
        except: 
            receipts_df = pd.DataFrame(columns=req_receipts)
            
        try: 
            users_df = pd.read_excel(EXCEL_FILE, sheet_name="users")
            for col in req_users:
                if col not in users_df.columns: users_df[col] = ""
        except: 
            users_df = pd.DataFrame(columns=req_users)
    else:
        receipts_df = pd.DataFrame(columns=req_receipts)
        users_df = pd.DataFrame(columns=req_users)
    
    receipts_df["Reimbursed"] = receipts_df["Reimbursed"].astype(bool)
    receipts_df["ReceiptImage"] = receipts_df["ReceiptImage"].fillna("").astype(str)
    users_df["Username"] = users_df["Username"].astype(str).str.strip().str.lower()
    return receipts_df, users_df

def save_and_push_to_github(receipts_df, users_df):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        receipts_df.to_excel(writer, sheet_name="receipts", index=False)
        users_df.to_excel(writer, sheet_name="users", index=False)
    try:
        token = st.secrets["github"]["token"]
        repo_url = st.secrets["github"]["repo_url"]
        authenticated_url = repo_url.replace("https://", f"https://oauth2:{token}@")
        
        repo = Repo(".")
        repo.git.checkout('main')
        
        try: origin = repo.remote(name="origin"); origin.set_url(authenticated_url)
        except: origin = repo.create_remote("origin", authenticated_url)
        
        repo.git.add(EXCEL_FILE)
        repo.index.commit("Automated secure database update [Only Solutions System]")
        origin.push("main")
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}

receipts_df, users_df = load_database()
active_txt = TXT[st.session_state["lang"]]

if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = ""
if "username" not in st.session_state: st.session_state["username"] = ""

# --- PHASE 1: LOGIN ---
if not st.session_state["logged_in"]:
    st.write(f"### {active_txt['auth']}")
    with st.form("login_form"):
        username_input = st.text_input(active_txt["username"]).strip().lower()
        password_input = st.text_input(active_txt["password"], type="password").strip()
        login_submit = st.form_submit_button(active_txt["login_btn"])
        
        if login_submit:
            if username_input == "admin" and password_input == "12345":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "admin"
                st.session_state["username"] = "admin"
                st.rerun()
            elif not users_df.empty and username_input in users_df["Username"].values:
                user_record = users_df[users_df["Username"] == username_input].iloc[0]
                if str(user_record["Password"]) == password_input:
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "employee"
                    st.session_state["username"] = username_input
                    st.rerun()
                else: st.error(active_txt["invalid_pass"])
            else: st.error(active_txt["invalid_user"])

# --- PHASE 2: ADMIN PANEL WITH RECEPTACLE TABS ---
elif st.session_state["user_role"] == "admin":
    st.sidebar.title("Admin")
    if st.sidebar.button(active_txt["logout"]):
        st.session_state["logged_in"] = False; st.session_state["user_role"] = ""; st.session_state["username"] = ""
        st.rerun()
        
    st.write(f"### {active_txt['admin_title']}")
    
    tab_receipts, tab_staff = st.tabs([active_txt["tab_receipts"], active_txt["tab_staff"]])
    
    # TAB 1: RECEIPTS AUDIT LOG
    with tab_receipts:
        pending_df = receipts_df[receipts_df["Reimbursed"] == False].reset_index(drop=True)
        processed_df = receipts_df[receipts_df["Reimbursed"] == True].reset_index(drop=True)
        
        # SECTION 1: PENDING RECEIPTS FOR REVIEW
        st.write(f"#### {active_txt['pending_ledger']}")
        if not pending_df.empty:
            edited_pending = st.data_editor(
                pending_df[["Timestamp", "EmployeeID", "Name", "Store", "ReceiptAmount", "ReimbursedAmount", "Reimbursed"]],
                column_config={
                    "Reimbursed": st.column_config.CheckboxColumn(
                        "Reimbursed (OK)",
                        default=False,
                    )
                },
                disabled=["Timestamp", "EmployeeID", "Name", "Store", "ReceiptAmount", "ReimbursedAmount"],
                use_container_width=True,
                key="admin_pending_editor_v3"
            )
            
            if not edited_pending["Reimbursed"].equals(pending_df["Reimbursed"]):
                if st.button(active_txt["save_status_btn"], key="save_pending_btn"):
                    for idx, row in edited_pending.iterrows():
                        if row["Reimbursed"] == True:
                            receipts_df.loc[
                                (receipts_df["Timestamp"] == row["Timestamp"]) & 
                                (receipts_df["EmployeeID"] == row["EmployeeID"]), "Reimbursed"
                            ] = True
                            
                    with st.spinner(active_txt["syncing"]):
                        res = save_and_push_to_github(receipts_df, users_df)
                        if res["success"]:
                            st.success(active_txt["status_success"])
                            st.rerun()
                        else:
                            st.error(f"❌ GitHub Sync Blocked: {res['error']}")
        else:
            st.info(active_txt["no_pending"])
            
        st.markdown("---")
        
        # SECTION 2: ARCHIVED/PROCESSED RECEIPTS
        st.write(f"#### {active_txt['processed_ledger']}")
        if not processed_df.empty:
            st.data_editor(
                processed_df[["Timestamp", "EmployeeID", "Name", "Store", "ReceiptAmount", "ReimbursedAmount", "Reimbursed"]],
                disabled=["Timestamp", "EmployeeID", "Name", "Store", "ReceiptAmount", "ReimbursedAmount", "Reimbursed"],
                use_container_width=True,
                key="admin_processed_editor_v3"
            )
        else:
            st.info(active_txt["no_processed"])
            
        st.markdown("---")
        
        # SECTION 3: MANAGEMENT PANEL (PREVIEW + DELETION LOGIC)
        st.write(f"#### {active_txt['img_preview_title']}")
        if not receipts_df.empty:
            receipts_df["DropdownLabel"] = receipts_df["Name"] + " - " + receipts_df["Store"] + " ($" + receipts_df["ReceiptAmount"].astype(str) + ") [" + receipts_df["Timestamp"] + "]"
            label_options = receipts_df["DropdownLabel"].tolist()
            
            col_select, col_delete = st.columns([2.5, 1.5])
            
            with col_select:
                selected_label = st.selectbox(active_txt["img_preview_instruction"], label_options, index=0)
            
            if selected_label:
                matched_row = receipts_df[receipts_df["DropdownLabel"] == selected_label].iloc[0]
                selected_timestamp = matched_row["Timestamp"]
                selected_emp_id = matched_row["EmployeeID"]
                selected_image_str = matched_row["ReceiptImage"]
                
                with col_delete:
                    st.markdown('<div class="delete-btn" style="margin-top: 28px;">', unsafe_allow_html=True)
                    delete_tx_clicked = st.button(active_txt["delete_tx_btn"], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if delete_tx_clicked:
                        # Drop row based on exact combination keys
                        updated_receipts_df = receipts_df[~(
                            (receipts_df["Timestamp"] == selected_timestamp) & 
                            (receipts_df["EmployeeID"] == selected_emp_id)
                        )].copy()
                        
                        # Strip dropdown parsing construction helper row column out before filing to excel
                        if "DropdownLabel" in updated_receipts_df.columns:
                            updated_receipts_df = updated_receipts_df.drop(columns=["DropdownLabel"])
                            
                        with st.spinner(active_txt["syncing"]):
                            res = save_and_push_to_github(updated_receipts_df, users_df)
                            if res["success"]:
                                st.success(active_txt["delete_tx_success"])
                                st.rerun()
                            else:
                                st.error(f"❌ Deletion failed to push to GitHub registry: {res['error']}")
                
                # Render Image underneath actions
                if selected_image_str and selected_image_str.strip() != "":
                    try:
                        img_bytes = base64.b64decode(selected_image_str)
                        st.image(img_bytes, use_container_width=True)
                    except:
                        st.error(active_txt["img_preview_empty"])
                else:
                    st.error(active_txt["img_preview_empty"])
        else:
            st.info(active_txt["no_any_receipts"])
            
    # TAB 2: STAFF ROSTER & MUTATION ACTIONS
    with tab_staff:
        with st.form("create_user_form", clear_on_submit=True):
            st.write(f"#### {active_txt['create_title']}")
            new_user = st.text_input(active_txt["form_user"]).strip().lower()
            new_pass = st.text_input(active_txt["form_pass"]).strip()
            new_name = st.text_input(active_txt["form_name"]).strip()
            new_id = st.text_input(active_txt["form_id"]).strip().upper()
            
            type_options = [active_txt["ft"], active_txt["pt"]]
            new_type_sel = st.selectbox(active_txt["form_type"], type_options)
            create_btn = st.form_submit_button(active_txt["save_btn"])
            
            if create_btn:
                if not (new_user and new_pass and new_name and new_id):
                    st.error(active_txt["err_fields"])
                elif not users_df.empty and new_user in users_df["Username"].values:
                    st.error(active_txt["err_conflict"])
                else:
                    db_type_string = "Full-Time" if new_type_sel == active_txt["ft"] else "Part-Time"
                    limit_allocation = 175.00 if db_type_string == "Full-Time" else 100.00
                    new_profile = pd.DataFrame([{
                        "Username": new_user, "Password": new_pass, "Name": new_name,
                        "EmployeeID": new_id, "Type": db_type_string, "Limit": limit_allocation
                    }])
                    updated_users = pd.concat([users_df, new_profile], ignore_index=True)
                    
                    with st.spinner(active_txt["syncing"]):
                        res = save_and_push_to_github(receipts_df, updated_users)
                        if res["success"]:
                            st.success(f"{active_txt['success_reg']} {new_name}!")
                            st.rerun()
                        else:
                            st.error(f"❌ Register Failed! GitHub rejected spreadsheet push: {res['error']}")

        st.write(f"#### {active_txt['roster']}")
        if not users_df.empty:
            st.dataframe(users_df[["EmployeeID", "Name", "Type", "Limit", "Username"]], use_container_width=True)
            
            st.markdown("---")
            with st.form("delete_user_form"):
                st.write(f"#### {active_txt['delete_title']}")
                user_list = users_df["Username"].tolist()
                target_user = st.selectbox(active_txt["delete_select"], user_list)
                
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                delete_btn = st.form_submit_button(active_txt["delete_btn"])
                st.markdown('</div>', unsafe_allow_html=True)
                
                if delete_btn:
                    updated_users = users_df[users_df["Username"] != target_user]
                    with st.spinner(active_txt["syncing"]):
                        res = save_and_push_to_github(receipts_df, updated_users)
                        if res["success"]:
                            st.success(active_txt["delete_success"])
                            st.rerun()
                        else:
                            st.error(f"❌ Delete Failed! GitHub rejected spreadsheet push: {res['error']}")
        else:
            st.info(active_txt["delete_empty"])

# --- PHASE 3: EMPLOYEE PORTAL ---
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
        emp_history = receipts_df[receipts_df["EmployeeID"] == str(emp_id).strip().upper()]
        total_spent = emp_history["ReimbursedAmount"].sum()
    else: total_spent = 0.0
        
    remaining_credit = max_limit - total_spent
    
    percentage = (total_spent / max_limit) * 100 if max_limit > 0 else 0
    percentage = min(percentage, 100)
    stroke_dasharray = f"{percentage}, 100"

    col_info, col_graphic = st.columns([1.8, 1.2])
    
    with col_info:
        translated_type_string = active_txt["ft"] if user_record["Type"] == "Full-Time" else active_txt["pt"]
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin-top:0; margin-bottom:15px; font-weight:700;">{active_txt['welcome']}, {user_record['Name']}</h3>
            <p style="margin:4px 0;"><strong>{active_txt['emp_code']}</strong> {emp_id}</p>
            <p style="margin:4px 0;"><strong>{active_txt['status_assign']}</strong> {translated_type_string}</p>
            <p style="margin:4px 0;"><strong>{active_txt['ann_limit']}</strong> ${max_limit:.2f}</p>
            <p style="margin:4px 0;"><strong>{active_txt['tot_reimb']}</strong> ${total_spent:.2f}</p>
            <h4 style="color: {'#DC2626' if remaining_credit <= 0 else '#10B981'}; margin-top:15px; margin-bottom:0; font-weight:700;">
                {active_txt['avail_credit']} ${remaining_credit:.2f}
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
    with col_graphic:
        st.markdown(f"""
        <div class="metric-card circle-container">
            <svg viewBox="0 0 36 36" class="svg-item">
                <path style="fill: none; stroke: #E2E8F0; stroke-width: 3.8;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path style="fill: none; stroke: #1E3A8A; stroke-width: 3.8; stroke-linecap: round; transition: stroke-dasharray 0.6s ease;" stroke-dasharray="{stroke_dasharray}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <text x="18" y="20.3" style="font-family: sans-serif; font-size: 7px; font-weight: bold; text-anchor: middle; fill: #0F172A;">{int(percentage)}%</text>
            </svg>
            <div class="metric-label" style="margin-top: 10px; font-weight:600; text-align:center;">{active_txt['chart_label']}</div>
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
                if receipt_amount > remaining_credit:
                    reimbursed_amount = remaining_credit
                    st.warning(f"{active_txt['warn_clamp']} **${reimbursed_amount:.2f}**.")
                else:
                    reimbursed_amount = receipt_amount
                    st.success(f"{active_txt['success_claim']} **${reimbursed_amount:.2f}**.")
                
                base64_image_encoded = base64.b64encode(uploaded_file.read()).decode("utf-8")
                
                new_receipt = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "EmployeeID": str(emp_id),
                    "Name": user_record["Name"], "Type": user_record["Type"], "Store": store_name,
                    "ReceiptAmount": receipt_amount, "ReimbursedAmount": reimbursed_amount, 
                    "Reimbursed": False, "ReceiptImage": base64_image_encoded
                }])
                updated_receipts = pd.concat([receipts_df, new_receipt], ignore_index=True)
                
                with st.spinner(active_txt["syncing"]):
                    res = save_and_push_to_github(updated_receipts, users_df)
                    if res["success"]:
                        st.rerun()
                    else:
                        st.error(f"❌ Submission Failed! GitHub rejected spreadsheet push: {res['error']}")

    st.write(active_txt["ledger_title"])
    if not receipts_df.empty:
        personal_logs = receipts_df[receipts_df["EmployeeID"] == str(emp_id)]
        if not personal_logs.empty:
            st.dataframe(personal_logs[["Timestamp", "Store", "ReceiptAmount", "ReimbursedAmount", "Reimbursed"]], use_container_width=True)
        else: st.info(active_txt["no_logs"])
    else: st.info(active_txt["no_logs"])
