import os

from locust import HttpUser, task, between

AUTH_TOKEN = os.getenv("NAMO_NEXUS_TOKEN", "namo-nexus-enterprise-2026")
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


class NamoLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def interact(self):
        self.client.post(
            "/triage",
            json={
                "message": "I feel anxious today",
                "user_id": "load_test_001",
            },
            headers=AUTH_HEADERS,
        )
