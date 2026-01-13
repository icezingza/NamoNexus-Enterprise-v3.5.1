# API Monetization Strategy

Audience: 3rd-party app developers and platform partners  
Purpose: Define pricing, tiers, and go-to-market for NamoNexus APIs.

## API Monetization Overview

Target customers: 3rd-party app developers building mental health and wellness features.

Primary use cases:

- Dating apps (Bumble-style): mental health check-ins
- HR apps (Workday-style): employee wellness screening
- Gaming apps: player mental state detection
- Telemedicine platforms: patient pre-screening
- Insurance companies: risk assessment and benefit offers

## API Credit System

### Pricing Model

- Base unit: 1 API call = 1 interaction
- Billing: per-call, monthly invoice
- Minimum: 1,000 credits/month
- Payment: credit card or bank transfer

### Tier 1: Startup / Early-Stage

- Name: Developer
- Monthly credits: 10,000 (10K calls)
- Price per credit: 0.5 THB
- Monthly cost: 5,000 THB (50K THB for 100K calls)
- Best for: apps <100K users, testing phase
- SLA: 99% uptime (non-critical)
- Support: email + community forum
- Onboarding: self-serve documentation

### Tier 2: Growing Business

- Name: Professional
- Monthly credits: 100,000 (100K calls)
- Price per credit: 0.4 THB
- Monthly cost: 40,000 THB base + overage
- Best for: apps 100K-1M users
- SLA: 99.5% uptime + 1-hour response
- Support: email + Slack channel + monthly check-in
- Onboarding: dedicated integration engineer (first month free)
- Features: advanced analytics, custom dashboards

### Tier 3: Enterprise

- Name: Enterprise
- Monthly credits: 500,000+ (custom)
- Price per credit: 0.3 THB (or negotiated)
- Monthly cost: 150,000 THB base + custom
- Best for: apps >1M users, mission-critical
- SLA: 99.9% uptime + 30-min response
- Support: dedicated account manager + 24/7 phone
- Onboarding: full integration project (dedicated team)
- Features: custom integrations, white-label options, priority roadmap

### Tier 4: Bulk / Government

- Name: Government/Bulk
- Monthly credits: 1M+ (custom negotiation)
- Price per credit: 0.1-0.25 THB (volume discount)
- Monthly cost: custom (100K-500K+ THB)
- Best for: government agencies, large platforms
- SLA: custom (up to 99.99%)
- Support: dedicated team + custom SLA
- Onboarding: full project management
- Features: on-premise option, data residency, custom compliance

## Pricing Summary Table

| Tier | Monthly Credits | Price/Credit | Base Monthly | Best For | SLA |
| --- | --- | --- | --- | --- | --- |
| Developer | 10K | 0.5 THB | 5,000 THB | <100K users | 99% |
| Professional | 100K | 0.4 THB | 40,000 THB | 100K-1M users | 99.5% |
| Enterprise | 500K+ | 0.3 THB | 150,000 THB | >1M users | 99.9% |
| Government | 1M+ | 0.1-0.25 THB | 100K-500K+ THB | National programs | Custom |

## API Call Examples and Credit Costs

| Use Case | Calls/Month | Tier | Cost/Month |
| --- | --- | --- | --- |
| Dating app (100K users) | 50K | Developer | 25K THB |
| HR wellness (500K employees) | 200K | Professional | 80K THB |
| Insurance risk (1M policies) | 500K | Enterprise | 150K THB |
| Government (all provinces) | 1M+ | Government | Custom |

## Revenue Projection (API Monetization)

### Year 1

- 10 API customers (Developer tier)
- 500K calls/month total
- Revenue: 50K-100K THB/month
- Annual: 600K-1.2M THB

### Year 2

- 30 API customers (mixed tier)
- 3M calls/month total
- Revenue: 300K-500K THB/month
- Annual: 3.6M-6M THB

### Year 3

- 50+ API customers
- 10M+ calls/month total
- Revenue: 1M+ THB/month
- Annual: 12M+ THB

## Go-to-Market (API Channel)

### Developer Relations

- Slack community for API customers
- Monthly API office hours (live Q&A)
- API documentation portal + sandbox environment
- Code samples (Node.js, Python, Go)
- Blog posts on integration best practices

### Partner Program

- Referral commission: 20% of first-year revenue
- Co-marketing: feature partner apps in blog + newsletter
- Revenue share: high-volume partners (10M+ calls/year)
- White-label options for enterprise partners

