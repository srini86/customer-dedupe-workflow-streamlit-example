"""
Customer De-duping Workflow - Streamlit in Snowflake (SiS)
Tower Insurance NZ - Pacific Islands Customer Duplicate Management System

This app allows agents to:
- Review clustered duplicate candidates by country
- Compare customer records side-by-side
- Confirm or reject matches
- Track all decisions with full audit trail
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta
import uuid

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Tower Insurance | Customer De-duping Workflow",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# Custom CSS - Tower Insurance NZ Corporate Branding (From Official Logo)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Tower Insurance NZ Corporate Colors - From Official Logo */
    :root {
        --tower-navy: #0d1b4c;
        --tower-navy-dark: #080f2d;
        --tower-navy-light: #1a2d6b;
        --tower-yellow: #FFD700;
        --tower-yellow-dark: #E6C200;
        --tower-yellow-light: #FFE44D;
        --white: #ffffff;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-400: #94a3b8;
        --gray-600: #475569;
        --gray-800: #1e293b;
        --success: #22c55e;
        --warning: #eab308;
        --danger: #ef4444;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Top header bar - Tower branded with deep navy */
    .top-header {
        background: linear-gradient(90deg, var(--tower-navy-dark) 0%, var(--tower-navy) 100%);
        padding: 0.75rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(13, 27, 76, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .top-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: 10%;
        width: 150px;
        height: 200%;
        background: radial-gradient(ellipse at center, rgba(255, 215, 0, 0.1) 0%, transparent 70%);
        transform: rotate(-15deg);
    }
    
    .header-brand {
        display: flex;
        align-items: center;
        gap: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .header-logo {
        background: var(--tower-yellow);
        color: var(--tower-navy);
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
    }
    
    .header-title {
        color: var(--white);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .header-env {
        color: var(--tower-yellow);
        font-size: 0.8rem;
        text-align: right;
        position: relative;
        z-index: 1;
    }
    
    /* Main content card */
    .main-card {
        background: var(--white);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 24px rgba(0, 83, 155, 0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Greeting */
    .greeting {
        font-size: 2rem;
        font-weight: 600;
        color: var(--tower-navy);
        margin-bottom: 2rem;
    }
    
    /* Big stat number */
    .big-stat {
        text-align: center;
        padding: 1rem;
    }
    
    .big-stat-value {
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--tower-navy);
        line-height: 1;
    }
    
    .big-stat-label {
        font-size: 0.85rem;
        color: var(--gray-600);
        margin-top: 0.5rem;
    }
    
    /* Metrics table */
    .metrics-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .metrics-table th {
        text-align: right;
        padding: 0.75rem 1rem;
        font-weight: 600;
        color: var(--gray-600);
        font-size: 0.85rem;
        border-bottom: 2px solid var(--gray-200);
    }
    
    .metrics-table th:first-child {
        text-align: left;
    }
    
    .metrics-table td {
        padding: 0.75rem 1rem;
        text-align: right;
        color: var(--tower-navy-dark);
        font-size: 0.95rem;
        border-bottom: 1px solid var(--gray-100);
    }
    
    .metrics-table td:first-child {
        text-align: left;
        font-weight: 500;
    }
    
    /* Country breakdown */
    .country-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 2px solid var(--gray-200);
    }
    
    .country-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--gray-600);
        margin-bottom: 1rem;
    }
    
    .country-grid {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    
    .country-badge {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem 1rem;
        background: var(--gray-50);
        border-radius: 8px;
        min-width: 50px;
    }
    
    .country-code {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: var(--tower-navy);
        font-size: 0.85rem;
    }
    
    .country-count {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--tower-navy-dark);
    }
    
    .country-legend {
        font-size: 0.75rem;
        color: var(--gray-400);
        margin-top: 0.5rem;
    }
    
    /* Action buttons */
    .action-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        border: none;
    }
    
    .btn-primary {
        background: var(--tower-navy);
        color: var(--white);
    }
    
    .btn-primary:hover {
        background: var(--tower-navy-dark);
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: var(--white);
        color: var(--tower-navy);
        border: 2px solid var(--tower-navy);
    }
    
    .btn-secondary:hover {
        background: var(--gray-50);
    }
    
    /* Data table styling */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    
    .data-table thead {
        background: var(--tower-navy);
        color: var(--white);
    }
    
    .data-table th {
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .data-table td {
        padding: 0.75rem;
        border-bottom: 1px solid var(--gray-200);
        vertical-align: middle;
    }
    
    .data-table tr:hover {
        background: var(--gray-50);
    }
    
    .data-table .mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    
    /* Checkbox styling */
    .custom-checkbox {
        width: 18px;
        height: 18px;
        accent-color: var(--tower-navy);
    }
    
    /* Filter bar */
    .filter-bar {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: var(--gray-50);
        border-radius: 8px;
        margin-bottom: 1rem;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .filter-input {
        padding: 0.5rem 1rem;
        border: 1px solid var(--gray-200);
        border-radius: 6px;
        font-size: 0.85rem;
        min-width: 150px;
    }
    
    .filter-input:focus {
        outline: none;
        border-color: var(--tower-navy);
        box-shadow: 0 0 0 3px rgba(0, 83, 155, 0.1);
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-confirmed {
        background: #dcfce7;
        color: #166534;
    }
    
    .badge-pending {
        background: #fef9c3;
        color: #a16207;
    }
    
    .badge-rejected {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Back button */
    .back-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--tower-navy);
        color: var(--white);
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
        border: none;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    /* Comparison cards - Tower branded */
    .compare-card {
        background: var(--white);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 83, 155, 0.08);
        border-top: 4px solid var(--tower-navy);
    }
    
    .compare-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--gray-100);
    }
    
    .compare-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--tower-navy-dark);
    }
    
    .customer-id-badge {
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, var(--tower-navy) 0%, var(--tower-navy-light) 100%);
        color: var(--white);
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .field-row {
        display: flex;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--gray-100);
    }
    
    .field-label {
        flex: 0 0 40%;
        font-size: 0.85rem;
        color: var(--gray-600);
        font-weight: 500;
    }
    
    .field-value {
        flex: 1;
        font-size: 0.9rem;
        color: var(--tower-navy-dark);
    }
    
    .field-match {
        background: rgba(34, 197, 94, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    .field-diff {
        background: rgba(239, 68, 68, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Match score indicator - Tower themed with proper contrast */
    .match-score-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .score-high {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .score-medium {
        background: linear-gradient(135deg, var(--tower-yellow) 0%, var(--tower-yellow-dark) 100%);
        color: var(--tower-navy);
        font-weight: 700;
    }
    
    .score-low {
        background: linear-gradient(135deg, var(--tower-navy) 0%, var(--tower-navy-dark) 100%);
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Streamlit button overrides - Tower branded with proper contrast */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
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
    
    /* Dataframe styling */
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
# Country Codes for Pacific Islands
# =============================================================================
PACIFIC_COUNTRIES = {
    'FJ': 'Fiji',
    'NZ': 'New Zealand', 
    'AS': 'American Samoa',
    'CK': 'Cook Islands',
    'SB': 'Solomon Islands',
    'TO': 'Tonga',
    'VU': 'Vanuatu',
    'WS': 'Western Samoa',
    'Unknown': 'Multiple/No Country Code'
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_agent_name():
    """Get current agent name from session state."""
    return st.session_state.get('agent_name', 'Agent')

def get_greeting():
    """Get time-appropriate greeting in Fijian style."""
    hour = datetime.now().hour
    if hour < 12:
        return "Bula! Good Morning"
    elif hour < 17:
        return "Bula! Good Afternoon"
    else:
        return "Bula! Good Evening"

def get_dashboard_metrics():
    """Get comprehensive metrics for dashboard."""
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    query = f"""
    WITH metrics AS (
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN STATUS = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN STATUS = 'MATCHED' THEN 1 ELSE 0 END) as matched,
            SUM(CASE WHEN STATUS = 'NOT_MATCHED' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN PRIORITY = 'HIGH' AND STATUS = 'PENDING' THEN 1 ELSE 0 END) as high_priority
        FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES
    ),
    today_stats AS (
        SELECT 
            COUNT(*) as today_completed,
            SUM(CASE WHEN d.DECISION = 'MATCHED' THEN 1 ELSE 0 END) as today_matched,
            SUM(CASE WHEN d.DECISION = 'NOT_MATCHED' THEN 1 ELSE 0 END) as today_rejected
        FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS d
        WHERE DATE(d.DECISION_TIMESTAMP) = '{today}'
    ),
    week_stats AS (
        SELECT 
            COUNT(*) as week_completed,
            SUM(CASE WHEN d.DECISION = 'MATCHED' THEN 1 ELSE 0 END) as week_matched,
            SUM(CASE WHEN d.DECISION = 'NOT_MATCHED' THEN 1 ELSE 0 END) as week_rejected
        FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS d
        WHERE DATE(d.DECISION_TIMESTAMP) >= '{week_start}'
    ),
    month_stats AS (
        SELECT 
            COUNT(*) as month_completed,
            SUM(CASE WHEN d.DECISION = 'MATCHED' THEN 1 ELSE 0 END) as month_matched,
            SUM(CASE WHEN d.DECISION = 'NOT_MATCHED' THEN 1 ELSE 0 END) as month_rejected
        FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS d
        WHERE DATE(d.DECISION_TIMESTAMP) >= '{month_start}'
    )
    SELECT m.*, t.*, w.*, mo.*
    FROM metrics m, today_stats t, week_stats w, month_stats mo
    """
    return session.sql(query).collect()[0]

def get_country_breakdown():
    """Get pending clusters by country."""
    query = """
    SELECT 
        COALESCE(c1.COUNTRY, 'Unknown') as COUNTRY,
        COUNT(*) as COUNT
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES dc
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c1 ON dc.CUSTOMER_ID_1 = c1.CUSTOMER_ID
    WHERE dc.STATUS = 'PENDING'
    GROUP BY c1.COUNTRY
    ORDER BY COUNT DESC
    """
    return session.sql(query).to_pandas()

def get_pending_clusters(filters=None):
    """Get pending duplicate candidates with optional filters."""
    query = """
    SELECT 
        dc.CANDIDATE_ID as CLUSTER_ID,
        COALESCE(c1.COUNTRY, 'Unknown') as CNTY,
        dc.MATCH_SCORE as POINTS,
        dc.CUSTOMER_ID_1,
        dc.CUSTOMER_ID_2,
        c1.FIRST_NAME || ' ' || c1.LAST_NAME as NAME_1,
        c2.FIRST_NAME || ' ' || c2.LAST_NAME as NAME_2,
        dc.ASSIGNED_TO as CONSULTANT,
        dc.STATUS,
        dc.PRIORITY,
        dc.CREATED_DATE,
        dc.MATCH_REASON
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES dc
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c1 ON dc.CUSTOMER_ID_1 = c1.CUSTOMER_ID
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c2 ON dc.CUSTOMER_ID_2 = c2.CUSTOMER_ID
    WHERE dc.STATUS = 'PENDING'
    """
    
    if filters:
        if filters.get('cluster_id'):
            query += f" AND dc.CANDIDATE_ID LIKE '%{filters['cluster_id']}%'"
        if filters.get('customer'):
            query += f" AND (dc.CUSTOMER_ID_1 LIKE '%{filters['customer']}%' OR dc.CUSTOMER_ID_2 LIKE '%{filters['customer']}%')"
        if filters.get('country'):
            query += f" AND c1.COUNTRY = '{filters['country']}'"
    
    query += " ORDER BY dc.MATCH_SCORE DESC, dc.CREATED_DATE"
    return session.sql(query).to_pandas()

def get_all_clusters(filters=None):
    """Get all clusters for review (including processed)."""
    query = """
    SELECT 
        dc.CANDIDATE_ID as CLUSTER_ID,
        COALESCE(c1.COUNTRY, 'Unknown') as CNTY,
        dc.MATCH_SCORE as POINTS,
        dc.CUSTOMER_ID_1,
        dc.CUSTOMER_ID_2,
        c1.FIRST_NAME || ' ' || c1.LAST_NAME as NAME_1,
        c2.FIRST_NAME || ' ' || c2.LAST_NAME as NAME_2,
        dc.ASSIGNED_TO as CONSULTANT,
        dc.STATUS,
        CASE WHEN dc.STATUS = 'MATCHED' THEN TRUE ELSE FALSE END as CONFIRMED,
        CASE WHEN dc.STATUS != 'PENDING' THEN TRUE ELSE FALSE END as REVIEWED,
        dc.PRIORITY,
        dc.CREATED_DATE
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES dc
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c1 ON dc.CUSTOMER_ID_1 = c1.CUSTOMER_ID
    JOIN DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS c2 ON dc.CUSTOMER_ID_2 = c2.CUSTOMER_ID
    WHERE 1=1
    """
    
    if filters:
        if filters.get('cluster_id'):
            query += f" AND dc.CANDIDATE_ID LIKE '%{filters['cluster_id']}%'"
        if filters.get('customer'):
            query += f" AND (dc.CUSTOMER_ID_1 LIKE '%{filters['customer']}%' OR dc.CUSTOMER_ID_2 LIKE '%{filters['customer']}%')"
        if filters.get('country'):
            query += f" AND c1.COUNTRY = '{filters['country']}'"
        if filters.get('consultant'):
            query += f" AND dc.ASSIGNED_TO LIKE '%{filters['consultant']}%'"
    
    query += " ORDER BY dc.CREATED_DATE DESC"
    return session.sql(query).to_pandas()

def get_customer_details(customer_id):
    """Get full customer details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS 
    WHERE CUSTOMER_ID = '{customer_id}'
    """
    result = session.sql(query).collect()
    return result[0] if result else None

def get_cluster_details(cluster_id):
    """Get cluster/candidate details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    WHERE CANDIDATE_ID = '{cluster_id}'
    """
    result = session.sql(query).collect()
    return result[0] if result else None

def record_decision(cluster_id, agent_name, decision, reason, notes=''):
    """Record agent's decision."""
    decision_id = str(uuid.uuid4())[:36]
    session_id = st.session_state.get('session_id', str(uuid.uuid4())[:36])
    
    # Escape single quotes
    reason = reason.replace("'", "''") if reason else ''
    notes = notes.replace("'", "''") if notes else ''
    agent_name = agent_name.replace("'", "''") if agent_name else ''
    
    insert_query = f"""
    INSERT INTO DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS 
    (DECISION_ID, CANDIDATE_ID, AGENT_NAME, DECISION, DECISION_REASON, NOTES, SESSION_ID)
    VALUES ('{decision_id}', '{cluster_id}', '{agent_name}', '{decision}', '{reason}', '{notes}', '{session_id}')
    """
    session.sql(insert_query).collect()
    
    update_query = f"""
    UPDATE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    SET STATUS = '{decision}', ASSIGNED_TO = '{agent_name}'
    WHERE CANDIDATE_ID = '{cluster_id}'
    """
    session.sql(update_query).collect()
    
    return decision_id

