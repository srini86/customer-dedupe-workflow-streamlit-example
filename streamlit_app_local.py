"""
Dedupe Workflow Tool - LOCAL TESTING VERSION
Run this version locally before deploying to Snowflake.

Usage:
    pip install streamlit snowflake-connector-python pandas
    streamlit run streamlit_app_local.py

Configure your Snowflake connection in ~/.snowflake/connections.toml or use environment variables.
"""

import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import datetime
import uuid
import os

# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Dedupe Workflow Tool",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS (Same as production version)
# =============================================================================
st.markdown("""
<style>
    :root {
        --primary-color: #0d4f4f;
        --secondary-color: #1a7a7a;
        --accent-color: #ff6b5b;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d4f4f 0%, #1a7a7a 50%, #2d9d9d 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(13, 79, 79, 0.3);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafa 100%);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #1a7a7a;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0d4f4f;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #5a6c6c;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .customer-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #1a7a7a;
    }
    
    .customer-id {
        font-family: 'SF Mono', 'Consolas', monospace;
        background: #e8f4f4;
        color: #0d4f4f;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .match-score-high {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    .match-score-medium {
        background: linear-gradient(135deg, #f39c12 0%, #d68910 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    .match-score-low {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
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
        background: #fef3c7;
        color: #d97706;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .priority-low {
        background: #dbeafe;
        color: #2563eb;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .info-callout {
        background: linear-gradient(135deg, #e8f4f4 0%, #d5ebeb 100%);
        border-left: 4px solid #1a7a7a;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .status-matched {
        background: #d1fae5;
        color: #065f46;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .status-not-matched {
        background: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d4f4f 0%, #0a3535 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ecf0f1;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Snowflake Connection (Local Version)
# =============================================================================

@st.cache_resource
def get_connection():
    """Create Snowflake connection for local testing."""
    # Try to get credentials from Streamlit secrets first
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets.get("snowflake", {}).get("warehouse", "COMPUTE_WH"),
            database="DEDUPE_WORKFLOW_DB",
            schema="DEDUPE_SCHEMA"
        )
        return conn
    except:
        pass
    
    # Fall back to environment variables
    try:
        conn = snowflake.connector.connect(
            user=os.environ.get("SNOWFLAKE_USER"),
            password=os.environ.get("SNOWFLAKE_PASSWORD"),
            account=os.environ.get("SNOWFLAKE_ACCOUNT"),
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database="DEDUPE_WORKFLOW_DB",
            schema="DEDUPE_SCHEMA"
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        st.info("""
        **Setup Instructions:**
        
        Option 1: Create `.streamlit/secrets.toml`:
        ```toml
        [snowflake]
        user = "your_username"
        password = "your_password"
        account = "your_account"
        warehouse = "COMPUTE_WH"
        ```
        
        Option 2: Set environment variables:
        ```bash
        export SNOWFLAKE_USER=your_username
        export SNOWFLAKE_PASSWORD=your_password
        export SNOWFLAKE_ACCOUNT=your_account
        export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
        ```
        """)
        return None

def execute_query(query, fetch=True):
    """Execute a query and return results."""
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if fetch:
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        return True
    except Exception as e:
        st.error(f"Query error: {e}")
        return None
    finally:
        cursor.close()

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
    result = execute_query(query)
    if result is not None and len(result) > 0:
        return result.iloc[0].to_dict()
    return None

def get_pending_candidates(priority_filter=None):
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
    query += " ORDER BY dc.MATCH_SCORE DESC"
    return execute_query(query)

def get_customer_details(customer_id):
    """Get full customer details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS 
    WHERE CUSTOMER_ID = '{customer_id}'
    """
    result = execute_query(query)
    if result is not None and len(result) > 0:
        return result.iloc[0].to_dict()
    return None

def get_candidate_details(candidate_id):
    """Get duplicate candidate details."""
    query = f"""
    SELECT * FROM DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    WHERE CANDIDATE_ID = '{candidate_id}'
    """
    result = execute_query(query)
    if result is not None and len(result) > 0:
        return result.iloc[0].to_dict()
    return None

def record_decision(candidate_id, agent_name, decision, reason, notes):
    """Record agent's decision and update candidate status."""
    decision_id = str(uuid.uuid4())[:36]
    session_id = st.session_state.get('session_id', str(uuid.uuid4())[:36])
    
    # Escape single quotes
    reason = reason.replace("'", "''")
    notes = notes.replace("'", "''")
    agent_name = agent_name.replace("'", "''")
    
    insert_query = f"""
    INSERT INTO DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS 
    (DECISION_ID, CANDIDATE_ID, AGENT_NAME, DECISION, DECISION_REASON, NOTES, SESSION_ID)
    VALUES ('{decision_id}', '{candidate_id}', '{agent_name}', '{decision}', '{reason}', '{notes}', '{session_id}')
    """
    execute_query(insert_query, fetch=False)
    
    update_query = f"""
    UPDATE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES 
    SET STATUS = '{decision}', ASSIGNED_TO = '{agent_name}'
    WHERE CANDIDATE_ID = '{candidate_id}'
    """
    execute_query(update_query, fetch=False)
    
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
    return execute_query(query)

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
# Sidebar
# =============================================================================
with st.sidebar:
    st.markdown("### 🔗 Dedupe Workflow")
    st.markdown("*(Local Testing)*")
    st.markdown("---")
    
    agent_name = st.text_input("👤 Agent Name", value="Demo Agent", key="agent_name")
    
    st.markdown("---")
    st.markdown("### Navigation")
    
    if st.button("📊 Dashboard", use_container_width=True, type="secondary"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    if st.button("📋 Work Queue", use_container_width=True, type="secondary"):
        st.session_state.current_view = 'work_queue'
        st.rerun()
    
    if st.button("🔍 Review Records", use_container_width=True, type="primary"):
        st.session_state.current_view = 'review'
        st.rerun()
    
    if st.button("📜 Decision History", use_container_width=True, type="secondary"):
        st.session_state.current_view = 'history'
        st.rerun()
    
    st.markdown("---")
    
    conn = get_connection()
    if conn:
        st.success("✅ Connected to Snowflake")
        metrics = get_dashboard_metrics()
        if metrics:
            st.metric("Pending Reviews", int(metrics['PENDING']))
            st.metric("High Priority", int(metrics['HIGH_PRIORITY_PENDING']))
    else:
        st.error("❌ Not connected")

# =============================================================================
# Main Content
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1>🔗 Duplicate Record Management</h1>
    <p>Review and verify potential customer duplicate records (Local Testing)</p>
</div>
""", unsafe_allow_html=True)

conn = get_connection()
if conn is None:
    st.stop()

# =============================================================================
# Dashboard View
# =============================================================================
if st.session_state.current_view == 'dashboard':
    st.markdown("## 📊 Dashboard Overview")
    
    metrics = get_dashboard_metrics()
    if metrics:
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
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Start High Priority Review", use_container_width=True, type="primary"):
                pending = get_pending_candidates(priority_filter='HIGH')
                if pending is not None and len(pending) > 0:
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
        
        st.markdown("### 📈 Recent Activity")
        history = get_decision_history(limit=5)
        if history is not None and len(history) > 0:
            for _, row in history.iterrows():
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {'#2ecc71' if row['DECISION'] == 'MATCHED' else '#e74c3c'};">
                    <strong>{row['AGENT_NAME']}</strong> marked <code>{row['CUSTOMER_ID_1']}</code> ↔ <code>{row['CUSTOMER_ID_2']}</code> as 
                    <span class="{'status-matched' if row['DECISION'] == 'MATCHED' else 'status-not-matched'}">{row['DECISION']}</span>
                    <br><small style="color: #666;">Score: {row['MATCH_SCORE']}%</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent decisions recorded")

# =============================================================================
# Work Queue View
# =============================================================================
elif st.session_state.current_view == 'work_queue':
    st.markdown("## 📋 Work Queue")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=[None, 'HIGH', 'MEDIUM', 'LOW'],
            format_func=lambda x: 'All Priorities' if x is None else x
        )
    
    pending = get_pending_candidates(priority_filter=priority_filter)
    
    if pending is not None and len(pending) > 0:
        st.markdown(f"**{len(pending)} records pending review**")
        
        for _, row in pending.iterrows():
            priority_class = f"priority-{row['PRIORITY'].lower()}"
            score = row['MATCH_SCORE']
            score_class = 'match-score-high' if score >= 85 else ('match-score-medium' if score >= 70 else 'match-score-low')
            
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.markdown(f"""
                **{row['NAME_1']}** ↔ **{row['NAME_2']}**  
                <small><code>{row['CUSTOMER_ID_1']}</code> vs <code>{row['CUSTOMER_ID_2']}</code></small>
                """, unsafe_allow_html=True)
            
            with col2:
                reason = row['MATCH_REASON']
                st.markdown(f"<small>{reason[:60] if reason else ''}...</small>", unsafe_allow_html=True)
            
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

# =============================================================================
# Review View
# =============================================================================
elif st.session_state.current_view == 'review':
    st.markdown("## 🔍 Record Comparison")
    
    if st.session_state.selected_candidate is None:
        pending = get_pending_candidates()
        if pending is not None and len(pending) > 0:
            st.session_state.selected_candidate = pending.iloc[0]['CANDIDATE_ID']
        else:
            st.success("🎉 All caught up! No pending items to review.")
            st.stop()
    
    candidate = get_candidate_details(st.session_state.selected_candidate)
    
    if candidate is None:
        st.warning("Candidate not found. Please select from the work queue.")
        st.session_state.selected_candidate = None
        st.stop()
    
    customer1 = get_customer_details(candidate['CUSTOMER_ID_1'])
    customer2 = get_customer_details(candidate['CUSTOMER_ID_2'])
    
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
        ('TOTAL_TRANSACTIONS', 'Total Transactions'),
        ('ACCOUNT_BALANCE', 'Account Balance'),
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="customer-card">
            <h3 style="margin:0; color: #0d4f4f;">Record A</h3>
            <span class="customer-id">{customer1['CUSTOMER_ID']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        for field_key, field_label in compare_fields:
            val1 = customer1.get(field_key)
            val2 = customer2.get(field_key)
            match_indicator = "✅" if str(val1) == str(val2) else "⚠️"
            st.markdown(f"**{field_label}** {match_indicator}")
            st.text(str(val1) if val1 else "—")
    
    with col2:
        st.markdown(f"""
        <div class="customer-card">
            <h3 style="margin:0; color: #0d4f4f;">Record B</h3>
            <span class="customer-id">{customer2['CUSTOMER_ID']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        for field_key, field_label in compare_fields:
            val1 = customer1.get(field_key)
            val2 = customer2.get(field_key)
            match_indicator = "✅" if str(val1) == str(val2) else "⚠️"
            st.markdown(f"**{field_label}** {match_indicator}")
            st.text(str(val2) if val2 else "—")
    
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
                "Insufficient information to decide",
                "Data quality issue - needs investigation",
                "Other (specify in notes)"
            ]
        )
        notes = st.text_area("Additional Notes", placeholder="Add any relevant notes...")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✅ MATCH - Same Person", use_container_width=True, type="primary"):
            record_decision(st.session_state.selected_candidate, agent_name, 'MATCHED', decision_reason, notes)
            st.success("Decision recorded: MATCHED")
            st.session_state.selected_candidate = None
            st.rerun()
        
        if st.button("❌ NOT MATCH - Different People", use_container_width=True):
            record_decision(st.session_state.selected_candidate, agent_name, 'NOT_MATCHED', decision_reason, notes)
            st.success("Decision recorded: NOT MATCHED")
            st.session_state.selected_candidate = None
            st.rerun()
        
        if st.button("⏭️ Skip for Now", use_container_width=True):
            st.session_state.selected_candidate = None
            st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Work Queue"):
        st.session_state.current_view = 'work_queue'
        st.rerun()

# =============================================================================
# History View
# =============================================================================
elif st.session_state.current_view == 'history':
    st.markdown("## 📜 Decision History")
    
    history = get_decision_history(limit=100)
    
    if history is not None and len(history) > 0:
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
        st.dataframe(
            history[['DECISION_TIMESTAMP', 'AGENT_NAME', 'CUSTOMER_ID_1', 'CUSTOMER_ID_2', 'MATCH_SCORE', 'DECISION', 'DECISION_REASON']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No decisions recorded yet.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Dedupe Workflow Tool (Local Testing) • Session: {st.session_state.session_id[:8]}
</div>
""", unsafe_allow_html=True)
