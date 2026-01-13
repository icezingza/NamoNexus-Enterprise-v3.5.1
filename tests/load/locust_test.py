from locust import HttpUser, task, between


class NamoLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def interact(self):
        self.client.post(
            "/interact",
            json={
                "message": "I feel anxious today",
                "user_id": "load_test_001",
            },
        )
