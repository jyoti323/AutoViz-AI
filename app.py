import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import hashlib
import io
import datetime
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# Page configuration
st.set_page_config(
    page_title="AutoViz AI Enterprise",
    page_icon="🔮",
    layout="wide"
)

# User and File Storage Paths
USER_DB_FILE = "users.json"
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# State management variables initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = "Analyst"
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []
if 'clean_logs' not in st.session_state:
    st.session_state.clean_logs = {"rows_removed": 0, "nulls_fixed": 0, "types_converted": 0}
if 'dashboards' not in st.session_state:
    st.session_state.dashboards = []
if 'global_stats' not in st.session_state:
    st.session_state.global_stats = {"datasets": 3, "records": 12840, "charts": 34, "users": 4}

# Password hashing helper
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load users
def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            data = json.load(f)
            # Support backwards compatibility if stored users don't have roles
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = {"hash": v, "role": "Analyst"}
            return data
    except:
        return {}

# Save users
def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Register user
def register_user(username, password, role="Analyst"):
    users = load_users()
    if username in users:
        return False
    users[username] = {"hash": hash_password(password), "role": role}
    save_users(users)
    return True

# Verify user credentials
def verify_user(username, password):
    users = load_users()
    if username not in users:
        return None
    user_info = users[username]
    if user_info["hash"] == hash_password(password):
        return user_info["role"]
    return None