### Pricing Psychology

- Highlight per-call cost (0.3-0.5 THB)
- Free trial: 10K credits in first month
- Annual prepay discount: 15-20%
- Multi-year or enterprise annual commitment: 25-30% discount
- Clear scale path without renegotiation

## API Rate Limits and Anti-Abuse

| Tier | Requests/Sec | Burst | Monthly Cap |
| --- | --- | --- | --- |
| Developer | 10 | 100 | 10M |
| Professional | 100 | 1,000 | 100M |
| Enterprise | Custom | Custom | Unlimited |
| Government | Custom | Custom | Unlimited |

## Integration Examples

### Dating App Integration

```json
POST /api/mental-health-check
{
  "text": "I'm feeling anxious",
  "user_id": "bumble_user_123"
}
```

```json
{
  "tier": 1,
  "response": "That sounds tough. You're not alone.",
  "recommendation": "Consider talking to someone you trust."
}
```

Cost: 1 credit per call (0.5 THB in Developer tier).

### HR App Integration

```json
POST /api/employee-wellness
{
  "text": "Feeling unmotivated today",
  "user_id": "hr_emp_456"
}
```

```json
{
  "wellness_score": 6,
  "recommendation": "Take a short break and check in with your EAP."
}
```

Volume example: 500 employees x 20 days/month = 10K calls  
Monthly cost: ~4K THB (Professional tier rate).

### Insurance Integration

```json
POST /api/risk-assessment
{
  "symptom_data": ["sleep_issues", "low_mood"],
  "user_profile": {"age": 35, "region": "TH-10"}
}
```

```json
{
  "risk_tier": 2,
  "recommendation": "Offer mental health benefit and follow-up."
}
```

Cost: 0.3 THB per call (Enterprise tier).  
Volume example: 1M policies quarterly = 250K calls/month.

## Support and SLA by Tier

| Tier | Response Time | Uptime SLA | Dedicated Support |
| --- | --- | --- | --- |
| Developer | 48 hours | 99% | Community only |
| Professional | 4 hours | 99.5% | Email + Slack |
| Enterprise | 1 hour | 99.9% | Account manager |
| Government | 30 min | 99.99% | Dedicated team |

## Compliance and Data Handling

### Data Privacy (PDPA)

- All API calls pseudonymized
- No PII stored beyond 30 days (configurable)
- Data residency in Thailand (enterprise option)
- Audit logs available for compliance review

### Security

- API keys + OAuth2 authentication
- Rate limiting + DDoS protection
- Encryption in transit (TLS) and at rest
- Monthly security audit

### Compliance Certifications (Roadmap)

- ISO 27001 (information security)
- PDPA compliance (Thai data protection)
- SOC 2 Type II (enterprise readiness)

## Billing and Invoicing

- Real-time usage dashboard (credit consumption)
- Monthly automated invoices
- Overage alerts at 80% of monthly credits
- Prepaid credits with 10-20% discount
- Annual commitment discounts available

## Success Metrics (API Channel)

| Metric | Year 1 Target | Year 2 Target | Year 3 Target |
| --- | --- | --- | --- |
| API customers | 10 | 30 | 50+ |
| Monthly API calls | 500K | 3M | 10M+ |
| API revenue | 50-100K THB | 300-500K THB | 1M+ THB |
| API adoption rate | 5% of customers | 20% | 40%+ |

## Go-Live Plan (API Monetization)

| Timeline | Milestone |
| --- | --- |
| Month 8 | API documentation + sandbox ready |
| Month 9 | Soft launch (10 beta partners) |
| Month 10 | Public launch + pricing page |
| Month 12 | 10+ paying API customers |
| Month 18 | 30+ customers, 1M+ calls/month |

## Risk Mitigation (API Channel)

- Risk: API abuse or unpaid high-volume usage  
  Mitigation: rate limiting + prepaid credits requirement
- Risk: Data privacy incident on partner app  
  Mitigation: clear T&Cs, audit rights, liability caps
- Risk: Poor integrations hurt reputation  
  Mitigation: integration review process and quality checklist
- Risk: Low adoption  
  Mitigation: free trial, referral incentives, and co-marketing

## Next Steps

- Approve tier pricing and discount policy.
- Publish API documentation and sandbox.
- Recruit 10 beta partners for Month 9 soft launch.
