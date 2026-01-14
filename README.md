# Dedupe Workflow Tool - Streamlit in Snowflake Demo

A demonstration application showing how to replace a SharePoint/PowerApps duplicate management workflow with Snowflake and Streamlit in Snowflake (SiS).

## 🎯 Overview

This demo showcases a **Duplicate Record Management** workflow where customer service agents can:
- Review potential duplicate customer records
- Compare records side-by-side
- Make match/no-match decisions
- Track all decisions with full audit trail

## 📁 Project Structure

```
ASB-Streamlit/
├── 01_setup_database.sql          # Creates database, schema, and tables
├── 02_load_sample_data.sql        # Loads sample Fiji customer data
├── 03_setup_permissions.sql       # Sets up roles and permissions
├── 04_comparison_sharepoint_vs_snowflake.md  # Pros/cons analysis document
├── streamlit_app.py               # Main Streamlit application
└── README.md                      # This file
```

## 🚀 Deployment Instructions

### Step 1: Set Up Database and Tables

Run the SQL scripts in order using Snowsight or your preferred SQL client:

```sql
-- Run these scripts in order:
-- 1. Create the database and tables
-- Execute: 01_setup_database.sql

-- 2. Load sample data
-- Execute: 02_load_sample_data.sql

-- 3. Set up permissions (optional, customize as needed)
-- Execute: 03_setup_permissions.sql
```

### Step 2: Deploy Streamlit App

#### Option A: Using Snowsight UI

1. Navigate to **Snowsight** → **Streamlit** → **+ Streamlit App**
2. Enter app name: `Dedupe_Workflow_Tool`
3. Select warehouse: Choose an appropriate warehouse
4. Select database: `DEDUPE_WORKFLOW_DB`
5. Select schema: `DEDUPE_SCHEMA`
6. Copy the contents of `streamlit_app.py` into the editor
7. Click **Run**

#### Option B: Using SQL Command

```sql
CREATE OR REPLACE STREAMLIT DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DEDUPE_WORKFLOW_TOOL
  ROOT_LOCATION = '@DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.STREAMLIT_STAGE'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = 'COMPUTE_WH';
```

Note: For Option B, you'll need to first create a stage and upload the Python file.

### Step 3: Access the Application

Once deployed, access the app via:
- Snowsight: Navigate to **Streamlit** → **Dedupe_Workflow_Tool**
- Direct URL: Available in the Streamlit app settings

## 🖥️ Application Features

### Dashboard
- Overview metrics (pending, matched, not matched)
- High priority alerts
- Recent activity feed
- Quick action buttons

### Work Queue
- Filterable list of pending duplicate candidates
- Priority indicators (High/Medium/Low)
- Match score badges
- One-click navigation to review

### Record Comparison
- Side-by-side customer record display
- Field-level match indicators
- Match reason explanation
- Decision recording with reasons and notes

### Decision History
- Full audit trail of all decisions
- Agent name, timestamp, and reason
- Exportable for reporting

## 📊 Sample Data

The demo includes realistic Fiji customer data with various duplicate scenarios:

| Scenario | Description |
|----------|-------------|
| Clear duplicates | Same person, different records (data migration) |
| Typo variations | Similar names with spelling differences |
| Name changes | Married name scenarios |
| Nickname matches | Formal vs informal names |
| False positives | Same address (family members) |
| Business vs Personal | Same person, different account types |

## 🔧 Customization

### Adding New Fields

Edit the `compare_fields` list in `streamlit_app.py`:

```python
compare_fields = [
    ('FIELD_NAME', 'Display Label'),
    # Add your custom fields here
]
```

### Modifying Match Scoring Thresholds

Update the configuration table:

```sql
UPDATE WORKFLOW_CONFIG 
SET CONFIG_VALUE = '90' 
WHERE CONFIG_KEY = 'HIGH_PRIORITY_THRESHOLD';
```

### Changing UI Theme

Modify the CSS variables in the `<style>` section of the Streamlit app.

## 📋 Requirements

- Snowflake account with Streamlit enabled
- Warehouse for running queries
- Appropriate permissions (see `03_setup_permissions.sql`)

## 🔒 Security

- All data stays within Snowflake
- RBAC controls access to data and app
- Full audit trail of all decisions
- Session tracking for compliance

## 📞 Support

For questions about this demo, please contact your Snowflake account team.

---

## 🔄 Comparison: SharePoint/PowerApps vs Snowflake/Streamlit

See `04_comparison_sharepoint_vs_snowflake.md` for a detailed analysis of the pros and cons of migrating from the current architecture.

### Key Benefits of Snowflake/Streamlit:
- ✅ Data stays in Snowflake (no sync required)
- ✅ Real-time data access
- ✅ Single source of truth
- ✅ Unified security model
- ✅ No additional licensing costs
- ✅ Better scalability

### Considerations:
- ⚠️ Team needs Python/Snowflake skills
- ⚠️ UI less polished than PowerApps (but functional)
- ⚠️ Change management for existing users
