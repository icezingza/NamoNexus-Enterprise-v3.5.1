# Thai FDA SaMD Submission Checklist (CDS, Class 3)

## Scope and Classification
- Class: SaMD Class 3 (Clinical Decision Support, not autonomous).
- Intended use: triage and documentation support with human approval.
- Safety posture: deterministic guardrails plus human-in-the-loop.

## Regulatory Pathway
- Pathway: Thai FDA CSDT (Common Submission Dossier Template).
- Pre-submission consultation recommended to confirm scope and claims.
- Evidence package aligned to Thai FDA SaMD expectations.

## Checklist Table (CSDT-Aligned)
| Area | Required Evidence | Notes |
| --- | --- | --- |
| Device Description | Intended use, clinical scope, limitations | Must state CDS-only, not autonomous |
| Risk Management | ISO 14971 risk analysis, mitigations | Include deterministic guardrails |
| Clinical Evidence | Trial protocol, efficacy data, safety outcomes | Triage accuracy vs human baseline |
| Software Lifecycle | IEC 62304 plan, traceability | Include change control and release notes |
| Verification and Validation | V&V reports, test results | Unit, integration, system tests |
| Cybersecurity | Threat model, controls, patch plan | Include incident response |
| Privacy | PDPA handling, consent process | Data minimization and audit logs |
| Quality System | ISO 13485 QMS readiness | Documented SOPs and audits |

## Required Sections (Summary)
- Device description and intended use.
- Risk management file (ISO 14971).
- Clinical evaluation report (CER).
- Software lifecycle documentation (IEC 62304).
- Verification and validation (V&V) reports.
- Cybersecurity plan (threat model and patching).
- PDPA compliance and consent documentation.
- ISO 13485 QMS readiness evidence.

## Software Documentation (IEC 62304)
- Software development plan and lifecycle processes.
- Requirements and traceability matrix.
- V&V reports and regression testing evidence.
- Configuration management and release notes.

## Safety and Risk (ISO 14971)
- Hazard identification and risk analysis.
- Risk control measures with validation evidence.
- Residual risk assessment and acceptance.
- Post-market monitoring plan.

## Privacy and PDPA
- Minimal data collection and pseudonymization.
- Consent language for CDS support and data retention.
- Access controls and audit logs for all data actions.

## Clinical Evidence
- Trial protocol approved by IRB.
- Primary endpoint: triage accuracy vs human baseline.
- Secondary endpoints: user satisfaction, safety, escalation time.
- Safety outcomes and false negative analysis.

## Cybersecurity
- Threat model and vulnerability assessment.
- Encryption in transit (TLS) and at rest.
- Patch management and security update policy.

## Quality Management (ISO 13485)
- QMS scope definition for SaMD.
- SOPs for development, validation, and change control.
- Internal audits and management review records.

## Timeline (18 Months)
| Milestone | Target |
| --- | --- |
| Month 3 | Planning complete, QMS gap analysis |
| Month 9 | Evidence package with pilot data |
| Month 15 | Draft CSDT dossier ready |
| Month 18 | Submit to Thai FDA |

## Cost Estimate (2-3M THB)
| Cost Item | Range (THB) |
| --- | --- |
| ISO 13485 QMS | 300K-700K |
| Clinical trial | 1M-3M |
| Regulatory consulting | 500K |
| V&V testing | 300K-600K |

## Roles and Ownership
- Regulatory lead: CSDT completeness and submission coordination.
- Quality lead: ISO 13485 readiness and audits.
- Clinical lead: trial evidence and CER approval.
- Engineering lead: IEC 62304 and V&V evidence.

## Next Steps
- Confirm SaMD Class 3 scope with Thai FDA.
- Finalize trial protocol and IRB submission.
- Begin ISO 13485 QMS preparation.
