# GitLab CI/CD

This repository includes a `.gitlab-ci.yml` that mirrors the GitHub workflow.

## What it does
- Validation: lint + security scans
- Tests: pytest with coverage output
- Build: Docker image build/push
- Deploy: manual Kubernetes apply
- Monitoring: manual alerts apply

## Required variables (build/deploy)
GitLab Registry (default):
- `CI_REGISTRY`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD`, `CI_REGISTRY_IMAGE`

Custom registry (optional):
- `DOCKER_REGISTRY`
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DOCKER_IMAGE`

Kubernetes:
- `KUBE_CONFIG_DATA` (base64 kubeconfig)
- `KUBE_DEPLOYMENT_NAME` (optional)
- `KUBE_NAMESPACE` (optional)

## Notes
- Deploy/monitoring jobs are manual and only run on `main`.
- `k8s/deployment.yaml` and `monitoring/alerts.yaml` must exist for those jobs to appear.
