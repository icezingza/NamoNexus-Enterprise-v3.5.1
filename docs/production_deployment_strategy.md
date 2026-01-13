# Production Deployment Strategy

## Deployment Decision Matrix

### Option 1: Cloud Run (Recommended for Pilot)
Pros:
- Fast deployment (< 1 hour)
- Auto-scaling
- Pay-per-use (cost-effective for pilot)
- Minimal ops overhead

Cons:
- Cold start latency (1-2s)
- Vendor lock-in
- Data residency concerns for government

Use Case: 1323 pilot, private hospital proof

Cost: ~13K THB/month for 1M calls

### Option 2: On-Premise (Required for Government)
Pros:
- Full data control
- PDPA compliance easier
- No cold starts
- Predictable costs at scale

Cons:
- High upfront cost (300-400K THB)
- Requires ops team
- Slower iteration

Use Case: government contracts, DMH partnership

Cost: 10K THB/month + 300K setup

## Pre-Deployment Checklist

### Code and Tests
- [ ] Code cleanup completed (research modules archived)
- [ ] Test coverage >= 80%
- [ ] All safety tests passing
- [ ] Performance benchmarks meet targets
- [ ] Security audit completed

### Configuration
- [ ] Environment variables documented
- [ ] Secrets management configured (no secrets in code)
- [ ] Feature flags defined
- [ ] Rate limiting configured
- [ ] CORS origins whitelisted

### Monitoring
- [ ] Logging configured (structured JSON)
- [ ] Metrics endpoint working
- [ ] Alerting rules defined
- [ ] Dashboard created (latency, errors, triage distribution)
- [ ] Incident response plan documented

### Safety and Compliance
- [ ] Escalation SLA documented
- [ ] Supervisor queue tested
- [ ] Audit logs enabled
- [ ] PDPA consent flow validated
- [ ] Emergency shutdown procedure ready

### Disaster Recovery
- [ ] Backup strategy defined
- [ ] RTO/RPO documented
- [ ] Failover procedure tested
- [ ] Database backup verified

## Deployment Phases

### Phase 0: Staging (Week 1)
Goal: Validate everything works.
- Deploy to staging environment
- Run smoke tests
- Invite 5 internal testers
- Fix critical issues

### Phase 1: Alpha (Week 2-3)
Goal: Limited production exposure.
- Deploy to production with feature flag
- 10 calls/day max
- Manual monitoring every hour
- Daily team debrief

### Phase 2: Beta (Week 4-6)
Goal: Controlled scale-up.
- 50-100 calls/day
- Automated monitoring
- Weekly review
- Collect metrics for go/no-go decision

### Phase 3: Production (Week 7+)
Goal: Full deployment.
- Remove rate limits
- 24/7 monitoring
- On-call rotation
- Monthly review

## Success Metrics (Go/No-Go Gates)

| Metric | Alpha Target | Beta Target | Production Target |
| --- | --- | --- | --- |
| Uptime | 95% | 99% | 99.5% |
| Response time (p95) | < 5s | < 3s | < 2s |
| Triage accuracy | >= 85% | >= 90% | >= 92% |
| Escalation success | 100% | 100% | 100% |
| False negative rate | < 5% | < 3% | < 2% |
| User satisfaction | >= 6/10 | >= 7/10 | >= 8/10 |

## Benchmark Monitoring (Runtime)

### Step 1: Check current metrics

JSON metrics:
```bash
curl http://localhost:8000/metrics
```

Prometheus metrics:
```bash
curl -H "Accept: text/plain" http://localhost:8000/metrics
```

Focus on:
- p50/p95/p99 latency
- error counts
- request volume and RPS

Example JSON:
```json
{
  "status": "ok",
  "latency": {
    "p50_ms": 102.5,
    "p95_ms": 298.3,
    "p99_ms": 445.8,
    "avg_ms": 134.7,
    "errors": 2,
    "requests": 156,
    "rps": 0.0433
  }
}
```

### Step 2: Check health and readiness

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
curl http://localhost:8000/health
```

Example readiness response:
```json
{
  "status": "ready",
  "components": {
    "collective": {"status": "ok"},
    "simulation": {"status": "ok"}
  },
  "metrics": {
    "latency": {
      "p95_ms": 287.4,
      "p99_ms": 412.1
    }
  }
}
```

### Benchmark degradation signals and fixes

| Problem | Signal | Mitigation |
| --- | --- | --- |
| Slow database | p95/p99 latency increases | Add indexes, optimize queries |
| Memory leak | CPU/Memory climbs | Profile code, track leaks |
| High error rate | errors > 2% | Review logs, fix failing endpoints |
| Concurrent load | latency spikes at peak | Add caching, load balancing |
| Network issues | timeouts rise | Check connection pools |

## Post-Deployment Actions

### Daily (First Week)
- Review all escalations
- Check error logs
- Monitor latency
- User feedback review

### Weekly (First Month)
- Triage accuracy analysis
- Safety incident review
- Performance optimization
- Feature prioritization

### Monthly (Ongoing)
- Business metrics review
- Cost optimization
- Roadmap alignment
- Team retrospective

## Emergency Response

### Critical Issues (Act Immediately)
- False negative in Tier 3 detection
- System down > 5 minutes
- Data breach or PDPA violation
- Escalation failure

Response:
1. Activate incident commander
2. Enable manual fallback
3. Notify stakeholders
4. Root cause analysis within 24h
5. Post-mortem within 1 week

### Non-Critical Issues (Fix Within 24h)
- High latency spikes
- Minor accuracy degradation
- UI/UX issues
- Documentation errors

## Contacts and Escalation

Technical Lead: [Name, Phone]

Clinical Lead: [Name, Phone]

On-Call Engineer: [Rotation Schedule]

1323 Director: [Name, Phone]

Escalation Path:
1. Engineer on duty -> Technical Lead
2. Technical Lead -> Clinical Lead
3. Clinical Lead -> 1323 Director
4. Director -> DMH Leadership (if needed)
