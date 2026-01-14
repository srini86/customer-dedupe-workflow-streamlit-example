-- ============================================================================
-- DEDUPE WORKFLOW DEMO - Permissions Setup
-- This script sets up roles and permissions for the Streamlit app
-- ============================================================================

USE DATABASE DEDUPE_WORKFLOW_DB;
USE SCHEMA DEDUPE_SCHEMA;

-- ============================================================================
-- Create Application Role
-- ============================================================================

-- Create a role for Dedupe Workflow users
CREATE ROLE IF NOT EXISTS DEDUPE_WORKFLOW_USER;

-- Grant database and schema access
GRANT USAGE ON DATABASE DEDUPE_WORKFLOW_DB TO ROLE DEDUPE_WORKFLOW_USER;
GRANT USAGE ON SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_USER;

-- Grant table permissions
GRANT SELECT ON ALL TABLES IN SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_USER;
GRANT INSERT ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS TO ROLE DEDUPE_WORKFLOW_USER;
GRANT UPDATE ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES TO ROLE DEDUPE_WORKFLOW_USER;
GRANT INSERT ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.MERGE_ACTIONS TO ROLE DEDUPE_WORKFLOW_USER;

-- Grant future table permissions
GRANT SELECT ON FUTURE TABLES IN SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_USER;

-- ============================================================================
-- Create Admin Role
-- ============================================================================

CREATE ROLE IF NOT EXISTS DEDUPE_WORKFLOW_ADMIN;

-- Admin gets all user permissions plus more
GRANT ROLE DEDUPE_WORKFLOW_USER TO ROLE DEDUPE_WORKFLOW_ADMIN;

-- Admin can modify all tables
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_ADMIN;
GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_ADMIN;

-- Admin can create objects
GRANT CREATE TABLE ON SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_ADMIN;
GRANT CREATE VIEW ON SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA TO ROLE DEDUPE_WORKFLOW_ADMIN;

-- ============================================================================
-- Streamlit App Permissions
-- ============================================================================

-- Grant warehouse usage (required for Streamlit apps)
-- Replace MY_WAREHOUSE with your warehouse name
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DEDUPE_WORKFLOW_USER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DEDUPE_WORKFLOW_ADMIN;

-- ============================================================================
-- Assign Roles to Users (Customize as needed)
-- ============================================================================

-- Example: Grant role to specific users
-- GRANT ROLE DEDUPE_WORKFLOW_USER TO USER agent_user1;
-- GRANT ROLE DEDUPE_WORKFLOW_USER TO USER agent_user2;
-- GRANT ROLE DEDUPE_WORKFLOW_ADMIN TO USER admin_user;

-- Example: Grant roles to existing role hierarchy
-- GRANT ROLE DEDUPE_WORKFLOW_USER TO ROLE SYSADMIN;
-- GRANT ROLE DEDUPE_WORKFLOW_ADMIN TO ROLE SYSADMIN;

-- ============================================================================
-- Verify Permissions
-- ============================================================================

SHOW GRANTS ON SCHEMA DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA;
SHOW GRANTS ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.CUSTOMERS;
SHOW GRANTS ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.DUPLICATE_CANDIDATES;
SHOW GRANTS ON TABLE DEDUPE_WORKFLOW_DB.DEDUPE_SCHEMA.AGENT_DECISIONS;

SELECT 'Permissions setup complete!' AS STATUS;
