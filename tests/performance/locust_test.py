import os
import random

from locust import HttpUser, task, between

AUTH_TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "namo-nexus-enterprise-2026")
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


class NamoNexusUser(HttpUser):
    """Simulate real user behavior."""

    wait_time = between(1, 5)

    @task(1)
    def health_check(self):
        """Simulate health check."""
        self.client.get("/healthz")

    @task(2)
    def reflect_positive(self):
        """Simulate positive reflection."""
        self.client.post(
            "/triage",
            json={
                "message": "I feel happy and grateful",
                "user_id": f"user_{random.randint(1, 1000)}",
            },
            headers=AUTH_HEADERS,
        )

    @task(2)
    def reflect_negative(self):
        """Simulate negative reflection."""
        self.client.post(
            "/triage",
            json={
                "message": "I am stressed about work",
                "user_id": f"user_{random.randint(1, 1000)}",
            },
            headers=AUTH_HEADERS,
        )

    @task(1)
    def interact(self):
        """Simulate interaction."""
        self.client.post(
            "/triage",
            json={
                "message": "Help me manage my anxiety",
                "user_id": f"user_{random.randint(1, 1000)}",
            },
            headers=AUTH_HEADERS,
        )


class AdminUser(HttpUser):
    """Simulate admin checking status."""

    wait_time = between(10, 20)

    @task
    def check_status(self):
        """Check API status."""
        self.client.get("/health")
