"""
Customer De-duping Workflow - Streamlit in Snowflake (SiS)
Tower Insurance NZ - Duplicate Customer Management System

This app allows customer service agents to:
- Review potential duplicate customer records
- Compare records side-by-side
- Make match/no-match decisions
- Track all decisions with full audit trail
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, count, when, lit, current_timestamp
from datetime import datetime
import uuid

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Tower Insurance | Customer De-duping Workflow",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS - Tower Insurance NZ Corporate Branding
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Tower Insurance NZ Corporate Colors - From Official Logo */
    :root {
        --tower-navy: #0d1b4c;
        --tower-navy-dark: #080f2d;
        --tower-navy-light: #1a2d6b;
        --tower-yellow: #FFD700;
        --tower-yellow-dark: #E6C200;
        --tower-yellow-light: #FFE44D;
        --tower-white: #ffffff;
        --tower-gray-50: #f8fafc;
        --tower-gray-100: #f1f5f9;
        --tower-gray-200: #e2e8f0;
        --tower-gray-400: #94a3b8;
        --tower-gray-600: #475569;
        --tower-gray-800: #1e293b;
        --success-color: #22c55e;
        --warning-color: #eab308;
        --danger-color: #ef4444;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Tower Header styling - Deep Navy with Yellow Accent */
    .main-header {
        background: linear-gradient(135deg, var(--tower-navy-dark) 0%, var(--tower-navy) 50%, var(--tower-navy-light) 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(13, 27, 76, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -5%;
        width: 200px;
        height: 200%;
        background: radial-gradient(ellipse at center, rgba(255, 215, 0, 0.15) 0%, transparent 70%);
        transform: rotate(-15deg);
    }
    
    .main-header h1 {
        color: var(--tower-white);
        margin: 0;
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header h1::before {
        content: '🏢';
        font-size: 1.5rem;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    
    .tower-logo {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--tower-yellow);
        color: var(--tower-navy);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    
    /* Metric cards - Tower branded */
    .metric-card {
        background: linear-gradient(145deg, var(--tower-white) 0%, var(--tower-gray-50) 100%);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(13, 27, 76, 0.1);
        border-left: 4px solid var(--tower-navy);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(13, 27, 76, 0.15);
        border-left-color: var(--tower-yellow);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--tower-navy);
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--tower-gray-600);
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    /* Customer comparison cards - Tower branded */
    .customer-card {
        background: var(--tower-white);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(13, 27, 76, 0.1);
        border-top: 4px solid var(--tower-navy);
        height: 100%;
    }
    
    .customer-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--tower-gray-200);
    }
    
    .customer-id {
        font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
        background: linear-gradient(135deg, var(--tower-navy) 0%, var(--tower-navy-light) 100%);
        color: var(--tower-white);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .field-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--tower-gray-100);
    }
    
    .field-label {
        flex: 0 0 35%;
        color: var(--tower-gray-600);
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .field-value {
        flex: 1;
        color: var(--tower-gray-800);
        font-size: 0.9rem;
    }
    
    .field-match {
        background: rgba(34, 197, 94, 0.15);
        border-radius: 4px;
        padding: 0 4px;
    }
    
    .field-diff {
        background: rgba(239, 68, 68, 0.15);
        border-radius: 4px;
        padding: 0 4px;
    }
    
    /* Match score badges - Tower themed with proper contrast */
    .match-score-high {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        display: inline-block;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .match-score-medium {
        background: linear-gradient(135deg, var(--tower-yellow) 0%, var(--tower-yellow-dark) 100%);
        color: var(--tower-navy);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
    }
    
    .match-score-low {
        background: linear-gradient(135deg, var(--tower-navy) 0%, var(--tower-navy-dark) 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        display: inline-block;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Priority badges */
    .priority-high {
        background: #fee2e2;
        color: #dc2626;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .priority-medium {
        background: #fef9c3;
        color: #a16207;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .priority-low {
        background: #e0f2fe;
        color: var(--tower-navy);
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Action buttons - Tower branded with proper contrast */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--tower-navy) 0%, var(--tower-navy-dark) 100%);
        border: none;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--tower-navy-light) 0%, var(--tower-navy) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(13, 27, 76, 0.3);
    }
    
    /* Decision panel */
    .decision-panel {
        background: linear-gradient(145deg, var(--tower-gray-50) 0%, var(--tower-gray-100) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 2px solid var(--tower-gray-200);
    }
    
    /* Info callout - Tower branded */
    .info-callout {
        background: linear-gradient(135deg, rgba(13, 27, 76, 0.05) 0%, rgba(13, 27, 76, 0.1) 100%);
        border-left: 4px solid var(--tower-navy);
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-pending {
        background: #fef9c3;
        color: #a16207;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-matched {
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-not-matched {
        background: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Sidebar styling - Tower branded with light text on dark navy */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--tower-navy) 0%, var(--tower-navy-dark) 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--tower-yellow) !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput label {
        color: var(--tower-yellow) !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 215, 0, 0.3);
        color: white;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label {
        color: var(--tower-yellow) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 215, 0, 0.15);
        border: 1px solid rgba(255, 215, 0, 0.4);
        color: white;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 215, 0, 0.25);
        border-color: var(--tower-yellow);
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: var(--tower-yellow);
        color: var(--tower-navy);
        border: none;
        font-weight: 700;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: var(--tower-yellow-light);
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 215, 0, 0.3);
    }
    
    section[data-testid="stSidebar"] .stMetric label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: var(--tower-yellow) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Table styling */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* DataEditor/DataFrame styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Initialize Session
# =============================================================================
@st.cache_resource
def get_session():
    return get_active_session()

session = get_session()

# =============================================================================
# Helper Functions
# =============================================================================

def get_dashboard_metrics():
    """Get summary metrics for the dashboard."""
    query = """
    SELECT 
        COUNT(*) as total_candidates,
        SUM(CASE WHEN STATUS = 'PENDING' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN STATUS = 'MATCHED' THEN 1 ELSE 0 END) as matched,
        SUM(CASE WHEN STATUS = 'NOT_MATCHED' THEN 1 ELSE 0 END) as not_matched,
        SUM(CASE WHEN PRIORITY = 'HIGH' AND STATUS = 'PENDING' THEN 1 ELSE 0 END) as high_priority_pending,
        AVG(MATCH_SCORE) as avg_match_score
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES
    """
    return session.sql(query).collect()[0]

def get_pending_candidates(priority_filter=None, sort_by='MATCH_SCORE'):
    """Get list of pending duplicate candidates."""
    query = """
    SELECT 
        dc.CANDIDATE_ID,
        dc.CUSTOMER_ID_1,
        dc.CUSTOMER_ID_2,
        dc.MATCH_SCORE,
        dc.MATCH_REASON,
        dc.PRIORITY,
        dc.CREATED_DATE,
        c1.FIRST_NAME || ' ' || c1.LAST_NAME as NAME_1,
        c2.FIRST_NAME || ' ' || c2.LAST_NAME as NAME_2
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES dc
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c1 ON dc.CUSTOMER_ID_1 = c1.CUSTOMER_ID
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c2 ON dc.CUSTOMER_ID_2 = c2.CUSTOMER_ID
    WHERE dc.STATUS = 'PENDING'
    """
    if priority_filter:
        query += f" AND dc.PRIORITY = '{priority_filter}'"
    
    query += f" ORDER BY dc.{sort_by} DESC"
    
    return session.sql(query).to_pandas()

def get_customer_details(customer_id):
    """Get full customer details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS 
    WHERE CUSTOMER_ID = '{customer_id}'
    """
    result = session.sql(query).collect()
    return result[0] if result else None

def get_candidate_details(candidate_id):
    """Get duplicate candidate details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    WHERE CANDIDATE_ID = '{candidate_id}'
    """
    result = session.sql(query).collect()
    return result[0] if result else None

def record_decision(candidate_id, agent_name, decision, reason, notes):
    """Record agent's decision and update candidate status."""
    decision_id = str(uuid.uuid4())[:36]
    session_id = st.session_state.get('session_id', str(uuid.uuid4())[:36])
    
    # Insert decision record
    insert_query = f"""
    INSERT INTO DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS 
    (DECISION_ID, CANDIDATE_ID, AGENT_NAME, DECISION, DECISION_REASON, NOTES, SESSION_ID)
    VALUES ('{decision_id}', '{candidate_id}', '{agent_name}', '{decision}', '{reason}', '{notes}', '{session_id}')
    """
    session.sql(insert_query).collect()
    
    # Update candidate status
    update_query = f"""
    UPDATE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    SET STATUS = '{decision}', ASSIGNED_TO = '{agent_name}'
    WHERE CANDIDATE_ID = '{candidate_id}'
    """
    session.sql(update_query).collect()
    
    return decision_id

