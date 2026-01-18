import os
import random

from locust import HttpUser, task, between

class NamoUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a User starts running."""
        token = os.getenv("NAMO_NEXUS_TOKEN", "")
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @task(3)
    def triage_normal(self):
        """Simulate normal usage"""
        self.client.post("/triage", json={
            "user_id": f"user_{random.randint(1, 1000)}",
            "message": "I feel a bit stressed today but I am managing."
        }, headers=self.headers)

    @task(1)
    def triage_crisis(self):
        """Simulate crisis usage (less frequent)"""
        self.client.post("/triage", json={
            "user_id": f"user_{random.randint(1, 1000)}",
            "message": "I don't want to live anymore."
        }, headers=self.headers)

    @task(5)
    def health_check(self):
        self.client.get("/health")
