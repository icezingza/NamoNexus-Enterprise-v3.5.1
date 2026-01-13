# Infrastructure and Hardware Specs

Purpose: Define deployment options, sizing guidance, and cost expectations for NamoNexus.  
Audience: Technical leadership, IT, and procurement.

## NamoNexus Infrastructure Overview

- Deployment model: cloud-native (Cloud Run) + on-premise option
- Scalability: horizontal (add instances, do not upgrade single nodes)
- Cost structure: OpEx, pay-per-use where possible

## Single Instance Specifications

### Compute Requirements (Per Instance)

#### Recommended (Production)

- CPU: 4 vCPU (2.4-3.6 GHz)
- RAM: 16 GB
- GPU: optional (1x NVIDIA T4 for inference acceleration)
- Storage: 50 GB SSD
- Network: 1 Gbps

#### Minimum (Testing/Development)

- CPU: 2 vCPU
- RAM: 8 GB
- GPU: none (CPU inference acceptable)
- Storage: 20 GB SSD
- Network: 100 Mbps

#### High-Performance (Large Enterprise)

- CPU: 8 vCPU (Intel Xeon or AMD EPYC)
- RAM: 32 GB
- GPU: 2x NVIDIA A100 (batch processing)
- Storage: 500 GB SSD + 1 TB HDD (archive)
- Network: 10 Gbps

### Performance Metrics (Per Instance)

| Metric | Minimum | Recommended | High-Perf |
| --- | --- | --- | --- |
| Concurrent users | 50 | 200 | 1000+ |
| Requests/sec | 10 | 50 | 200+ |
| Avg latency | <3 sec | <1 sec | <0.5 sec |
| Peak throughput | 100 req/min | 1000 req/min | 10K+ req/min |
| Uptime SLA | 99% | 99.5% | 99.9%+ |

## Deployment Options and Costs

### Option 1: Cloud Run (Google Cloud) - Recommended

#### Setup

- Container: Docker image (~500 MB)
- Runtime: Python 3.11 + FastAPI
- Database: Cloud SQL (PostgreSQL)
- Vector store: Pinecone (external, optional)

#### Pricing (Per Month)

- Compute: ~10K THB (1M invocations/month)
- Database: ~2K THB (Cloud SQL small instance)
- Storage: ~500 THB (50 GB)
- Network: ~500 THB (egress traffic)
- Total: ~13K THB/month (single instance)

#### Scaling (Estimate)

- 100K calls/month: ~1.3K THB
- 1M calls/month: ~13K THB
- 10M calls/month: ~130K THB (auto-scales horizontally)
- 100M calls/month: ~1.3M THB (multi-region)

#### Pros

- Auto-scaling (no manual intervention)
- Pay-per-use (no waste)
- Low ops overhead
- Built-in logging and monitoring

#### Cons

- Vendor lock-in (Google)
- Cold start latency (1-2 sec after idle)
- Cost can spike with traffic

### Option 2: Self-Hosted (On-Premise)

#### Hardware Cost (One-Time)

- Server: 150K THB (dedicated physical server)
- GPU: 100K THB (NVIDIA T4, optional)
- Network: 50K THB (setup)
- Installation: 50K THB (labor)
- Total: 300-400K THB (setup)

#### Monthly Operating Cost

- Electricity: 2K THB
- Network: 5K THB
- Maintenance: 2K THB
- Backup: 1K THB
- Total: 10K THB/month

#### Capacity

- 1 instance: ~200 concurrent users, 50 req/sec
- 5 instances: ~1000 concurrent users, 250 req/sec
- Cost for 5 instances: ~20K THB/month (power and ops)

#### Pros

- No vendor lock-in
- Full control
- Data residency (PDPA compliant)
- Lower marginal cost at scale

#### Cons

- High upfront capital cost
- Requires ops team (maintenance and monitoring)
- Less elastic scaling (physical limits)

### Option 3: Hybrid (Cloud + On-Premise)

#### Setup

- Primary: Cloud Run (scale and bursts)
- Secondary: on-premise (data residency and compliance)
- Sync: real-time replication between regions

#### Cost

- Cloud Run: 10-50K THB/month (variable load)
- On-premise: 10K THB/month (fixed baseline)
- Total: 20-60K THB/month

#### Best For

- Government contracts (data residency requirement)
- Large enterprises (redundancy + compliance)
- Growing platforms (scale with flexibility)

## Cost Per Deployment Scenario

### Scenario 1: 1323 Hotline Pilot (10K calls/month)

- Deployment: Cloud Run
- Instance: Recommended (4 vCPU, 16 GB RAM)
- Monthly cost: 1.5K THB (compute)
- Plus: 2K THB (database, storage, network)
- Total: 3.5K THB/month
- Cost per call: 0.35 THB

### Scenario 2: 5 Private Hospitals (100K calls/month)

- Deployment: Cloud Run + on-premise backup
- Instances: 2 instances (recommended tier)
- Monthly cost: 15K THB (Cloud Run)
- Plus: 10K THB (on-premise)
- Total: 25K THB/month
- Cost per call: 0.25 THB

### Scenario 3: National Scale (1M calls/month)

- Deployment: multi-cloud (Cloud Run + AWS + Azure)
- Instances: 10+ instances (auto-scaled)
- Monthly cost: 150K THB (compute)
- Plus: 30K THB (database, network, monitoring)
- Total: 180K THB/month
- Cost per call: 0.18 THB

### Scenario 4: Government (10M calls/month)

- Deployment: hybrid (cloud + on-premise + regional)
- Instances: 50+ instances (auto-scaled)
- Monthly cost: 1.5M THB (compute)
- Plus: 300K THB (database, network, ops team)
- Total: 1.8M THB/month
- Cost per call: 0.18 THB
- Note: cost per call decreases at scale