def get_decision_history(limit=50):
    """Get recent decision history."""
    query = f"""
    SELECT 
        ad.DECISION_TIMESTAMP,
        ad.AGENT_NAME,
        ad.DECISION,
        ad.DECISION_REASON,
        ad.NOTES,
        dc.CUSTOMER_ID_1,
        dc.CUSTOMER_ID_2,
        dc.MATCH_SCORE
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS ad
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES dc ON ad.CANDIDATE_ID = dc.CANDIDATE_ID
    ORDER BY ad.DECISION_TIMESTAMP DESC
    LIMIT {limit}
    """
    return session.sql(query).to_pandas()

def highlight_differences(val1, val2):
    """Return CSS class based on whether values match."""
    if val1 is None or val2 is None:
        return 'field-diff' if val1 != val2 else ''
    return 'field-match' if str(val1).strip().lower() == str(val2).strip().lower() else 'field-diff'

# =============================================================================
# Initialize Session State
# =============================================================================
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:36]
if 'selected_candidate' not in st.session_state:
    st.session_state.selected_candidate = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'

# =============================================================================
# Tower Logo SVG (Based on official logo: navy bg, yellow curve, white tower)
# =============================================================================
TOWER_LOGO_SVG = '''
<svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" rx="18" fill="#0d1b4c"/>
  <ellipse cx="50" cy="35" rx="35" ry="25" fill="#FFD700" transform="rotate(-15 50 35)"/>
  <path d="M50 25 L50 75 M42 75 L58 75 M44 35 L56 35 M46 45 L54 45 M45 55 L55 55 M48 25 L52 25 L52 20 L50 15 L48 20 Z" 
        stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="50" cy="30" r="4" fill="white"/>
</svg>
'''

