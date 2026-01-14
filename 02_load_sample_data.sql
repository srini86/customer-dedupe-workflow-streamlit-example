-- ============================================================================
-- DEDUPE WORKFLOW DEMO - Sample Data
-- This script populates tables with realistic Fiji customer data
-- ============================================================================

USE DATABASE DEDUPE_WORKFLOW_DB;
USE SCHEMA DEDUPE_SCHEMA;

-- ============================================================================
-- Clear existing data (for re-runs)
-- ============================================================================
TRUNCATE TABLE MERGE_ACTIONS;
TRUNCATE TABLE AGENT_DECISIONS;
TRUNCATE TABLE DUPLICATE_CANDIDATES;
TRUNCATE TABLE CUSTOMERS;

-- ============================================================================
-- INSERT CUSTOMER RECORDS - Mix of unique and potential duplicates
-- ============================================================================

-- Customer Set 1: Clear duplicates (same person, different records)
INSERT INTO CUSTOMERS VALUES
('CUST-001', 'Apisai', 'Naiqama', 'apisai.naiqama@gmail.com', '+679-9234567', '1985-03-15', '45 Victoria Parade', 'Suite 12', 'Suva', 'Central', '99999', 'Fiji', 'ACTIVE', 'Premium', '2019-06-12 10:30:00', '2024-01-10 14:22:00', 234, 15420.50, 'ONLINE'),
('CUST-002', 'Apisai', 'Naiqama', 'a.naiqama@gmail.com', '+679 923 4567', '1985-03-15', '45 Victoria Pde', NULL, 'Suva', 'Central', '99999', 'Fiji', 'ACTIVE', 'Standard', '2021-02-28 09:15:00', '2024-01-08 11:45:00', 45, 2340.00, 'BRANCH'),

-- Customer Set 2: Likely duplicates (typos/variations)
('CUST-003', 'Sera', 'Koroi', 'sera.koroi@hotmail.com', '+679-7891234', '1990-07-22', '123 Waimanu Road', 'Apt 4B', 'Suva', 'Central', '99998', 'Fiji', 'ACTIVE', 'Standard', '2020-01-15 08:00:00', '2024-01-12 16:30:00', 89, 5670.25, 'MOBILE'),
('CUST-004', 'Sarah', 'Koroi', 'sera.koroi@hotmail.com', '+6797891234', '1990-07-22', '123 Waimanu Rd', '4B', 'Suva', 'Central', '99998', 'Fiji', 'DORMANT', 'Standard', '2018-05-20 14:30:00', '2022-06-15 10:00:00', 12, 150.00, 'BRANCH'),

-- Customer Set 3: Possible duplicates (same address, similar names)
('CUST-005', 'Josefa', 'Tuisawau', 'josefa.t@yahoo.com', '+679-8345678', '1978-11-30', '78 Ratu Mara Road', NULL, 'Nausori', 'Central', '99997', 'Fiji', 'ACTIVE', 'Business', '2017-03-10 11:20:00', '2024-01-11 09:15:00', 567, 89500.00, 'BRANCH'),
('CUST-006', 'Joe', 'Tuisawau', 'joe.tuisawau@company.com.fj', '+679-8345679', '1978-11-30', '78 Ratu Mara Road', 'Unit 1', 'Nausori', 'Central', '99997', 'Fiji', 'ACTIVE', 'Personal', '2022-08-05 16:45:00', '2024-01-09 13:20:00', 23, 4500.75, 'ONLINE'),

-- Customer Set 4: Married name change scenario
('CUST-007', 'Lavenia', 'Rabukawaqa', 'lavenia.r@gmail.com', '+679-9567890', '1992-04-18', '56 Kings Road', NULL, 'Ba', 'Western', '99996', 'Fiji', 'ACTIVE', 'Premium', '2018-09-22 10:00:00', '2024-01-10 15:30:00', 345, 28900.00, 'ONLINE'),
('CUST-008', 'Lavenia', 'Cama', 'lavenia.cama@gmail.com', '+679-9567890', '1992-04-18', '56 Kings Road', NULL, 'Ba', 'Western', '99996', 'Fiji', 'ACTIVE', 'Standard', '2023-06-15 14:20:00', '2024-01-12 11:00:00', 18, 3200.50, 'MOBILE'),