def get_consultants():
    """Get list of consultants who have made decisions."""
    query = """
    SELECT DISTINCT AGENT_NAME as CONSULTANT, 
           MAX(DECISION_TIMESTAMP) as LAST_ACTIVE
    FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS
    GROUP BY AGENT_NAME
    ORDER BY LAST_ACTIVE DESC
    """
    return session.sql(query).to_pandas()

# =============================================================================
# Initialize Session State
# =============================================================================
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:36]
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'
if 'selected_cluster' not in st.session_state:
    st.session_state.selected_cluster = None
if 'agent_name' not in st.session_state:
    st.session_state.agent_name = 'Agent'

# =============================================================================
# Header - Tower Insurance NZ Branded with Logo Colors
# =============================================================================
st.markdown("""
<div class="top-header">
    <div class="header-brand">
        <span class="header-logo">🏢 TOWER</span>
        <span class="header-title" style="color: white;">Customer De-duping Workflow (Read-only)</span>
    </div>
    <div class="header-env">
        <div style="color: rgba(255,255,255,0.7);">Environment</div>
        <div style="font-weight: 600; color: #FFD700;">Customer Deduping | NZ</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# Navigation Sidebar (Hidden by default, use buttons instead)
# =============================================================================
# Agent name input in expander
with st.expander("⚙️ Settings", expanded=False):
    agent_name = st.text_input("Your Name", value=st.session_state.agent_name)
    if agent_name != st.session_state.agent_name:
        st.session_state.agent_name = agent_name
        st.rerun()

# =============================================================================
# DASHBOARD VIEW
# =============================================================================
if st.session_state.current_view == 'dashboard':
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Greeting
    st.markdown(f'<div class="greeting">{get_greeting()}, {get_agent_name()}!</div>', unsafe_allow_html=True)
    
    try:
        metrics = get_dashboard_metrics()
        
        # Layout: Stats on left, Metrics table on right
        col_stats, col_metrics, col_actions = st.columns([1, 2, 1])
        
        with col_stats:
            # Big stats
            st.markdown(f"""
            <div class="big-stat">
                <div class="big-stat-value">{int(metrics['PENDING'])}</div>
                <div class="big-stat-label">your unresolved /<br>blocked records</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="big-stat" style="margin-top: 1rem;">
                <div class="big-stat-value">{int(metrics['HIGH_PRIORITY'])}</div>
                <div class="big-stat-label">clusters left in<br>today's queue</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metrics:
            # Metrics table
            st.markdown("""
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th></th>
                        <th>Today</th>
                        <th>This Week</th>
                        <th>This Month</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                    <tr>
                        <td>Clusters completed:</td>
                        <td>{int(metrics['TODAY_COMPLETED'])}</td>
                        <td>{int(metrics['WEEK_COMPLETED'])}</td>
                        <td>{int(metrics['MONTH_COMPLETED'])}</td>
                    </tr>
                    <tr>
                        <td>Matches checked:</td>
                        <td>{int(metrics['TODAY_COMPLETED'])}</td>
                        <td>{int(metrics['WEEK_COMPLETED'])}</td>
                        <td>{int(metrics['MONTH_COMPLETED'])}</td>
                    </tr>
                    <tr>
                        <td>Matches confirmed:</td>
                        <td>{int(metrics['TODAY_MATCHED'])}</td>
                        <td>{int(metrics['WEEK_MATCHED'])}</td>
                        <td>{int(metrics['MONTH_MATCHED'])}</td>
                    </tr>
                    <tr>
                        <td>Matches rejected:</td>
                        <td>{int(metrics['TODAY_REJECTED'])}</td>
                        <td>{int(metrics['WEEK_REJECTED'])}</td>
                        <td>{int(metrics['MONTH_REJECTED'])}</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)
        
        with col_actions:
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Get Started", use_container_width=True, type="primary"):
                st.session_state.current_view = 'review_matches'
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("📊 Review Clusters", use_container_width=True):
                st.session_state.current_view = 'review_clusters'
                st.rerun()
            
            if st.button("🔍 Review Matches", use_container_width=True):
                st.session_state.current_view = 'review_matches'
                st.rerun()
            
            if st.button("👥 User Admin", use_container_width=True):
                st.session_state.current_view = 'admin'
                st.rerun()
        
        # Country breakdown
        st.markdown('<div class="country-section">', unsafe_allow_html=True)
        st.markdown('<div class="country-title">Clusters Left: Country Level</div>', unsafe_allow_html=True)
        
        country_data = get_country_breakdown()
        
        # Create country grid
        cols = st.columns(len(PACIFIC_COUNTRIES))
        for i, (code, name) in enumerate(PACIFIC_COUNTRIES.items()):
            count = 0
            if len(country_data) > 0:
                matching = country_data[country_data['COUNTRY'].str.upper().str.contains(code.upper(), na=False)]
                if len(matching) > 0:
                    count = int(matching['COUNT'].sum())
            
            with cols[i]:
                color = "#0d1b4c" if count > 0 else "#94a3b8"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: {color}; font-size: 0.85rem;">{code}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #080f2d;">{count}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Legend
        st.markdown("""
        <div class="country-legend">
            <strong>AS:</strong> American Samoa, <strong>CK:</strong> Cook Islands, <strong>FJ:</strong> Fiji, 
            <strong>NZ:</strong> New Zealand, <strong>SB:</strong> Solomon Islands, <strong>TO:</strong> Tonga, 
            <strong>VU:</strong> Vanuatu, <strong>WS:</strong> Western Samoa, <strong>Unknown:</strong> Multiple/No Country Code
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Please ensure the database is set up correctly.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# REVIEW CLUSTERS VIEW
# =============================================================================
elif st.session_state.current_view == 'review_clusters':
    
    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    
    with col1:
        filter_cluster = st.text_input("Filter by CLUSTER_ID", placeholder="Enter cluster ID...")
    with col2:
        filter_customer = st.text_input("Filter by CUSTOMER", placeholder="Enter customer ID...")
    with col3:
        filter_consultant = st.text_input("Filter by CONSULTANT", placeholder="Enter consultant...")
    with col4:
        filter_country = st.selectbox("Filter by Country", options=['All'] + list(PACIFIC_COUNTRIES.values()))
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        clear_filters = st.button("Clear", use_container_width=True)
    
    # Build filters dict
    filters = {}
    if filter_cluster and not clear_filters:
        filters['cluster_id'] = filter_cluster
    if filter_customer and not clear_filters:
        filters['customer'] = filter_customer
    if filter_consultant and not clear_filters:
        filters['consultant'] = filter_consultant
    if filter_country and filter_country != 'All' and not clear_filters:
        filters['country'] = filter_country
    
    try:
        clusters = get_all_clusters(filters if filters else None)
        
        if len(clusters) > 0:
            st.markdown(f"**{len(clusters)} clusters found**")
            
            # Display as interactive table
            for _, row in clusters.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 2, 2, 1])
                
                with col1:
                    st.markdown(f"<span class='mono'>{row['CLUSTER_ID']}</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write(row['CNTY'][:2] if row['CNTY'] else 'N/A')
                
                with col3:
                    st.write(f"{row['POINTS']:.0f}")
                
                with col4:
                    st.markdown(f"<span class='mono'>{row['CUSTOMER_ID_1']}</span>", unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"<span class='mono'>{row['CUSTOMER_ID_2']}</span>", unsafe_allow_html=True)
                
                with col6:
                    status = row['STATUS']
                    if status == 'MATCHED':
                        st.markdown('<span class="badge badge-confirmed">✓ Confirmed</span>', unsafe_allow_html=True)
                    elif status == 'NOT_MATCHED':
                        st.markdown('<span class="badge badge-rejected">✗ Rejected</span>', unsafe_allow_html=True)
                    else:
                        if st.button("Review", key=f"rev_{row['CLUSTER_ID']}"):
                            st.session_state.selected_cluster = row['CLUSTER_ID']
                            st.session_state.current_view = 'compare'
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("No clusters found matching your criteria.")
            
    except Exception as e:
        st.error(f"Error loading clusters: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# REVIEW MATCHES VIEW (Work Queue)
# =============================================================================
elif st.session_state.current_view == 'review_matches':
    
    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 🔍 Pending Matches for Review")
    
    try:
        pending = get_pending_clusters()
        
        if len(pending) > 0:
            st.markdown(f"**{len(pending)} matches pending review**")
            st.markdown("---")
            
            for _, row in pending.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    **{row['NAME_1']}** ↔ **{row['NAME_2']}**  
                    <small class="mono">{row['CUSTOMER_ID_1']} vs {row['CUSTOMER_ID_2']}</small>
                    """, unsafe_allow_html=True)
                
                with col2:
                    reason = row['MATCH_REASON'] if row['MATCH_REASON'] else ''
                    st.markdown(f"<small>{reason[:50]}...</small>", unsafe_allow_html=True)
                
                with col3:
                    score = row['POINTS']
                    score_class = 'score-high' if score >= 85 else ('score-medium' if score >= 70 else 'score-low')
                    st.markdown(f'<span class="match-score-pill {score_class}">{score:.0f}%</span>', unsafe_allow_html=True)
                
                with col4:
                    if st.button("Review →", key=f"review_{row['CLUSTER_ID']}", type="primary"):
                        st.session_state.selected_cluster = row['CLUSTER_ID']
                        st.session_state.current_view = 'compare'
                        st.rerun()
                
                st.markdown("---")
        else:
            st.success("🎉 All caught up! No pending matches to review.")
            
    except Exception as e:
        st.error(f"Error loading matches: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# COMPARE VIEW (Side-by-side comparison)
# =============================================================================
elif st.session_state.current_view == 'compare':
    
    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.current_view = 'review_matches'
        st.rerun()
    
    if st.session_state.selected_cluster is None:
        st.warning("No cluster selected. Please select from the review list.")
        st.stop()
    
    try:
        cluster = get_cluster_details(st.session_state.selected_cluster)
        
        if cluster is None:
            st.warning("Cluster not found.")
            st.session_state.selected_cluster = None
            st.stop()
        
        customer1 = get_customer_details(cluster['CUSTOMER_ID_1'])
        customer2 = get_customer_details(cluster['CUSTOMER_ID_2'])
        
        # Match score header
        score = cluster['MATCH_SCORE']
        score_class = 'score-high' if score >= 85 else ('score-medium' if score >= 70 else 'score-low')
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(13, 27, 76, 0.05) 0%, rgba(13, 27, 76, 0.1) 100%); padding: 1rem 1.5rem; border-radius: 8px; border-left: 4px solid #0d1b4c; margin-bottom: 1.5rem;">
            <strong>Match Analysis:</strong> {cluster['MATCH_REASON']}
            <br><br>
            <span class="match-score-pill {score_class}">Match Score: {score:.0f}%</span>
            &nbsp;&nbsp;
            <span class="badge badge-{'confirmed' if cluster['PRIORITY'] == 'HIGH' else 'pending'}">{cluster['PRIORITY']} Priority</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        
        compare_fields = [
            ('CUSTOMER_ID', 'Customer ID'),
            ('FIRST_NAME', 'First Name'),
            ('LAST_NAME', 'Last Name'),
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('DATE_OF_BIRTH', 'Date of Birth'),
            ('ADDRESS_LINE1', 'Address'),
            ('CITY', 'City'),
            ('POSTAL_CODE', 'Postal Code'),
            ('ACCOUNT_STATUS', 'Account Status'),
            ('ACCOUNT_TYPE', 'Account Type'),
            ('SOURCE_SYSTEM', 'Source System'),
            ('TOTAL_TRANSACTIONS', 'Transactions'),
            ('ACCOUNT_BALANCE', 'Balance'),
        ]
        
        with col1:
            st.markdown(f"""
            <div class="compare-card">
                <div class="compare-header">
                    <span class="compare-title">Record A</span>
                    <span class="customer-id-badge">{customer1['CUSTOMER_ID']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for field_key, field_label in compare_fields:
                val1 = customer1.get(field_key)
                val2 = customer2.get(field_key)
                match = "✅" if str(val1) == str(val2) else "⚠️"
                st.markdown(f"**{field_label}** {match}")
                st.text(str(val1) if val1 else "—")
        
        with col2:
            st.markdown(f"""
            <div class="compare-card">
                <div class="compare-header">
                    <span class="compare-title">Record B</span>
                    <span class="customer-id-badge">{customer2['CUSTOMER_ID']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for field_key, field_label in compare_fields:
                val1 = customer1.get(field_key)
                val2 = customer2.get(field_key)
                match = "✅" if str(val1) == str(val2) else "⚠️"
                st.markdown(f"**{field_label}** {match}")
                st.text(str(val2) if val2 else "—")
        
        # Decision panel
        st.markdown("---")
        st.markdown("### 📝 Make Decision")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            decision_reason = st.selectbox(
                "Decision Reason",
                options=[
                    "Same person - confirmed match",
                    "Different people - name coincidence",
                    "Different people - family members",
                    "Insufficient information",
                    "Data quality issue",
                    "Other"
                ]
            )
            notes = st.text_area("Notes (optional)", placeholder="Add any notes...")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✅ CONFIRM MATCH", use_container_width=True, type="primary"):
                record_decision(st.session_state.selected_cluster, get_agent_name(), 'MATCHED', decision_reason, notes)
                st.success("✓ Match confirmed!")
                st.session_state.selected_cluster = None
                st.rerun()
            
            if st.button("❌ REJECT - Not a Match", use_container_width=True):
                record_decision(st.session_state.selected_cluster, get_agent_name(), 'NOT_MATCHED', decision_reason, notes)
                st.success("✗ Match rejected")
                st.session_state.selected_cluster = None
                st.rerun()
            
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.selected_cluster = None
                st.session_state.current_view = 'review_matches'
                st.rerun()
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.selected_cluster = None

# =============================================================================
# ADMIN VIEW
# =============================================================================
elif st.session_state.current_view == 'admin':
    
    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown("## 👥 User Administration")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_consultant = st.text_input("Filter by Consultant", placeholder="Search...")
    with col2:
        filter_country_admin = st.selectbox("Filter by Country", options=['All'] + list(PACIFIC_COUNTRIES.values()), key="admin_country")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Reset", use_container_width=True)
    
    try:
        consultants = get_consultants()
        
        if len(consultants) > 0:
            st.markdown("---")
            
            # Table header
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            with col1:
                st.markdown("**CONSULTANT**")
            with col2:
                st.markdown("**ADMIN**")
            with col3:
                st.markdown("**COUNTRY**")
            with col4:
                st.markdown("**ACTIONS**")
            
            st.markdown("---")
            
            for _, row in consultants.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
                
                with col1:
                    st.write(row['CONSULTANT'])
                
                with col2:
                    st.checkbox("", key=f"admin_{row['CONSULTANT']}", label_visibility="collapsed")
                
                with col3:
                    st.selectbox(
                        "Country",
                        options=list(PACIFIC_COUNTRIES.keys()),
                        key=f"country_{row['CONSULTANT']}",
                        label_visibility="collapsed"
                    )
                
                with col4:
                    st.button("🗑️", key=f"delete_{row['CONSULTANT']}")
                
                st.markdown("---")
        else:
            st.info("No consultants found. Decisions will create consultant records.")
        
        # Add new consultant section
        st.markdown("### Add New Consultant")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_consultant = st.text_input("Email/Name", placeholder="consultant@email.com")
        with col2:
            new_country = st.selectbox("Assign Country", options=list(PACIFIC_COUNTRIES.keys()))
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add", type="primary", use_container_width=True):
                if new_consultant:
                    st.success(f"Added {new_consultant}")
                else:
                    st.warning("Please enter a consultant name/email")
                    
    except Exception as e:
        st.error(f"Error loading admin data: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# Footer - Tower Insurance NZ Branded with Logo Colors
# =============================================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem;">
    <div style="display: inline-flex; align-items: center; gap: 0.5rem;">
        <span style="background: #0d1b4c; color: #FFD700; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600; font-size: 0.7rem;">TOWER</span>
        <span>Customer De-duping Workflow</span>
        <span>•</span>
        <span>Pacific Islands Region</span>
        <span>•</span>
        <span>Session: {st.session_state.session_id[:8]}</span>
    </div>
</div>
""", unsafe_allow_html=True)