# =============================================================================
# Sidebar Navigation - Tower Branded with Logo
# =============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <div style="display: inline-block; margin-bottom: 0.5rem;">
            {TOWER_LOGO_SVG}
        </div>
        <div style="color: #FFD700; font-size: 1.1rem; font-weight: 700; margin-top: 0.5rem;">
            TOWER
        </div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; margin-top: 0.25rem;">
            Customer De-duping
        </div>
        <div style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin-top: 0.25rem;">
            Pacific Islands Region
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Agent identification
    agent_name = st.text_input("👤 Agent Name", value="Demo Agent", key="agent_name")
    
    st.markdown("---")
    
    # Navigation with highlighted selection
    st.markdown('<p style="color: #FFD700; font-weight: 600; margin-bottom: 0.5rem;">Navigation</p>', unsafe_allow_html=True)
    
    # Dashboard button
    is_dashboard = st.session_state.current_view == 'dashboard'
    if is_dashboard:
        st.markdown('''<div style="background: #FFD700; color: #0d1b4c; padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 0.5rem; text-align: center;">📊 Dashboard</div>''', unsafe_allow_html=True)
    else:
        if st.button("📊 Dashboard", use_container_width=True, type="secondary", key="nav_dashboard"):
            st.session_state.current_view = 'dashboard'
            st.rerun()
    
    # Work Queue button
    is_work_queue = st.session_state.current_view == 'work_queue'
    if is_work_queue:
        st.markdown('''<div style="background: #FFD700; color: #0d1b4c; padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 0.5rem; text-align: center;">📋 Work Queue</div>''', unsafe_allow_html=True)
    else:
        if st.button("📋 Work Queue", use_container_width=True, type="secondary", key="nav_work_queue"):
            st.session_state.current_view = 'work_queue'
            st.rerun()
    
    # Review Records button
    is_review = st.session_state.current_view == 'review'
    if is_review:
        st.markdown('''<div style="background: #FFD700; color: #0d1b4c; padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 0.5rem; text-align: center;">🔍 Review Records</div>''', unsafe_allow_html=True)
    else:
        if st.button("🔍 Review Records", use_container_width=True, type="secondary", key="nav_review"):
            st.session_state.current_view = 'review'
            st.rerun()
    
    # Decision History button
    is_history = st.session_state.current_view == 'history'
    if is_history:
        st.markdown('''<div style="background: #FFD700; color: #0d1b4c; padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 0.5rem; text-align: center;">📜 Decision History</div>''', unsafe_allow_html=True)
    else:
        if st.button("📜 Decision History", use_container_width=True, type="secondary", key="nav_history"):
            st.session_state.current_view = 'history'
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    
    try:
        metrics = get_dashboard_metrics()
        st.metric("Pending Reviews", int(metrics['PENDING']))
        st.metric("High Priority", int(metrics['HIGH_PRIORITY_PENDING']))
    except Exception as e:
        st.warning("Connect to Snowflake to see stats")

