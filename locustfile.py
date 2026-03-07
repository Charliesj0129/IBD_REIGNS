from locust import HttpUser, task, between

class IbdReignsUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def load_main_page(self):
        self.client.get("/")

    @task(1)
    def load_analytics(self):
        self.client.get("/?analytics=true") # Mock query
