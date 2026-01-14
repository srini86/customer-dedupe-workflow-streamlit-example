# Dedupe Workflow: SharePoint/PowerApps vs Snowflake/Streamlit

## Executive Summary

This document compares the current SharePoint/PowerApps architecture with a proposed Snowflake/Streamlit solution for the Dedupe Workflow Tool.

---

## Architecture Comparison

### Current State: SharePoint + PowerApps
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Warehouse │────▶│   SharePoint    │◀───▶│    PowerApps    │
│     (Source)    │     │  (Lists/Data)   │     │  (Frontend UI)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        Access Control via
                        SharePoint Groups
```

### Proposed State: Snowflake + Streamlit
```
┌─────────────────┐     ┌─────────────────────────────────────────┐
│  Data Warehouse │────▶│              Snowflake                  │
│     (Source)    │     │  ┌─────────────┐    ┌────────────────┐  │
└─────────────────┘     │  │   Tables    │◀──▶│   Streamlit    │  │
                        │  │   (Data)    │    │   (Frontend)   │  │
                        │  └─────────────┘    └────────────────┘  │
                        │         │                               │
                        │    Snowflake RBAC                       │
                        └─────────────────────────────────────────┘
```

---

## Detailed Comparison

### ✅ Advantages of Snowflake/Streamlit

| Category | Benefit | Details |
|----------|---------|---------|
| **Data Proximity** | Zero data movement | Data stays in Snowflake; no ETL to SharePoint required |
| **Real-time Sync** | Always current | Queries directly against warehouse; no sync delays |
| **Performance** | Fast queries | Leverages Snowflake's compute power; scales automatically |
| **Data Governance** | Single source of truth | All data and decisions in one platform |
| **Security** | Unified RBAC | Snowflake's enterprise security model |
| **Audit Trail** | Native tracking | Complete audit trail in same database |
| **Cost** | No additional licensing | Streamlit is included with Snowflake |
| **Development** | Python-based | Easier to find developers; more flexible |
| **Analytics** | Integrated reporting | Direct SQL access for dashboards and reports |
| **Scalability** | Elastic compute | Handles any volume without architecture changes |

### ⚠️ Considerations & Potential Challenges

| Category | Consideration | Mitigation |
|----------|---------------|------------|
| **User Experience** | Streamlit UI is functional but less polished than PowerApps | Custom CSS and components can enhance UX |
| **Offline Access** | Requires network connectivity | PowerApps also requires connectivity for SharePoint |
| **Learning Curve** | Team needs Snowflake/Python skills | Training investment required |
| **Mobile Support** | Streamlit mobile experience is basic | Responsive design helps; mobile app possible later |
| **SSO Integration** | May need configuration | Snowflake supports SAML/OAuth |
| **Change Management** | Users familiar with PowerApps | Phased rollout with training recommended |

---

## Feature Comparison Matrix

| Feature | SharePoint/PowerApps | Snowflake/Streamlit |
|---------|---------------------|---------------------|
| Data Storage | SharePoint Lists | Snowflake Tables |
| Frontend Framework | PowerApps (Low-code) | Streamlit (Python) |
| Data Sync | ETL required | Native (same platform) |
| Real-time Data | Delayed sync | Real-time queries |
| Custom Logic | Power Fx | Python |
| Integrations | Power Platform | Snowflake ecosystem |
| Version Control | Limited | Git-native |
| Testing | Manual | Automated possible |
| Deployment | Power Platform Admin | Snowflake deployment |
| Monitoring | Power Platform analytics | Snowflake Query History |
| Cost Model | Per-user licensing | Consumption-based |

---

## Cost Analysis

### Current: SharePoint + PowerApps
- SharePoint licenses (typically included with M365)
- PowerApps per-user or per-app licenses
- Data transfer costs (to SharePoint)
- Maintenance overhead for sync processes

### Proposed: Snowflake + Streamlit
- Snowflake compute costs (queries + Streamlit)
- No additional software licensing
- Reduced data transfer (data stays in Snowflake)
- Lower maintenance (no sync processes)

**Note**: Streamlit in Snowflake is included with Snowflake licensing. The primary cost is compute time for running the app.

---

## Security Comparison

### SharePoint/PowerApps
- SharePoint groups for access control
- Separate identity management
- Data exported outside Snowflake
- Complex audit across systems

### Snowflake/Streamlit
- Snowflake RBAC (roles, privileges)
- SSO via SAML/OAuth
- Data never leaves Snowflake
- Unified audit trail
- Row-level security possible
- Column-level masking available

---

## Implementation Approach

### Recommended Phases

**Phase 1: Proof of Concept (2-4 weeks)**
- Deploy demo app with sample data
- User acceptance testing with subset of agents
- Validate performance and usability

**Phase 2: Pilot (4-6 weeks)**
- Connect to real duplicate candidates
- Limited rollout to select agents
- Collect feedback and iterate

**Phase 3: Production (4-6 weeks)**
- Full migration
- Parallel running with existing system
- Complete cutover

**Phase 4: Enhancement (Ongoing)**
- Additional features (auto-merge, ML scoring)
- Reporting and analytics
- Integration with other workflows

---

## Technical Requirements

### Snowflake
- Database for application tables
- Warehouse for Streamlit app
- Appropriate roles and permissions

### Streamlit App
- Python 3.8+
- Snowpark library
- Custom UI components

### Network
- Users need access to Snowflake URL
- Standard HTTPS traffic (port 443)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User adoption resistance | Medium | High | Training, phased rollout |
| Performance issues | Low | Medium | Proper warehouse sizing |
| Data migration errors | Low | High | Testing, validation scripts |
| Integration gaps | Medium | Medium | API development if needed |

---

## Recommendation

**We recommend proceeding with a Proof of Concept** using the provided demo application. This allows the team to:

1. Evaluate the user experience firsthand
2. Test with realistic data volumes
3. Assess performance characteristics
4. Identify any missing requirements
5. Make an informed decision with concrete evidence

The demo application includes:
- Complete workflow functionality
- Sample Fiji customer data
- Agent decision recording
- Audit trail tracking
- Dashboard and reporting views

---

## Questions for Discussion

1. What is the current user count for the PowerApps application?
2. Are there specific PowerApps features that are critical to retain?
3. What is the current data sync frequency from warehouse to SharePoint?
4. Are there mobile/offline requirements?
5. What is the timeline expectation for migration?
6. Are there other workflows that could benefit from consolidation?

---

## Next Steps

1. Review this comparison document
2. Schedule demo of the Streamlit application
3. Discuss specific requirements and concerns
4. Define success criteria for POC
5. Plan POC timeline and resources