# =============================================================================
# Main Content Area
# =============================================================================

# Header Logo SVG (smaller version for header)
TOWER_LOGO_SMALL = '''
<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" rx="18" fill="#0d1b4c"/>
  <ellipse cx="50" cy="35" rx="35" ry="25" fill="#FFD700" transform="rotate(-15 50 35)"/>
  <path d="M50 25 L50 75 M42 75 L58 75 M44 35 L56 35 M46 45 L54 45 M45 55 L55 55 M48 25 L52 25 L52 20 L50 15 L48 20 Z" 
        stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="50" cy="30" r="4" fill="white"/>
</svg>
'''

# Header - Tower Branded with Logo
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="flex-shrink: 0;">
                {TOWER_LOGO_SMALL}
            </div>
            <div>
                <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">
                    Customer De-duping Workflow
                </h1>
                <p style="color: rgba(255,255,255,0.85); margin: 0.25rem 0 0 0; font-size: 0.9rem;">Review and verify potential duplicate customer records</p>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="color: rgba(255,255,255,0.7); font-size: 0.8rem;">Environment</div>
            <div style="font-weight: 600; color: #FFD700; font-size: 0.9rem;">Customer Deduping | NZ</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# Dashboard View
# =============================================================================
if st.session_state.current_view == 'dashboard':
    st.markdown("## 📊 Dashboard Overview")
    
    try:
        metrics = get_dashboard_metrics()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(metrics['PENDING'])}</div>
                <div class="metric-label">Pending Review</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(metrics['HIGH_PRIORITY_PENDING'])}</div>
                <div class="metric-label">High Priority</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(metrics['MATCHED'])}</div>
                <div class="metric-label">Confirmed Matches</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{int(metrics['NOT_MATCHED'])}</div>
                <div class="metric-label">Not Matched</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Start High Priority Review", use_container_width=True, type="primary"):
                pending = get_pending_candidates(priority_filter='HIGH')
                if len(pending) > 0:
                    st.session_state.selected_candidate = pending.iloc[0]['CANDIDATE_ID']
                    st.session_state.current_view = 'review'
                    st.rerun()
                else:
                    st.info("No high priority items pending")
        
        with col2:
            if st.button("📋 View All Pending", use_container_width=True):
                st.session_state.current_view = 'work_queue'
                st.rerun()
        
        with col3:
            if st.button("📜 View History", use_container_width=True):
                st.session_state.current_view = 'history'
                st.rerun()
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        history = get_decision_history(limit=5)
        if len(history) > 0:
            for _, row in history.iterrows():
                status_class = 'status-matched' if row['DECISION'] == 'MATCHED' else 'status-not-matched'
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {'#2ecc71' if row['DECISION'] == 'MATCHED' else '#e74c3c'};">
                    <strong>{row['AGENT_NAME']}</strong> marked <code>{row['CUSTOMER_ID_1']}</code> ↔ <code>{row['CUSTOMER_ID_2']}</code> as 
                    <span class="{status_class}">{row['DECISION']}</span>
                    <br><small style="color: #666;">Score: {row['MATCH_SCORE']}% • {row['DECISION_TIMESTAMP']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent decisions recorded")
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Please ensure you're connected to Snowflake and the database is set up correctly.")

# =============================================================================
# Work Queue View
# =============================================================================
elif st.session_state.current_view == 'work_queue':
    st.markdown("## 📋 Work Queue")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=[None, 'HIGH', 'MEDIUM', 'LOW'],
            format_func=lambda x: 'All Priorities' if x is None else x
        )
    
    try:
        pending = get_pending_candidates(priority_filter=priority_filter)
        
        if len(pending) > 0:
            st.markdown(f"**{len(pending)} records pending review**")
            
            for _, row in pending.iterrows():
                priority_class = f"priority-{row['PRIORITY'].lower()}"
                score = row['MATCH_SCORE']
                score_class = 'match-score-high' if score >= 85 else ('match-score-medium' if score >= 70 else 'match-score-low')
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **{row['NAME_1']}** ↔ **{row['NAME_2']}**  
                        <small><code>{row['CUSTOMER_ID_1']}</code> vs <code>{row['CUSTOMER_ID_2']}</code></small>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<small>{row['MATCH_REASON'][:60]}...</small>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <span class="{score_class}">{score}%</span>
                        <span class="{priority_class}">{row['PRIORITY']}</span>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("Review →", key=f"review_{row['CANDIDATE_ID']}"):
                            st.session_state.selected_candidate = row['CANDIDATE_ID']
                            st.session_state.current_view = 'review'
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.success("🎉 All caught up! No pending items to review.")
            
    except Exception as e:
        st.error(f"Error loading work queue: {str(e)}")