## Database and Storage Requirements

### Primary Database (PostgreSQL)

- Size: 1 GB per 100K interactions (log storage)
- Growth: ~1 GB/month (volume dependent)
- Backup: daily snapshots (1 month retention)
- Cost (Cloud SQL small): ~2K THB/month

### Vector Store (Optional, for Memory)

- Pinecone: ~$70/month (~2,500 THB) base
- Self-hosted: ~500 THB/month (vectordb on server)
- Size: ~100 MB per 10K conversations

### Audit Logs and Compliance

- Retention: 2 years (regulatory)
- Size: 5 GB per 1M interactions
- Storage cost: 500-1K THB/month (archive tier)

## Network and Bandwidth

### Egress Bandwidth Costs

- Cloud Run egress: ~0.1 THB per GB
- Typical usage: 100-500 MB per 1M calls
- Monthly egress (1M calls): ~50 THB
- Most intra-cloud traffic is free

### CDN (Optional)

- Cloudflare CDN: ~10 THB/month
- Benefit: lower latency for external users
- Expected improvement: 30-50% latency reduction

## GPU Acceleration (Optional)

### When to Add GPU

- If average latency >2 sec on CPU only
- If batch processing thousands of calls/sec
- For advanced NLP models with heavy inference

### GPU Options

- NVIDIA T4: 100K THB one-time + 5K THB/month
- NVIDIA A100: 500K THB one-time + 20K THB/month
- Cloud GPU: ~500 THB/hour (pay-per-use)

### Speed Improvement

- CPU only: 1-3 sec/call
- T4 GPU: 0.5-1 sec/call (50% faster)
- A100 GPU: 0.1-0.3 sec/call (90% faster)

## Monitoring and Observability

### Tools Needed

- Application monitoring: Datadog (~5K THB/month)
- Log aggregation: ELK stack (~2K THB/month)
- Uptime monitoring: StatusPage.io (~1K THB/month)
- Error tracking: Sentry (~2K THB/month)
- Total: ~10K THB/month

### Key Metrics Tracked

- Response latency (p50, p95, p99)
- Error rate (5xx, 4xx, timeouts)
- Database query time
- Memory usage and CPU utilization
- Concurrent connections
- API credit usage

## Disaster Recovery and Backup

### Backup Strategy

- Database: daily snapshots + point-in-time recovery
- Code: Git repository
- Configuration: version controlled
- RTO: 1 hour
- RPO: 1 hour

### Cost

- Backup storage: ~1K THB/month
- DR testing: ~2K THB/month (labor)
- Total: ~3K THB/month

## Security Infrastructure

### Network Security

- WAF: ~5K THB/month
- DDoS protection: ~3K THB/month
- VPN/tunneling: ~1K THB/month
- Total: ~9K THB/month

### Compliance Infrastructure

- TLS/SSL: included (Lets Encrypt)
- Secret management: HashiCorp Vault (~3K THB/month)
- Audit logging: ~2K THB/month
- Compliance scanning: ~1K THB/month
- Total: ~6K THB/month

## Total Cost of Ownership (TCO)

### Year 1 (Pilot Phase, 100K calls/month)

- Infrastructure: 25K x 12 = 300K THB
- Monitoring + observability: 10K x 12 = 120K THB
- Security + compliance: 15K x 12 = 180K THB
- Backup + DR: 3K x 12 = 36K THB
- Ops team (1 person): 500K THB
- Total Year 1: ~1.1M THB

### Year 2 (Growth Phase, 1M calls/month)

- Infrastructure: 180K x 12 = 2.2M THB
- Monitoring + observability: 12K x 12 = 144K THB
- Security + compliance: 20K x 12 = 240K THB
- Backup + DR: 5K x 12 = 60K THB
- Ops team (2 people): 1.0M THB
- Total Year 2: ~3.6M THB

### Year 3 (Scale Phase, 10M calls/month)

- Infrastructure: 1.8M x 12 = 21.6M THB
- Monitoring + observability: 15K x 12 = 180K THB
- Security + compliance: 30K x 12 = 360K THB
- Backup + DR: 10K x 12 = 120K THB
- Ops team (3 people): 1.5M THB
- Total Year 3: ~23.7M THB

## OpEx vs Revenue Analysis

| Phase | Monthly OpEx | Monthly Revenue | Margin |
| --- | --- | --- | --- |
| Pilot (100K calls) | 25K THB | 50-100K THB | 50-75% |
| Growth (1M calls) | 180K THB | 300-500K THB | 40-60% |
| Scale (10M calls) | 1.8M THB | 1.5-2M THB | 20-30% |

## Recommendations

### Startups (0-100K calls/month)

- Use: Cloud Run (Google Cloud)
- Cost: 3-5K THB/month
- Focus: product-market fit

### Growth (100K-1M calls/month)

- Use: Cloud Run primary, monitor for on-premise needs
- Cost: 15-50K THB/month
- Consider hybrid if government contracts appear

### Scale (1M+ calls/month)

- Use: multi-cloud (Cloud Run + AWS + on-premise)
- Cost: 180K-1.8M THB/month
- Focus: cost per call and regional resiliency

### Government (10M+ calls/month)

- Use: hybrid (on-premise primary + cloud backup)
- Cost: 1.8M+ THB/month
- Focus: data sovereignty, compliance, redundancy

## Next Steps

- Confirm deployment scenario and target call volume.
- Select cloud vs on-premise baseline for procurement.
- Finalize monitoring, security, and DR tooling.
