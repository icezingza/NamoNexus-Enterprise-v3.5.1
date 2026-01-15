# CI/CD Secrets

This repository uses `.github/workflows/ci.yml`.

## Required for deploy
- `DOCKER_REGISTRY` (example: `ghcr.io`)
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `DOCKER_IMAGE` (example: `ghcr.io/your-org/namonexus-enterprise`)
- `KUBE_CONFIG_DATA` (base64-encoded kubeconfig)
- `KUBE_DEPLOYMENT_NAME` (optional)
- `KUBE_NAMESPACE` (optional, default is `default`)

## Optional integrations
- `SONAR_TOKEN`
- `SONAR_PROJECT_KEY`
- `SONAR_ORGANIZATION`
- `CODECOV_TOKEN`

## Notes
- Update `k8s/deployment.yaml` with the correct image and `NAMO_NEXUS_TOKEN`.
- Monitoring requires `monitoring/alerts.yaml` and `KUBE_CONFIG_DATA`.