# =============================================================================
# Review View - Side-by-Side Comparison
# =============================================================================
elif st.session_state.current_view == 'review':
    st.markdown("## 🔍 Record Comparison")
    
    # Get candidate to review
    if st.session_state.selected_candidate is None:
        try:
            pending = get_pending_candidates()
            if len(pending) > 0:
                st.session_state.selected_candidate = pending.iloc[0]['CANDIDATE_ID']
            else:
                st.success("🎉 All caught up! No pending items to review.")
                st.stop()
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()
    
    try:
        candidate = get_candidate_details(st.session_state.selected_candidate)
        
        if candidate is None:
            st.warning("Candidate not found. Please select from the work queue.")
            st.session_state.selected_candidate = None
            st.stop()
        
        customer1 = get_customer_details(candidate['CUSTOMER_ID_1'])
        customer2 = get_customer_details(candidate['CUSTOMER_ID_2'])
        
        # Match score header
        score = candidate['MATCH_SCORE']
        score_class = 'match-score-high' if score >= 85 else ('match-score-medium' if score >= 70 else 'match-score-low')
        priority_class = f"priority-{candidate['PRIORITY'].lower()}"
        
        st.markdown(f"""
        <div class="info-callout">
            <strong>Match Analysis</strong>: {candidate['MATCH_REASON']}
            <br><br>
            <span class="{score_class}">Match Score: {score}%</span>
            &nbsp;&nbsp;
            <span class="{priority_class}">{candidate['PRIORITY']} Priority</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        
        # Define fields to compare
        compare_fields = [
            ('CUSTOMER_ID', 'Customer ID'),
            ('FIRST_NAME', 'First Name'),
            ('LAST_NAME', 'Last Name'),
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('DATE_OF_BIRTH', 'Date of Birth'),
            ('ADDRESS_LINE1', 'Address Line 1'),
            ('ADDRESS_LINE2', 'Address Line 2'),
            ('CITY', 'City'),
            ('POSTAL_CODE', 'Postal Code'),
            ('ACCOUNT_STATUS', 'Account Status'),
            ('ACCOUNT_TYPE', 'Account Type'),
            ('SOURCE_SYSTEM', 'Source System'),
            ('CREATED_DATE', 'Created Date'),
            ('TOTAL_TRANSACTIONS', 'Total Transactions'),
            ('ACCOUNT_BALANCE', 'Account Balance'),
        ]
        
        def render_customer_card(customer, card_title, col):
            with col:
                st.markdown(f"""
                <div class="customer-card">
                    <div class="customer-card-header">
                        <h3 style="margin:0; color: #0d4f4f;">{card_title}</h3>
                        <span class="customer-id">{customer['CUSTOMER_ID']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for field_key, field_label in compare_fields:
                    val1 = customer1[field_key]
                    val2 = customer2[field_key]
                    current_val = customer[field_key]
                    
                    # Check if values match
                    match_indicator = "✅" if str(val1) == str(val2) else "⚠️"
                    
                    st.markdown(f"**{field_label}** {match_indicator}")
                    st.text(str(current_val) if current_val else "—")
        
        render_customer_card(customer1, "Record A", col1)
        render_customer_card(customer2, "Record B", col2)
        
        # Decision Panel
        st.markdown("---")
        st.markdown("### 📝 Make Decision")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                decision_reason = st.selectbox(
                    "Decision Reason",
                    options=[
                        "Same person - confirmed match",
                        "Different people - name coincidence", 
                        "Different people - family members",
                        "Insufficient information to decide",
                        "Data quality issue - needs investigation",
                        "Other (specify in notes)"
                    ]
                )
                
                notes = st.text_area("Additional Notes", placeholder="Add any relevant notes about this decision...")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("✅ MATCH - Same Person", use_container_width=True, type="primary"):
                    record_decision(
                        st.session_state.selected_candidate,
                        agent_name,
                        'MATCHED',
                        decision_reason,
                        notes
                    )
                    st.success("Decision recorded: MATCHED")
                    st.session_state.selected_candidate = None
                    st.rerun()
                
                if st.button("❌ NOT MATCH - Different People", use_container_width=True):
                    record_decision(
                        st.session_state.selected_candidate,
                        agent_name,
                        'NOT_MATCHED',
                        decision_reason,
                        notes
                    )
                    st.success("Decision recorded: NOT MATCHED")
                    st.session_state.selected_candidate = None
                    st.rerun()
                
                if st.button("⏭️ Skip for Now", use_container_width=True):
                    st.session_state.selected_candidate = None
                    st.rerun()
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← Back to Work Queue", use_container_width=True):
                st.session_state.current_view = 'work_queue'
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading record details: {str(e)}")
        st.session_state.selected_candidate = None

# =============================================================================
# Decision History View
# =============================================================================
elif st.session_state.current_view == 'history':
    st.markdown("## 📜 Decision History")
    
    try:
        history = get_decision_history(limit=100)
        
        if len(history) > 0:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                matched_count = len(history[history['DECISION'] == 'MATCHED'])
                st.metric("Total Matched", matched_count)
            with col2:
                not_matched_count = len(history[history['DECISION'] == 'NOT_MATCHED'])
                st.metric("Total Not Matched", not_matched_count)
            with col3:
                st.metric("Total Decisions", len(history))
            
            st.markdown("---")
            
            # Display as table
            st.dataframe(
                history[['DECISION_TIMESTAMP', 'AGENT_NAME', 'CUSTOMER_ID_1', 'CUSTOMER_ID_2', 'MATCH_SCORE', 'DECISION', 'DECISION_REASON']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'DECISION_TIMESTAMP': st.column_config.DatetimeColumn('Timestamp', format='YYYY-MM-DD HH:mm'),
                    'AGENT_NAME': 'Agent',
                    'CUSTOMER_ID_1': 'Customer 1',
                    'CUSTOMER_ID_2': 'Customer 2',
                    'MATCH_SCORE': st.column_config.NumberColumn('Score', format='%.1f%%'),
                    'DECISION': 'Decision',
                    'DECISION_REASON': 'Reason'
                }
            )
        else:
            st.info("No decisions recorded yet.")
            
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")

# Footer Logo SVG (tiny version)
TOWER_LOGO_TINY = '''
<svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" rx="18" fill="#0d1b4c"/>
  <ellipse cx="50" cy="35" rx="35" ry="25" fill="#FFD700" transform="rotate(-15 50 35)"/>
  <path d="M50 25 L50 75 M42 75 L58 75 M44 35 L56 35 M46 45 L54 45 M45 55 L55 55 M48 25 L52 25 L52 20 L50 15 L48 20 Z" 
        stroke="white" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''

# =============================================================================
# Footer - Tower Branded with Logo
# =============================================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem;">
    <div style="display: inline-flex; align-items: center; gap: 0.5rem;">
        {TOWER_LOGO_TINY}
        <span style="font-weight: 600; color: #0d1b4c;">TOWER</span>
        <span>Customer De-duping Workflow</span>
        <span>•</span>
        <span>Powered by Snowflake</span>
        <span>•</span>
        <span>Session: {st.session_state.session_id[:8]}</span>
    </div>
</div>
""", unsafe_allow_html=True)