# Storage helpers
def get_user_storage_dir(username):
    user_dir = os.path.join(STORAGE_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def list_user_files(username):
    user_dir = get_user_storage_dir(username)
    return [f for f in os.listdir(user_dir) if f.endswith(".csv")]

def save_user_file(username, filename, df):
    user_dir = get_user_storage_dir(username)
    if not filename.endswith(".csv"):
        filename += ".csv"
    file_path = os.path.join(user_dir, filename)
    df.to_csv(file_path, index=False)

def delete_user_file(username, filename):
    user_dir = get_user_storage_dir(username)
    file_path = os.path.join(user_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

# Custom Styling Injection (Theme Aware)
def apply_theme_css():
    """Apply a refined, theme-aware visual system with subtle motion."""
    dark = st.session_state.theme == "Dark"
    bg_color = "#0D1117" if dark else "#F5F6FA"
    text_color = "#E8EAF0" if dark else "#202435"
    sidebar_bg = "#10151E" if dark else "#FFFFFF"
    card_bg = "rgba(23, 29, 41, 0.88)" if dark else "rgba(255, 255, 255, 0.92)"
    card_border = "rgba(194, 166, 110, 0.20)" if dark else "rgba(43, 55, 84, 0.10)"
    muted = "#9AA3B2" if dark else "#737B8C"
    accent = "#C9A96E"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
        :root {{ --accent: {accent}; --surface: {card_bg}; --muted: {muted}; }}
        html, body, [class*="css"], .stApp {{ font-family: 'DM Sans', sans-serif; background-color: {bg_color} !important; color: {text_color} !important; }}
        .stApp {{ animation: app-enter .55s ease both; }}
        @keyframes app-enter {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes rise-in {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .title-container {{ text-align: left; margin: 12px 0 28px; animation: rise-in .55s ease both; }}
        .glowing-title {{ font: 700 2.45rem 'Playfair Display', Georgia, serif !important; color: {text_color} !important; letter-spacing: -.035em; }}
        .subtitle {{ font-size: .98rem; color: {muted}; font-weight: 400; }}
        .metric-card {{ background: linear-gradient(145deg, {card_bg}, transparent), {card_bg}; border: 1px solid {card_border}; border-radius: 16px; padding: 20px 18px; text-align: left; box-shadow: 0 12px 30px rgba(0,0,0,.08); transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease; animation: rise-in .5s ease both; }}
        .metric-card:hover {{ transform: translateY(-4px); border-color: rgba(201,169,110,.55); box-shadow: 0 16px 34px rgba(0,0,0,.14); }}
        .metric-val {{ font-size: 2rem; font-weight: 700; color: {accent}; font-variant-numeric: tabular-nums; }}
        .metric-lbl {{ font-size: .73rem; color: {muted}; text-transform: uppercase; letter-spacing: .10em; }}
        .auth-card {{ background: {card_bg}; border: 1px solid {card_border}; border-radius: 20px; padding: 28px; box-shadow: 0 20px 55px rgba(0,0,0,.15); }}
        .stButton>button, .stDownloadButton>button {{ border-radius: 10px !important; border: 1px solid rgba(201,169,110,.44) !important; color: {text_color} !important; background: linear-gradient(135deg, rgba(201,169,110,.20), rgba(201,169,110,.08)) !important; font-weight: 600 !important; transition: transform .18s ease, box-shadow .18s ease, background .18s ease !important; }}
        .stButton>button:hover, .stDownloadButton>button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 8px 22px rgba(201,169,110,.18) !important; border-color: {accent} !important; }}
        [data-testid="stMetric"], [data-testid="stExpander"], [data-testid="stForm"] {{ border-radius: 14px; }}
        [data-testid="stPlotlyChart"] {{ border: 1px solid {card_border}; border-radius: 16px; padding: 8px; background: {card_bg}; animation: rise-in .45s ease both; }}
        div[data-testid="stFileUploader"] {{ background: {card_bg} !important; border: 1px dashed rgba(201,169,110,.48) !important; border-radius: 14px !important; }}
        section[data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {card_border} !important; }}
        section[data-testid="stSidebar"] h2 {{ font-family: 'Playfair Display', Georgia, serif; }}
        hr {{ border-color: {card_border} !important; margin: 22px 0 !important; }}
        .stButton>button:focus-visible, .stDownloadButton>button:focus-visible {{ outline: 2px solid #C9A96E !important; outline-offset: 3px; }}
        .stButton>button:active, .stDownloadButton>button:active {{ transform: translateY(0) scale(.985) !important; }}
        div[data-baseweb="select"]:focus-within {{ box-shadow: 0 0 0 2px rgba(201,169,110,.28); border-radius: 10px; }}
        input:focus, textarea:focus {{ border-color: #C9A96E !important; box-shadow: 0 0 0 1px rgba(201,169,110,.22) !important; }}
        [data-testid="stRadio"] input {{ accent-color: #C9A96E; }}
        [data-testid="stCheckbox"] input {{ accent-color: #C9A96E; }}
        [data-testid="stToggle"] {{ transition: filter .2s ease; }}
        [data-testid="stToggle"]:hover {{ filter: brightness(1.12); }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {{ border-radius: 10px; transition: background .18s ease, transform .18s ease; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {{ background: rgba(201,169,110,.10); transform: translateX(2px); }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {{ background: rgba(201,169,110,.13); border-left: 2px solid #C9A96E; }}
        [data-testid="stExpander"] {{ border: 1px solid {card_border}; background: {card_bg}; }}
        [data-baseweb="tab"][aria-selected="true"] {{ color: #C9A96E !important; }}
        [data-baseweb="tab-highlight"] {{ background-color: #C9A96E !important; }}
        [data-testid="stPlotlyChart"] {{ transition: border-color .2s ease, box-shadow .2s ease; }}
        [data-testid="stPlotlyChart"]:hover {{ border-color: rgba(201,169,110,.42); box-shadow: 0 10px 28px rgba(0,0,0,.10); }}
        div[data-testid="stFileUploader"] {{ transition: border-color .2s ease, background .2s ease; }}
        div[data-testid="stFileUploader"]:hover {{ border-color: #C9A96E !important; }}
        [data-testid="stDataFrame"], [data-testid="stTable"] {{ border-radius: 12px; overflow: hidden; }}
        [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {{ scroll-margin-top: 1rem; }}
        @media (max-width: 720px) {{ .glowing-title {{ font-size: 2rem !important; }} .title-container {{ margin-bottom: 20px; }} }}
        @media (max-width: 720px) {{ [data-testid="stPlotlyChart"] {{ padding: 4px; border-radius: 12px; }} .metric-card {{ padding: 16px; }} }}
        .metric-lbl {{ transition: color .2s ease; }}
        .metric-card:hover .metric-lbl {{ color: {text_color}; }}
        section[data-testid="stSidebar"] h2 {{ letter-spacing: -.02em; }}
        @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }} }}
        </style>
    """, unsafe_allow_html=True)

# Helper: Style Plotly Figures globally based on theme preference
def style_plotly_fig(fig):
    theme_template = "plotly_dark" if st.session_state.theme == "Dark" else "plotly_white"
    bg = "rgba(0,0,0,0)"
    font_color = "#E8EAF0" if st.session_state.theme == "Dark" else "#202435"
    grid_color = "rgba(255,255,255,0.075)" if st.session_state.theme == "Dark" else "rgba(32,36,53,0.08)"
    
    fig.update_layout(
        template=theme_template,
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(family="Outfit, sans-serif", color=font_color),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor=grid_color),
        yaxis=dict(gridcolor=grid_color),
        colorway=["#C9A96E", "#7797B8", "#91A68A", "#B88778", "#9B8CB5"],
        transition={"duration": 450, "easing": "cubic-in-out"},
        hoverlabel=dict(bgcolor="#1B2230", font_color="#F5F6FA", bordercolor="#C9A96E")
    )
    return fig

def build_chart(df, spec):
    """Build a chart consistently for both the preview and pinned dashboard."""
    chart_type = spec["type"]
    x_col, y_col = spec.get("x"), spec.get("y")
    color = spec.get("color") or None
    size = spec.get("size") or None
    title = spec.get("title") or (f"{chart_type} · {x_col}" + (f" vs {y_col}" if y_col else ""))
    if chart_type == "Scatter":
        fig = px.scatter(df, x=x_col, y=y_col, color=color, size=size, title=title)
    elif chart_type == "Line":
        fig = px.line(df, x=x_col, y=y_col, color=color, title=title)
    elif chart_type == "Bar":
        fig = px.bar(df, x=x_col, y=y_col, color=color, title=title)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_col, color=color, title=title)
    elif chart_type == "Box":
        fig = px.box(df, x=x_col, y=y_col, color=color, title=title)
    elif chart_type == "Correlation Matrix":
        numeric = df.select_dtypes(include=["number"])
        if numeric.shape[1] < 2:
            return None
        fig = px.imshow(numeric.corr(), text_auto=".2f", color_continuous_scale="RdBu_r", title="Correlation matrix")
    elif chart_type == "Bubble":
        if not size:
            return None
        fig = px.scatter(df, x=x_col, y=y_col, color=color, size=size, size_max=50, title=title)
    elif chart_type == "Treemap":
        fig = px.treemap(df, path=[x_col], color=color, title=title)
    elif chart_type == "Radar":
        if not y_col:
            return None
        grouped = df.groupby(x_col, dropna=False)[y_col].mean().reset_index()
        fig = px.line_polar(grouped, r=y_col, theta=x_col, line_close=True, title=title)
    else:
        return None
    return style_plotly_fig(fig)


# Helper: Load dataset and update metrics
def setup_active_dataset(df, filename):
    st.session_state.df = df
    st.session_state.original_df = df.copy()
    st.session_state.file_name = filename
    st.session_state.clean_logs = {"rows_removed": 0, "nulls_fixed": 0, "types_converted": 0}
    
    # Increment global statistics counter
    st.session_state.global_stats["datasets"] += 1
    st.session_state.global_stats["records"] += df.shape[0]
    
    # Add to history
    today = datetime.date.today().strftime("%Y-%m-%d")
    st.session_state.upload_history.append({
        "name": filename,
        "date": today,
        "rows": df.shape[0],
        "charts": 0
    })

# Apply dynamic styling
apply_theme_css()

# Navigation panel layout in Sidebar
st.sidebar.markdown("<h2 style='color: #00F2FE; margin: 0;'>AutoViz AI</h2>", unsafe_allow_html=True)
st.sidebar.caption("Enterprise Analytics Portal")

# Sidebar Theme Switcher
theme_toggle = st.sidebar.toggle("☀️ Light Mode" if st.session_state.theme == "Light" else "🌙 Dark Mode", value=(st.session_state.theme == "Light"))
st.session_state.theme = "Light" if theme_toggle else "Dark"

# 1. AUTHENTICATION HUB
if not st.session_state.logged_in:
    # Login / signup window
    pad_l, cent, pad_r = st.columns([1.2, 1.6, 1.2])
    
    with cent:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px; margin-top: 40px;">
                <h2 style="color: #00F2FE; margin-bottom: 0px;">AutoViz AI Portal</h2>
                <p style="color: #94A3B8; font-size: 0.9rem;">Sign in or register to launch the analytics dashboard</p>
            </div>
        """, unsafe_allow_html=True)
        
        auth_mode = st.radio("", ["Sign In", "Create Account"], horizontal=True, label_visibility="collapsed")
        
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        auth_username = st.text_input("Username", placeholder="e.g. manager1")
        auth_password = st.text_input("Password", type="password", placeholder="Password")
        
        role_choice = "Analyst"
        if auth_mode == "Create Account":
            role_choice = st.selectbox("Assign User Role", ["Admin", "Analyst", "Viewer"], help="Admin = full control. Analyst = visualizer + limited data cleaning. Viewer = read-only dashboard.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if auth_mode == "Sign In":
            if st.button("Access Dashboard"):
                if not auth_username or not auth_password:
                    st.error("Please enter both username and password.")
                else:
                    role = verify_user(auth_username, auth_password)
                    if role:
                        st.session_state.logged_in = True
                        st.session_state.user = auth_username
                        st.session_state.role = role
                        # Increment active users
                        st.session_state.global_stats["users"] += 1
                        st.toast(f"Successfully logged in as {role}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        else:
            if st.button("Create Profile"):
                if not auth_username or not auth_password:
                    st.error("Please enter both username and password.")
                elif len(auth_password) < 4:
                    st.error("Password must be at least 4 characters.")
                elif register_user(auth_username, auth_password, role_choice):
                    st.session_state.logged_in = True
                    st.session_state.user = auth_username
                    st.session_state.role = role_choice
                    st.session_state.global_stats["users"] += 1
                    st.success("Profile created! Unlocking workspace...")
                    st.rerun()
                else:
                    st.error("Username already registered.")
                    
        st.markdown('</div>', unsafe_allow_html=True)

# DASHBOARD MAIN WORKSPACE
else:
    # Sidebar Profile details
    st.sidebar.divider()
    st.sidebar.markdown(f"👤 User: **{st.session_state.user}**")
    
    # Permission badges
    role_color = "#10B981" if st.session_state.role == "Admin" else ("#3B82F6" if st.session_state.role == "Analyst" else "#64748B")
    st.sidebar.markdown(f"Role: <span style='background-color: {role_color}; padding: 3px 8px; border-radius: 4px; color: white; font-size: 0.8rem; font-weight: 600;'>{st.session_state.role}</span>", unsafe_allow_html=True)
    
    # Navigation Selector
    page = st.sidebar.selectbox("Navigation Hub", [
        "🏠 Workspace Hub",
        "📁 Data Center",
        "🛠️ Advanced Cleaner",
        "🎨 Visualizer Studio",
        "🧠 AI Analytics Desk",
        "🔮 Predictive ML Sandbox"
    ])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.df = None
        st.session_state.original_df = None
        st.session_state.file_name = None
        st.toast("Logged out.")
        st.rerun()

    # ---------------------------------------------
    # 🏠 WORKSPACE HUB PAGE
    # ---------------------------------------------
    if page == "🏠 Workspace Hub":
        st.markdown(f"""
            <div class="title-container">
                <h1 class="glowing-title">Workspace Hub</h1>
                <p class="subtitle">Welcome, <b>{st.session_state.user}</b>. Review global performance logs and active data profiles.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Enterprise Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Datasets Processed</div><div class="metric-val">{st.session_state.global_stats["datasets"]}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Total Records Scanned</div><div class="metric-val">{st.session_state.global_stats["records"]:,}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Visualizations Built</div><div class="metric-val">{st.session_state.global_stats["charts"]}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">Active Portal Users</div><div class="metric-val">{st.session_state.global_stats["users"]}</div></div>', unsafe_allow_html=True)
            
        st.divider()
        
        # Layout splitting User Details and Activity Chart
        left, right = st.columns(2)
        with left:
            st.subheader("Your Profile Permissions")
            
            # Interactive switch role to test permissions
            st.markdown("💡 *To demonstrate permissions to an interviewer, you can dynamically switch roles below:*")
            role_swap = st.selectbox("Simulate Role Swap", ["Admin", "Analyst", "Viewer"], index=["Admin", "Analyst", "Viewer"].index(st.session_state.role))
            if role_swap != st.session_state.role:
                st.session_state.role = role_swap
                st.toast(f"Role updated to {role_swap}!")
                st.rerun()
                
            perms = {
                "Admin": ["✓ View dataset profiles", "✓ Build custom dashboards & export code", "✓ Run Machine Learning algorithms", "✓ Execute Data Cleaner tools", "✓ Save & Delete files from account storage"],
                "Analyst": ["✓ View dataset profiles", "✓ Build custom dashboards & export code", "✓ Run Machine Learning algorithms", "⚠️ Restricted: Impute nulls / Drop columns (Requires Admin approval)", "✓ Load saved files"],
                "Viewer": ["✓ View dataset profiles", "❌ Blocked: Visualizer custom designs", "❌ Blocked: Machine learning models", "❌ Blocked: Edit data cells / Clean fields", "❌ Blocked: Save data to account"]
            }
            
            st.markdown(f"**Permissions associated with {st.session_state.role}:**")
            for p in perms[st.session_state.role]:
                st.markdown(p)
                
        with right:
            st.subheader("Workspace Processing Metrics")
            fig = go.Figure(data=[
                go.Bar(name='Records Processed', x=['May', 'June'], y=[8500, st.session_state.global_stats["records"]]),
                go.Bar(name='Charts Made', x=['May', 'June'], y=[18, st.session_state.global_stats["charts"]])
            ])
            fig = style_plotly_fig(fig)
            st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------
    # 📁 DATA CENTER PAGE
    # ---------------------------------------------
    elif page == "📁 Data Center":
        st.markdown("""
            <div class="title-container">
                <h1 class="glowing-title">Data Center</h1>
                <p class="subtitle">Load local files, review history lists, or run comparisons between datasets.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Grid uploader
        up_c1, up_c2 = st.columns([6, 4])
        with up_c1:
            st.subheader("Upload CSV Dataset")
            uploaded_file = st.file_uploader("", type=["csv"], key="datacenter_uploader")
            if uploaded_file is not None:
                if st.session_state.file_name != uploaded_file.name:
                    try:
                        df = pd.read_csv(uploaded_file)
                        setup_active_dataset(df, uploaded_file.name)
                        st.toast("Loaded file!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load file: {e}")
                        
        with up_c2:
            st.subheader("Cloud Saved Datasets")
            saved_files = list_user_files(st.session_state.user)
            if saved_files:
                sel = st.selectbox("Load saved CSV", ["None"] + saved_files)
                if sel != "None" and st.session_state.file_name != sel:
                    file_path = os.path.join(get_user_storage_dir(st.session_state.user), sel)
                    try:
                        df = pd.read_csv(file_path)
                        st.session_state.df = df
                        st.session_state.original_df = df.copy()
                        st.session_state.file_name = sel
                        st.toast(f"Loaded {sel}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Load failed: {e}")
            else:
                st.caption("No files saved to your account yet. Use the Save option below once data is loaded.")
                
        if st.session_state.df is not None:
            # Option to save
            st.markdown("---")
            st.subheader("Save Dataset to Account")
            save_name = st.text_input("Filename", value=st.session_state.file_name or "my_dataset.csv")
            if st.session_state.role == "Viewer":
                st.warning("Viewers are not permitted to write files to account storage.")
            else:
                if st.button("💾 Save File"):
                    save_user_file(st.session_state.user, save_name, st.session_state.df)
                    st.session_state.file_name = save_name
                    st.toast("File saved successfully!")
                    st.rerun()
                    
        st.divider()
        
        # Dataset Comparison Tool
        st.subheader("⚖️ Dataset Comparison Tool")
        st.caption("Compare your active dataset side-by-side with another CSV file.")
        
        comp_file = st.file_uploader("Upload second CSV to compare", type=["csv"], key="comparison_uploader")
        if comp_file is not None and st.session_state.df is not None:
            try:
                df_b = pd.read_csv(comp_file)
                df_a = st.session_state.df
                
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.markdown(f"**Dataset A (Active):** `{st.session_state.file_name}`")
                    st.markdown(f"- Rows: **{df_a.shape[0]:,}**")
                    st.markdown(f"- Columns: **{df_a.shape[1]}**")
                with c_col2:
                    st.markdown(f"**Dataset B (Compare):** `{comp_file.name}`")
                    st.markdown(f"- Rows: **{df_b.shape[0]:,}**")
                    st.markdown(f"- Columns: **{df_b.shape[1]}**")
                    
                # Differences
                row_diff = df_b.shape[0] - df_a.shape[0]
                pct_diff = (row_diff / df_a.shape[0] * 100) if df_a.shape[0] > 0 else 0
                st.markdown(f"🔍 **Comparison Summary**: Dataset B contains **{abs(row_diff):,} ({pct_diff:+.1f}%)** {'more' if row_diff > 0 else 'fewer'} rows than Dataset A.")
                
                # Column check
                common_cols = list(set(df_a.columns).intersection(set(df_b.columns)))
                added_cols = list(set(df_b.columns) - set(df_a.columns))
                removed_cols = list(set(df_a.columns) - set(df_b.columns))
                
                st.markdown(f"• Common Columns ({len(common_cols)}): `{', '.join(common_cols[:6])}...`")
                if added_cols:
                    st.markdown(f"➕ Columns in B not in A: `{', '.join(added_cols)}`")
                if removed_cols:
                    st.markdown(f"➖ Columns in A not in B: `{', '.join(removed_cols)}`")
            except Exception as e:
                st.error(f"Comparison failed: {e}")
        elif comp_file is not None and st.session_state.df is None:
            st.warning("Please upload or select an active dataset first.")

    # ---------------------------------------------
    # 🛠️ ADVANCED CLEANER PAGE
    # ---------------------------------------------
    elif page == "🛠️ Advanced Cleaner":
        st.markdown("""
            <div class="title-container">
                <h1 class="glowing-title">Advanced Data Cleaner</h1>
                <p class="subtitle">Convert types, impute missing cells, and drop outliers with logs.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df is None:
            st.warning("Please load a dataset in the Data Center to activate cleaner tools.")
        else:
            df = st.session_state.df
            
            # Roles check
            is_viewer = (st.session_state.role == "Viewer")
            is_analyst = (st.session_state.role == "Analyst")
            
            # Live Engineering Stats Card
            est1, est2, est3 = st.columns(3)
            with est1:
                st.markdown(f'<div class="metric-card"><div class="metric-lbl">Rows Removed</div><div class="metric-val" style="color:#EF4444;">{st.session_state.clean_logs["rows_removed"]}</div></div>', unsafe_allow_html=True)
            with est2:
                st.markdown(f'<div class="metric-card"><div class="metric-lbl">Missing Values Fixed</div><div class="metric-val" style="color:#10B981;">{st.session_state.clean_logs["nulls_fixed"]}</div></div>', unsafe_allow_html=True)
            with est3:
                st.markdown(f'<div class="metric-card"><div class="metric-lbl">Columns Converted</div><div class="metric-val" style="color:#3B82F6;">{st.session_state.clean_logs["types_converted"]}</div></div>', unsafe_allow_html=True)
                
            st.divider()
            
            clean_col1, clean_col2 = st.columns(2)
            
            with clean_col1:
                st.subheader("Data Engineering Tasks")
                
                # Action 1: Type Converter
                st.markdown("##### ⚙️ Convert Column Type")
                conv_col = st.selectbox("Select Column to Convert", df.columns.tolist())
                target_type = st.selectbox("Target Data Type", ["Int", "Float", "String", "Datetime"])
                
                if is_viewer:
                    st.button("Convert Type", disabled=True, help="Viewer account is read-only.")
                else:
                    if st.button("Convert Type"):
                        try:
                            new_df = df.copy()
                            if target_type == "Int":
                                new_df[conv_col] = pd.to_numeric(new_df[conv_col], errors='coerce').fillna(0).astype(int)
                            elif target_type == "Float":
                                new_df[conv_col] = pd.to_numeric(new_df[conv_col], errors='coerce').astype(float)
                            elif target_type == "String":
                                new_df[conv_col] = new_df[conv_col].astype(str)
                            elif target_type == "Datetime":
                                new_df[conv_col] = pd.to_datetime(new_df[conv_col], errors='coerce')
                                
                            st.session_state.df = new_df
                            st.session_state.clean_logs["types_converted"] += 1
                            st.toast(f"Converted {conv_col} to {target_type}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Type conversion failed: {e}")
                            
                st.divider()
                
                # Action 2: Outlier Purge
                st.markdown("##### 🗑️ Remove IQR Outliers")
                out_col = st.selectbox("Select Numeric Column to Clean Outliers", df.select_dtypes(include=['number']).columns.tolist())
                
                if is_viewer or (is_analyst and st.session_state.role != "Admin"):
                    st.button("Purge Outliers", disabled=True, help="Only Admins are authorized to drop rows.")
                else:
                    if st.button("Purge Outliers") and out_col:
                        q1 = df[out_col].quantile(0.25)
                        q3 = df[out_col].quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        clean_df = df[(df[out_col] >= lower_bound) & (df[out_col] <= upper_bound)]
                        removed = df.shape[0] - clean_df.shape[0]
                        st.session_state.df = clean_df
                        st.session_state.clean_logs["rows_removed"] += removed
                        st.toast(f"Removed {removed} outlier records!")
                        st.rerun()
                        
            with clean_col2:
                st.subheader("Missing & Null Value Auditor")
                
                # Null statistics report
                null_counts = df.isnull().sum()
                has_nulls = null_counts[null_counts > 0]
                
                if not has_nulls.empty:
                    for col, count in has_nulls.items():
                        st.markdown(f"⚠️ **{col}**: `{count}` missing entries ({count/df.shape[0]*100:.1f}%)")
                        
                    st.markdown("---")
                    st.markdown("##### 🩹 Batch Imputation")
                    imp_col = st.selectbox("Column to Impute", has_nulls.index.tolist())
                    imp_strategy = st.selectbox("Value Strategy", ["Mean", "Median", "Mode", "Zero (0)"])
                    
                    if is_viewer:
                        st.button("Apply Imputation", disabled=True)
                    else:
                        if st.button("Apply Imputation"):
                            new_df = df.copy()
                            if imp_strategy == "Mean":
                                fill_val = df[imp_col].mean()
                            elif imp_strategy == "Median":
                                fill_val = df[imp_col].median()
                            elif imp_strategy == "Mode":
                                fill_val = df[imp_col].mode()[0]
                            else:
                                fill_val = 0
                                
                            new_df[imp_col] = new_df[imp_col].fillna(fill_val)
                            st.session_state.df = new_df
                            st.session_state.clean_logs["nulls_fixed"] += int(null_counts[imp_col])
                            st.toast(f"Imputed missing fields for {imp_col}!")
                            st.rerun()
                else:
                    st.success("Clean Audit! Zero null values detected inside active dataset.")
                    
            st.divider()
            
            # Action 3: Drop duplicates
            if not is_viewer:
                if st.button("Drop Duplicate Records"):
                    dups = df.duplicated().sum()
                    if dups > 0:
                        st.session_state.df = df.drop_duplicates()
                        st.session_state.clean_logs["rows_removed"] += int(dups)
                        st.toast("Removed duplicates!")
                        st.rerun()

    # ---------------------------------------------
    # 🎨 VISUALIZER STUDIO PAGE
    # ---------------------------------------------
    elif page == "🎨 Visualizer Studio":
        st.markdown("""
            <div class="title-container">
                <h1 class="glowing-title">Visualizer Studio</h1>
                <p class="subtitle">Design interactive charts and compose customized layouts.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df is None:
            st.warning("Please upload a dataset in the Data Center to build dashboards.")
        else:
            df = st.session_state.df
            
            # Visualizer Options
            v_col1, v_col2 = st.columns([3, 7])
            
            with v_col1:
                st.subheader("Chart Builder Options")
                
                chart_choice = st.selectbox("Chart Template", [
                    "Scatter", "Line", "Bar", "Histogram", "Box", 
                    "Correlation Matrix", "Bubble", "Treemap", "Radar"
                ])
                
                x_col = st.selectbox("X-Axis Field", df.columns.tolist())
                y_col = None
                if chart_choice not in ["Histogram", "Treemap", "Correlation Matrix"]:
                    y_col = st.selectbox("Y-Axis Field", df.columns.tolist(), index=min(1, len(df.columns)-1))
                    
                color_by = st.selectbox("Color By Category", ["None"] + df.columns.tolist())
                color_field = None if color_by == "None" else color_by
                
                size_by = None
                size_field = None
                if chart_choice in ["Scatter", "Bubble"]:
                    size_by = st.selectbox("Marker Size (Numeric)", ["None"] + df.select_dtypes(include=['number']).columns.tolist())
                    size_field = None if size_by == "None" else size_by

                chart_title = st.text_input("Chart title (optional)", placeholder=f"{chart_choice} · {x_col}")
                    
                st.markdown("---")
                
                # Active Dashboard Builder
                st.markdown("##### 📌 Grid Dashboard Builder")
                widget_width = st.selectbox("Dashboard Widget Width", ["Half-Width (50%)", "Full-Width (100%)"])
                
                if st.session_state.role == "Viewer":
                    st.button("Add to Active Dashboard", disabled=True)
                else:
                    if st.button("Add to Active Dashboard"):
                        # Save configurations
                        st.session_state.dashboards.append({
                            "type": chart_choice,
                            "x": x_col,
                            "y": y_col,
                            "color": color_field,
                            "size": size_field if 'size_field' in locals() else None,
                            "title": chart_title.strip() or None,
                            "width": widget_width
                        })
                        st.session_state.global_stats["charts"] += 1
                        st.toast("Chart pinned to active dashboard!")
                        
            with v_col2:
                st.subheader("Visualizer Output Preview")
                
                try:
                    fig = build_chart(df, {
                        "type": chart_choice, "x": x_col, "y": y_col,
                        "color": color_field, "size": size_field, "title": chart_title.strip() or None,
                    })
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True, "modeBarButtonsToAdd": ["drawline", "eraseshape"]})
                    elif chart_choice == "Correlation Matrix":
                        st.info("Correlation Matrix requires 2+ numerical columns.")
                    elif chart_choice == "Bubble":
                        st.warning("Please configure a numeric sizing variable for Bubble charts.")
                    elif chart_choice == "Radar":
                        st.warning("Radar chart requires X (category) and Y (metric) variables.")
                        
                        # Standalone exports
                    if fig:
                        buffer = io.StringIO()
                        fig.write_html(buffer, include_plotlyjs="cdn")
                        html_bytes = buffer.getvalue().encode()
                        
                        exp_c1, exp_c2 = st.columns(2)
                        with exp_c1:
                            st.download_button(
                                label="📥 Export Plotly HTML",
                                data=html_bytes,
                                file_name="plotly_custom_export.html",
                                mime="text/html"
                            )
                        with exp_c2:
                            # Excel export
                            excel_buf = io.BytesIO()
                            with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
                                df.to_excel(writer, sheet_name="Dataset", index=False)
                            excel_data = excel_buf.getvalue()
                            st.download_button(
                                label="📥 Download Dataset (Excel)",
                                data=excel_data,
                                file_name="exported_report.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                except Exception as e:
                    st.error(f"Plot construction failed: {e}")
                    
            # Render the pinned dashboard with live categorical filters.
            if st.session_state.dashboards:
                st.divider()
                st.subheader("📌 Your interactive dashboard")
                st.caption(f"{len(st.session_state.dashboards)} pinned visualizations · hover, zoom, pan, and select chart elements to explore")

                categorical_cols = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
                if categorical_cols:
                    with st.expander("Filter dashboard data", expanded=False):
                        filter_col = st.selectbox("Filter by category", ["No filter"] + categorical_cols, key="dashboard_filter_col")
                        if filter_col != "No filter":
                            values = df[filter_col].dropna().unique().tolist()
                            selected = st.multiselect("Visible values", values, default=values, key="dashboard_filter_values")
                            df = df[df[filter_col].isin(selected)]
                            st.caption(f"Showing {len(df):,} of {len(st.session_state.df):,} rows")

                if df.empty:
                    st.info("No rows match the selected filter. Choose more values to see your charts.")
                else:
                    index = 0
                    while index < len(st.session_state.dashboards):
                        current = st.session_state.dashboards[index]
                        if current["width"] == "Full-Width (100%)":
                            group = [(index, current)]
                        elif index + 1 < len(st.session_state.dashboards) and st.session_state.dashboards[index + 1]["width"] == "Half-Width (50%)":
                            group = [(index, current), (index + 1, st.session_state.dashboards[index + 1])]
                        else:
                            group = [(index, current)]
                        columns = st.columns(len(group))
                        for col, (widget_index, card) in zip(columns, group):
                            with col:
                                with st.container(border=True):
                                    st.markdown(f"**{widget_index + 1:02d} · {card['type']}**")
                                    try:
                                        chart = build_chart(df, card)
                                        if chart is not None:
                                            st.plotly_chart(chart, use_container_width=True, key=f"dashboard_chart_{widget_index}", config={"displaylogo": False, "scrollZoom": True, "modeBarButtonsToAdd": ["drawline", "eraseshape"]})
                                        else:
                                            st.info("This chart needs more numeric columns or a size field.")
                                    except Exception as error:
                                        st.caption(f"Unable to draw this chart: {error}")
                                    if st.button("Remove from dashboard", key=f"del_{widget_index}"):
                                        st.session_state.dashboards.pop(widget_index)
                                        st.rerun()
                        index += len(group)

                if st.button("Clear dashboard", type="secondary", key="clear_dashboard"):
                    st.session_state.dashboards.clear()
                    st.rerun()

    # 🧠 AI ANALYTICS DESK PAGE
    # ---------------------------------------------
    elif page == "🧠 AI Analytics Desk":
        st.markdown("""
            <div class="title-container">
                <h1 class="glowing-title">AI Analytics Desk</h1>
                <p class="subtitle">Chat with your active dataset and review automated statistical reports.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df is None:
            st.warning("Please upload a CSV dataset to activate the AI Analytics tools.")
        else:
            df = st.session_state.df
            
            ai_col1, ai_col2 = st.columns([4, 6])
            
            with ai_col1:
                st.subheader("💡 Automated EDA Summary")
                
                # 5 Point Summary
                st.markdown("**1. Dimensional Check**")
                st.markdown(f"The active dataset contains **{df.shape[0]:,}** rows and **{df.shape[1]}** features.")
                
                st.markdown("**2. Quality Metric**")
                nulls = df.isnull().sum().sum()
                if nulls > 0:
                    st.markdown(f"⚠️ Out of {df.size} cells, {nulls} are missing. We suggest running cleaner imputation.")
                else:
                    st.markdown("✅ No missing entries. The dataset maintains clean cell structures.")
                    
                st.markdown("**3. Prominent Outlier Flags**")
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                outlier_flags = []
                for col in numeric_cols:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    cnt = df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)].shape[0]
                    if cnt > 0:
                        outlier_flags.append(f"• `{col}`: {cnt} cells")
                if outlier_flags:
                    st.markdown("\n".join(outlier_flags[:3]))
                else:
                    st.markdown("✅ Low outlier frequencies across numerical variables.")
                    
                st.markdown("**4. Feature Recommendations**")
                recs = []
                cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                if cat_cols and numeric_cols:
                    recs.append(f"• Use a **Bar chart** mapping Category `{cat_cols[0]}` against `{numeric_cols[0]}`.")
                if len(numeric_cols) >= 2:
                    recs.append(f"• Build a **Scatter plot** comparing `{numeric_cols[0]}` and `{numeric_cols[1]}`.")
                if recs:
                    st.markdown("\n".join(recs))
                    
                st.markdown("**5. Correlation Trends**")
                if len(numeric_cols) >= 2:
                    corr = df[numeric_cols].corr()
                    strongest = None
                    max_val = 0
                    for i in range(len(numeric_cols)):
                        for j in range(i+1, len(numeric_cols)):
                            v = abs(corr.iloc[i, j])
                            if v > max_val:
                                max_val = v
                                strongest = (numeric_cols[i], numeric_cols[j], corr.iloc[i, j])
                    if strongest:
                        st.markdown(f"Linear association is highest between `{strongest[0]}` and `{strongest[1]}` (r = {strongest[2]:.2f}).")
                else:
                    st.markdown("Not enough numerical columns to measure correlations.")

            with ai_col2:
                st.subheader("💬 Chat with Data")
                st.caption("Ask questions in natural language. Examples: 'average [numeric_column]', 'maximum [column]', 'show total rows'.")
                
                query_input = st.text_input("Enter query:", placeholder="e.g. average Age")
                
                if query_input:
                    q_lower = query_input.lower()
                    answered = False
                    
                    # Search matching columns
                    target_col = None
                    for c in df.columns:
                        if c.lower() in q_lower:
                            target_col = c
                            break
                            
                    # Keyword matching parsing
                    if "average" in q_lower or "mean" in q_lower:
                        if target_col and df[target_col].dtype in ['int64', 'float64']:
                            mean_val = df[target_col].mean()
                            st.markdown(f"✨ **AI Analytics**: The average/mean value for column **{target_col}** is **{mean_val:,.2f}**.")
                            
                            # Render matching plot
                            fig = px.histogram(df, x=target_col, title=f"Distribution of {target_col} with Mean indicator")
                            fig.add_vline(x=mean_val, line_dash="dash", line_color="red", annotation_text="Mean")
                            fig = style_plotly_fig(fig)
                            st.plotly_chart(fig, use_container_width=True)
                            answered = True
                        else:
                            st.warning("Please specify a numeric column name to calculate average (e.g. 'average Sales').")
                            
                    elif "maximum" in q_lower or "max" in q_lower:
                        if target_col:
                            max_val = df[target_col].max()
                            st.markdown(f"✨ **AI Analytics**: The maximum value in column **{target_col}** is **{max_val}**.")
                            answered = True
                            
                    elif "minimum" in q_lower or "min" in q_lower:
                        if target_col:
                            min_val = df[target_col].min()
                            st.markdown(f"✨ **AI Analytics**: The minimum value in column **{target_col}** is **{min_val}**.")
                            answered = True
                            
                    elif "total rows" in q_lower or "count" in q_lower:
                        st.markdown(f"✨ **AI Analytics**: There are **{df.shape[0]:,}** total rows inside this dataset.")
                        answered = True
                        
                    if not answered:
                        st.info("Query compiler did not match keywords. Try querying: 'average [numeric column]', 'maximum [column]', or 'total rows'.")

    # ---------------------------------------------
    # 🔮 PREDICTIVE ML SANDBOX PAGE
    # ---------------------------------------------
    elif page == "🔮 Predictive ML Sandbox":
        st.markdown("""
            <div class="title-container">
                <h1 class="glowing-title">Predictive ML Sandbox</h1>
                <p class="subtitle">Train linear regression trend lines, forecast future periods, and build K-Means clusters.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df is None:
            st.warning("Please upload a CSV dataset to activate the Predictive ML Sandbox.")
        else:
            df = st.session_state.df
            
            # Roles check
            if st.session_state.role == "Viewer":
                st.warning("Viewer profile is not authorized to train machine learning models.")
            else:
                ml_task = st.radio("Choose ML Model", ["Linear Regression", "Time-Series Forecasting", "K-Means Clustering"], horizontal=True)
                
                st.divider()
                
                # 1. Regression
                if ml_task == "Linear Regression":
                    st.subheader("Linear Regression Fitting")
                    st.caption("Pick a predictor variable (X) to estimate a numerical target variable (Y).")
                    
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) < 2:
                        st.warning("Regression model requires at least 2 numeric columns.")
                    else:
                        reg_x = st.selectbox("Predictor (X-Axis)", numeric_cols, index=0)
                        reg_y = st.selectbox("Target Target (Y-Axis)", numeric_cols, index=min(1, len(numeric_cols)-1))
                        
                        if reg_x == reg_y:
                            st.warning("Please select distinct variables for X and Y.")
                        else:
                            # Drop NaNs for training
                            reg_df = df[[reg_x, reg_y]].dropna()
                            
                            X_arr = reg_df[[reg_x]].values
                            y_arr = reg_df[reg_y].values
                            
                            # Fit Scikit Learn Regression model
                            model = LinearRegression()
                            model.fit(X_arr, y_arr)
                            
                            y_pred = model.predict(X_arr)
                            r2 = model.score(X_arr, y_arr)
                            
                            # Layout results
                            res_c1, res_c2 = st.columns([4, 6])
                            with res_c1:
                                st.markdown("##### 📈 Model Metrics")
                                st.markdown(f"- R² Coefficient of Determination: **{r2:.4f}**")
                                st.markdown(f"- Fitted Equation: $Y = {model.coef_[0]:.4f}X + {model.intercept_:.2f}$")
                                st.caption("R-squared scores closer to 1.0 indicate a strong model fit.")
                            with res_c2:
                                # Plot scatter with fitted regression line
                                fig = px.scatter(reg_df, x=reg_x, y=reg_y, title=f"Regression Model: {reg_y} vs {reg_x}")
                                fig.add_trace(go.Scatter(x=reg_df[reg_x], y=y_pred, name="Trend Line", line=dict(color="red", width=2)))
                                fig = style_plotly_fig(fig)
                                st.plotly_chart(fig, use_container_width=True)
                                
                # 2. Time-Series Forecasting
                elif ml_task == "Time-Series Forecasting":
                    st.subheader("Time-Series Linear Trend Forecasting")
                    st.caption("Select a chronological/numerical index column and fit a linear trend to forecast future steps.")
                    
                    idx_cols = df.columns.tolist()
                    val_cols = df.select_dtypes(include=['number']).columns.tolist()
                    
                    forecast_idx = st.selectbox("Timeline Column (X)", idx_cols)
                    forecast_val = st.selectbox("Metric Column (Y)", val_cols)
                    
                    steps = st.slider("Future Steps to Forecast", 5, 30, 10)
                    
                    if forecast_idx and forecast_val:
                        try:
                            # Sort by index and clean NaNs
                            f_df = df[[forecast_idx, forecast_val]].dropna()
                            
                            # Create mock numeric indexing if it is a date/string
                            f_df['mock_idx'] = np.arange(len(f_df))
                            
                            X_arr = f_df[['mock_idx']].values
                            y_arr = f_df[forecast_val].values
                            
                            # Fit model
                            model = LinearRegression()
                            model.fit(X_arr, y_arr)
                            
                            # Future mock steps
                            future_idx = np.arange(len(f_df), len(f_df) + steps).reshape(-1, 1)
                            future_preds = model.predict(future_idx)
                            
                            # Timeline trace data
                            timeline_x = f_df[forecast_idx].tolist()
                            future_timeline = [f"Step +{i+1}" for i in range(steps)]
                            
                            fig = go.Figure()
                            # Historical values
                            fig.add_trace(go.Scatter(x=timeline_x, y=y_arr, name="Historical", mode="lines+markers"))
                            # Forecasted values
                            fig.add_trace(go.Scatter(x=future_timeline, y=future_preds, name="Forecast", mode="lines+markers", line=dict(dash="dash", color="green")))
                            
                            fig = style_plotly_fig(fig)
                            fig.update_layout(title=f"Forecasting Future Periods for {forecast_val}")
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Forecasting engine error: {e}")
                            
                # 3. K-Means Clustering
                elif ml_task == "K-Means Clustering":
                    st.subheader("K-Means Cluster Visualizer")
                    st.caption("Apply unsupervised K-Means clustering to separate numerical columns into distinct groupings.")
                    
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) < 2:
                        st.warning("Clustering visualizer requires 2+ numeric columns.")
                    else:
                        cluster_x = st.selectbox("Column A (X)", numeric_cols, index=0)
                        cluster_y = st.selectbox("Column B (Y)", numeric_cols, index=min(1, len(numeric_cols)-1))
                        
                        k_val = st.slider("Number of Clusters (K)", 2, 5, 3)
                        
                        if cluster_x and cluster_y:
                            try:
                                # Filter
                                c_df = df[[cluster_x, cluster_y]].dropna()
                                
                                kmeans = KMeans(n_clusters=k_val, random_state=42)
                                c_df['Cluster'] = kmeans.fit_predict(c_df.values)
                                c_df['Cluster'] = c_df['Cluster'].astype(str) # category conversion for plotting
                                
                                fig = px.scatter(c_df, x=cluster_x, y=cluster_y, color='Cluster', title=f"K-Means Clustering: K={k_val}")
                                fig = style_plotly_fig(fig)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Cluster model error: {e}")
