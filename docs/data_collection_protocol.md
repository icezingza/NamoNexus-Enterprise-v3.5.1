# Data Collection Protocol (Pilot)

## Purpose
Define what data to collect during the 1323 pilot, how to collect it, and how to store and report it under PDPA.

## What to Collect (Per Call)
- Timestamp
- Caller ID (pseudonymized)
- AI triage tier (0-3)
- Counselor approval time
- Response accuracy (Y/N)
- User satisfaction (1-10)
- Escalation outcome (if Tier 2-3)
- Safety issues (any?)
- Counselor notes

## How to Collect
- Automatic logging (system-generated).
- Manual survey (post-call, 30 sec).
- Weekly counselor feedback (15 min).
- Monthly supervisor review (1 hour).

## Storage and Governance
- Pseudonymized in database.
- Encrypted at rest.
- Access logging enabled.
- Retention: 6 months pilot.
- PDPA consent documented.

## Weekly Report (Friday)
- Total calls processed
- Triage distribution (Tier 0-3)
- Average accuracy
- Escalation time
- Issues found
- User satisfaction average
- Counselor sentiment

## Quality Gates
- >= 50 calls/week (data volume)
- >= 80% counselor adoption (usage)
- >= 85% accuracy (quality)
- 100% escalation success (safety)
- Zero critical issues (reliability)

## Data Template (Per Call)
| Field | Example |
| --- | --- |
| Timestamp | 2025-02-07 14:25 |
| Caller ID | PSEUDO-1234 |
| Triage Tier | 2 |
| Approval Time (sec) | 45 |
| Accuracy (Y/N) | Y |
| Satisfaction (1-10) | 8 |
| Escalation Outcome | Supervisor review completed |
| Safety Issues | None |
| Counselor Notes | Caller calmer after guidance |

## Roles
- Data owner: pilot operations lead.
- Data steward: compliance lead.
- Report owner: supervisor on duty.

## Next Steps
- Confirm PDPA consent language.
- Validate logging fields with ops team.
