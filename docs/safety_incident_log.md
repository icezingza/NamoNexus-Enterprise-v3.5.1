# Safety Incident Log (Template)

## Incident Report Format
- Date/Time: [When]
- Incident ID: [INC-001]
- Severity: [ ] Minor / [ ] Moderate / [ ] Severe
- Type: [ ] False negative / [ ] False positive / [ ] Latency / [ ] Other
- Description: [What happened]
- Impact: [Who affected, how]
- Root cause: [Why]
- Action taken: [How fixed]
- Prevention: [Won't happen again]
- Closed by: [Name, date]

## Log Entry Template
```text
INC-___ | Date/Time: ___ | Severity: ___ | Type: ___
Description:
Impact:
Root cause:
Action taken:
Prevention:
Closed by:
```

## Examples (Reference)
### Example 1: False Negative
- Caller said "want to die" but AI classified as Tier 1.
- Caught by counselor.
- Policy updated and rule added.

### Example 2: Latency Spike
- Response took 8 sec (target <3 sec).
- Cache misconfiguration found.
- Fixed in 15 min.

### Example 3: Escalation Delay
- Supervisor alert took 45 min (target <15 min).
- Email filter issue.
- Switched to SMS.

## Weekly Safety Review
- All incidents reviewed.
- Trends identified.
- Policies updated if needed.
- Team briefed on learnings.

## Escalation Criteria
- Severity = Severe -> Notify leadership immediately.
- Pattern detected -> Pause system, investigate.
- False negative rate >5% -> Stop deployment, retrain.
