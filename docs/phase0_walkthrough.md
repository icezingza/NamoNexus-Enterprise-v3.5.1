# Phase 0 Walkthrough (Legacy Core Cleanup)

## Goal
Remove legacy core modules and confirm no remaining legacy references.

## Changes Completed
- Removed legacy core module files from the production tree.
- Research variants (if retained) now live under `research/`.

## Verification
- Search for legacy references:
  - Pattern: `DharmaReasoningEngine|EthicalCalibrationKernel|DhammicNexusHeart`
  - Scope: `src/**/*.py` (production), `research/**/*.py` (optional)
  - Expected: no matches in `src/`

## Tests to Run (Research)
- `pytest research/tests/test_integrity_validator.py -v`
- `pytest research/tests/test_critical_incident_protocol.py -v`

## Status
Phase 0 cleanup is complete for production (`src/`). Research modules remain under `research/`.
