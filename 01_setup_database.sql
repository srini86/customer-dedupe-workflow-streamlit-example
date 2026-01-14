-- ============================================================================
-- DEDUPE WORKFLOW DEMO - Database Setup
-- This script creates the database, schema, and tables for the Dedupe Workflow
-- Streamlit in Snowflake (SiS) demo
-- ============================================================================

-- Create dedicated database and schema
CREATE DATABASE IF NOT EXISTS DEDUPE_WORKFLOW_DB;
USE DATABASE DEDUPE_WORKFLOW_DB;

CREATE SCHEMA IF NOT EXISTS DEDUPE_SCHEMA;
USE SCHEMA DEDUPE_SCHEMA;

-- ============================================================================
-- TABLE 1: CUSTOMERS - Master customer records (simulating data warehouse)
-- ============================================================================
CREATE OR REPLACE TABLE CUSTOMERS (
    CUSTOMER_ID         VARCHAR(20) PRIMARY KEY,
    FIRST_NAME          VARCHAR(100),
    LAST_NAME           VARCHAR(100),
    EMAIL               VARCHAR(255),
    PHONE               VARCHAR(50),
    DATE_OF_BIRTH       DATE,
    ADDRESS_LINE1       VARCHAR(255),
    ADDRESS_LINE2       VARCHAR(255),
    CITY                VARCHAR(100),
    STATE               VARCHAR(50),
    POSTAL_CODE         VARCHAR(20),
    COUNTRY             VARCHAR(50) DEFAULT 'Fiji',
    ACCOUNT_STATUS      VARCHAR(20),
    ACCOUNT_TYPE        VARCHAR(50),
    CREATED_DATE        TIMESTAMP_NTZ,
    LAST_ACTIVITY_DATE  TIMESTAMP_NTZ,
    TOTAL_TRANSACTIONS  NUMBER(10,0),
    ACCOUNT_BALANCE     NUMBER(18,2),
    SOURCE_SYSTEM       VARCHAR(50)
);

-- ============================================================================
-- TABLE 2: DUPLICATE_CANDIDATES - Pairs identified by matching algorithm
-- ============================================================================
CREATE OR REPLACE TABLE DUPLICATE_CANDIDATES (
    CANDIDATE_ID        VARCHAR(36) PRIMARY KEY,
    CUSTOMER_ID_1       VARCHAR(20) NOT NULL,
    CUSTOMER_ID_2       VARCHAR(20) NOT NULL,
    MATCH_SCORE         NUMBER(5,2),           -- Algorithm confidence score (0-100)
    MATCH_REASON        VARCHAR(500),          -- Why algorithm flagged as potential match
    STATUS              VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, MATCHED, NOT_MATCHED, SKIPPED
    PRIORITY            VARCHAR(10) DEFAULT 'MEDIUM',   -- HIGH, MEDIUM, LOW
    CREATED_DATE        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    ASSIGNED_TO         VARCHAR(100),
    FOREIGN KEY (CUSTOMER_ID_1) REFERENCES CUSTOMERS(CUSTOMER_ID),
    FOREIGN KEY (CUSTOMER_ID_2) REFERENCES CUSTOMERS(CUSTOMER_ID)
);

-- ============================================================================
-- TABLE 3: AGENT_DECISIONS - Audit trail of all decisions made
-- ============================================================================
CREATE OR REPLACE TABLE AGENT_DECISIONS (
    DECISION_ID         VARCHAR(36) PRIMARY KEY,
    CANDIDATE_ID        VARCHAR(36) NOT NULL,
    AGENT_NAME          VARCHAR(100) NOT NULL,
    DECISION            VARCHAR(20) NOT NULL,   -- MATCHED, NOT_MATCHED, SKIPPED
    DECISION_REASON     VARCHAR(500),
    NOTES               VARCHAR(1000),
    DECISION_TIMESTAMP  TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    SESSION_ID          VARCHAR(100),
    FOREIGN KEY (CANDIDATE_ID) REFERENCES DUPLICATE_CANDIDATES(CANDIDATE_ID)
);

-- ============================================================================
-- TABLE 4: MERGE_ACTIONS - Track what happens after a match is confirmed
-- ============================================================================
CREATE OR REPLACE TABLE MERGE_ACTIONS (
    MERGE_ID            VARCHAR(36) PRIMARY KEY,
    CANDIDATE_ID        VARCHAR(36) NOT NULL,
    MASTER_CUSTOMER_ID  VARCHAR(20),           -- The surviving record
    MERGED_CUSTOMER_ID  VARCHAR(20),           -- The record being merged
    MERGE_STATUS        VARCHAR(20),           -- PENDING, COMPLETED, FAILED
    MERGE_TIMESTAMP     TIMESTAMP_NTZ,
    MERGED_BY           VARCHAR(100),
    FOREIGN KEY (CANDIDATE_ID) REFERENCES DUPLICATE_CANDIDATES(CANDIDATE_ID)
);

-- ============================================================================
-- TABLE 5: WORKFLOW_CONFIG - Configuration settings
-- ============================================================================
CREATE OR REPLACE TABLE WORKFLOW_CONFIG (
    CONFIG_KEY          VARCHAR(100) PRIMARY KEY,
    CONFIG_VALUE        VARCHAR(500),
    DESCRIPTION         VARCHAR(500),
    LAST_UPDATED        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert default configuration
INSERT INTO WORKFLOW_CONFIG (CONFIG_KEY, CONFIG_VALUE, DESCRIPTION) VALUES
    ('AUTO_ASSIGN_THRESHOLD', '85', 'Match score above which records are auto-assigned for review'),
    ('HIGH_PRIORITY_THRESHOLD', '90', 'Match score above which records are marked high priority'),
    ('MAX_DAILY_ASSIGNMENTS', '50', 'Maximum number of records assigned to single agent per day'),
    ('DECISION_TIMEOUT_HOURS', '48', 'Hours before pending decision is reassigned');

-- ============================================================================
-- Verify tables created
-- ============================================================================
SHOW TABLES;

SELECT 'Database setup complete!' AS STATUS;
