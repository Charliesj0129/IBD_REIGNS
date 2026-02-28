import time
import uuid
import json
from locust import HttpUser, task, between, events
import websocket

class StreamlitUser(HttpUser):
    # Simulate user reading/thinking time between actions (1 to 5 seconds)
    wait_time = between(1, 4)

    def on_start(self):
        """Called when a Locust user starts before any task is scheduled."""
        self.client.get("/_stcore/health", name="/_stcore/health")
        self.client.get("/", name="Load Main Page")
        
        # Streamlit relies heavily on WebSockets for its persistent state. 
        # Here we simulate keeping a WebSocket open per user.
        ws_url = self.host.replace("http", "ws") + "/_stcore/stream"
        self.ws = websocket.WebSocket()
        start_time = time.time()
        try:
            self.ws.connect(ws_url)
            events.request.fire(
                request_type="WS",
                name="Connect",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=None,
            )
        except Exception as e:
            events.request.fire(
                request_type="WS",
                name="Connect",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=e,
            )

    @task
    def ws_ping(self):
        """Simulate interacting via WebSocket without triggering full Streamlit reruns."""
        start_time = time.time()
        try:
            if hasattr(self, 'ws') and self.ws.connected:
                # We just send a dummy structure to keep the socket active and simulate load
                self.ws.send('{"type": "ping"}')
                events.request.fire(
                    request_type="WS",
                    name="Ping",
                    response_time=int((time.time() - start_time) * 1000),
                    response_length=0,
                    exception=None,
                )
        except Exception as e:
            events.request.fire(
                request_type="WS",
                name="Ping",
                response_time=int((time.time() - start_time) * 1000),
                response_length=0,
                exception=e,
            )

    def on_stop(self):
        if hasattr(self, 'ws') and self.ws.connected:
            self.ws.close()