-- Customer Set 5: Potential false positive (different people, similar data)
('CUST-009', 'Mohammed', 'Khan', 'mk1975@gmail.com', '+679-7234567', '1975-08-25', '234 Vitogo Parade', NULL, 'Lautoka', 'Western', '99995', 'Fiji', 'ACTIVE', 'Standard', '2019-11-10 09:30:00', '2024-01-08 14:00:00', 156, 12300.00, 'BRANCH'),
('CUST-010', 'Mohammed', 'Khan', 'mohammed.khan.fj@gmail.com', '+679-7234568', '1982-08-25', '236 Vitogo Parade', NULL, 'Lautoka', 'Western', '99995', 'Fiji', 'ACTIVE', 'Business', '2020-04-22 11:15:00', '2024-01-11 16:45:00', 89, 45600.00, 'ONLINE'),

-- Customer Set 6: Same household, different people (false positive)
('CUST-011', 'Adi', 'Vakacegu', 'adi.v@outlook.com', '+679-8901234', '1965-02-14', '89 Sunset Boulevard', NULL, 'Nadi', 'Western', '99994', 'Fiji', 'ACTIVE', 'Premium', '2016-07-18 13:00:00', '2024-01-10 10:30:00', 890, 125000.00, 'BRANCH'),
('CUST-012', 'Mereoni', 'Vakacegu', 'mereoni.v@outlook.com', '+679-8901234', '1968-09-03', '89 Sunset Boulevard', NULL, 'Nadi', 'Western', '99994', 'Fiji', 'ACTIVE', 'Standard', '2018-02-25 15:45:00', '2024-01-09 12:15:00', 234, 18500.00, 'ONLINE'),

-- Customer Set 7: Clear duplicates (system migration issue)
('CUST-013', 'Peni', 'Vuniwaqa', 'peni.vuniwaqa@fnu.ac.fj', '+679-6789012', '1988-12-05', '12 USP Road', 'Laucala Campus', 'Suva', 'Central', '99993', 'Fiji', 'ACTIVE', 'Student', '2020-02-01 08:30:00', '2024-01-12 09:00:00', 34, 890.00, 'ONLINE'),
('CUST-014', 'Peni', 'Vuniwaqa', 'peni.vuniwaqa@fnu.ac.fj', '+679 678 9012', '1988-12-05', '12 USP Road', 'Laucala Bay', 'Suva', 'Central', '99993', 'Fiji', 'ACTIVE', 'Student', '2021-01-15 10:00:00', '2024-01-11 14:30:00', 56, 1250.00, 'MOBILE'),

-- Customer Set 8: Business vs Personal account
('CUST-015', 'Samisoni', 'Bogi', 'sam.bogi@fijitrading.com.fj', '+679-5678901', '1970-06-28', '345 Rodwell Road', 'Floor 3', 'Suva', 'Central', '99992', 'Fiji', 'ACTIVE', 'Business', '2015-04-12 11:00:00', '2024-01-10 16:00:00', 1234, 567000.00, 'BRANCH'),
('CUST-016', 'Samisoni', 'Bogi', 'sambogi@gmail.com', '+679-5678902', '1970-06-28', '67 Domain Road', NULL, 'Suva', 'Central', '99991', 'Fiji', 'ACTIVE', 'Personal', '2019-08-20 14:30:00', '2024-01-12 11:45:00', 78, 8900.00, 'MOBILE'),

-- Additional unique customers for context
('CUST-017', 'Ana', 'Delai', 'ana.delai@gmail.com', '+679-4567890', '1995-01-10', '234 Grantham Road', NULL, 'Suva', 'Central', '99990', 'Fiji', 'ACTIVE', 'Standard', '2022-05-15 09:00:00', '2024-01-11 10:00:00', 45, 3400.00, 'ONLINE'),
('CUST-018', 'Timoci', 'Nayacalevu', 'timoci.n@hotmail.com', '+679-3456789', '1983-09-22', '56 Marine Drive', 'Unit 5', 'Lautoka', 'Western', '99989', 'Fiji', 'ACTIVE', 'Premium', '2018-11-30 16:00:00', '2024-01-10 14:00:00', 234, 45000.00, 'BRANCH'),
('CUST-019', 'Kelera', 'Waqanisau', 'kelera.w@yahoo.com', '+679-2345678', '1991-05-17', '78 Queens Highway', NULL, 'Sigatoka', 'Western', '99988', 'Fiji', 'DORMANT', 'Standard', '2020-07-22 11:30:00', '2023-03-15 09:00:00', 12, 450.00, 'MOBILE'),
('CUST-020', 'Rupeni', 'Caucau', 'rupeni.c@fijisports.com', '+679-1234567', '1986-03-08', '123 Fletcher Road', NULL, 'Nausori', 'Central', '99987', 'Fiji', 'ACTIVE', 'Standard', '2019-02-14 10:00:00', '2024-01-09 15:30:00', 167, 12500.00, 'BRANCH');

-- ============================================================================
-- INSERT DUPLICATE CANDIDATES - Pre-identified potential matches
-- ============================================================================

INSERT INTO DUPLICATE_CANDIDATES (CANDIDATE_ID, CUSTOMER_ID_1, CUSTOMER_ID_2, MATCH_SCORE, MATCH_REASON, STATUS, PRIORITY, CREATED_DATE, ASSIGNED_TO) VALUES
-- High confidence matches
('DC-001', 'CUST-001', 'CUST-002', 95.5, 'Same DOB, similar name, phone number match after normalization, similar address', 'PENDING', 'HIGH', '2024-01-13 08:00:00', NULL),
('DC-002', 'CUST-013', 'CUST-014', 98.2, 'Exact name match, same email, same DOB, phone match after normalization', 'PENDING', 'HIGH', '2024-01-13 08:00:00', NULL),

-- Medium confidence matches
('DC-003', 'CUST-003', 'CUST-004', 82.0, 'Same email, same DOB, similar name (typo detected), similar address', 'PENDING', 'MEDIUM', '2024-01-13 08:00:00', NULL),
('DC-004', 'CUST-005', 'CUST-006', 75.5, 'Same DOB, similar name (nickname match), same address street', 'PENDING', 'MEDIUM', '2024-01-13 08:00:00', NULL),
('DC-005', 'CUST-007', 'CUST-008', 78.0, 'Same phone, same DOB, same address, different last name (potential name change)', 'PENDING', 'MEDIUM', '2024-01-13 08:00:00', NULL),
('DC-006', 'CUST-015', 'CUST-016', 72.0, 'Same name, same DOB, different addresses (business vs personal)', 'PENDING', 'MEDIUM', '2024-01-13 08:00:00', NULL),

-- Lower confidence (potential false positives)
('DC-007', 'CUST-009', 'CUST-010', 65.0, 'Same name, similar address, different DOB years', 'PENDING', 'LOW', '2024-01-13 08:00:00', NULL),
('DC-008', 'CUST-011', 'CUST-012', 58.5, 'Same address, same phone, same last name, different first names', 'PENDING', 'LOW', '2024-01-13 08:00:00', NULL),

-- Some already processed for demo
('DC-009', 'CUST-017', 'CUST-019', 45.0, 'Similar email domain pattern, partial name similarity', 'NOT_MATCHED', 'LOW', '2024-01-10 08:00:00', 'Maria Santos'),
('DC-010', 'CUST-018', 'CUST-020', 42.5, 'Same region, similar account patterns', 'NOT_MATCHED', 'LOW', '2024-01-10 08:00:00', 'John Smith');

-- ============================================================================
-- INSERT SAMPLE AGENT DECISIONS (for previously processed records)
-- ============================================================================

INSERT INTO AGENT_DECISIONS (DECISION_ID, CANDIDATE_ID, AGENT_NAME, DECISION, DECISION_REASON, NOTES, DECISION_TIMESTAMP, SESSION_ID) VALUES
('DEC-001', 'DC-009', 'Maria Santos', 'NOT_MATCHED', 'Different customers', 'Names are completely different, only coincidental email pattern match', '2024-01-10 14:30:00', 'SESSION-001'),
('DEC-002', 'DC-010', 'John Smith', 'NOT_MATCHED', 'Different customers', 'Different DOB, different names, just happen to be in same region', '2024-01-10 15:45:00', 'SESSION-002');

-- ============================================================================
-- Verify data loaded
-- ============================================================================

SELECT 'CUSTOMERS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM CUSTOMERS
UNION ALL
SELECT 'DUPLICATE_CANDIDATES', COUNT(*) FROM DUPLICATE_CANDIDATES
UNION ALL
SELECT 'AGENT_DECISIONS', COUNT(*) FROM AGENT_DECISIONS;

SELECT 'Sample data loaded successfully!' AS STATUS;
