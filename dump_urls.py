import streamlit.components.v1.components as components
import sys
sys.path.append("/home/charlie/IBD_REIGNS")
from ibd_reigns.ui.swipe import _component_func
import urllib.request, time, subprocess

# Start streamlit
app_code = """
import streamlit as st
import streamlit.components.v1.components as components
from ibd_reigns.ui.swipe import swipe_card_component
swipe_card_component("c1", "char", "text", "1", "2", {}, {}, {}, "<svg></svg>")
"""
with open("test_app2.py", "w") as f: f.write(app_code)

p = subprocess.Popen(["uv", "run", "streamlit", "run", "test_app2.py", "--server.port=8511", "--server.headless=true"])
time.sleep(4)

# We can query the main page and look for anything resembling /component/
req = urllib.request.urlopen("http://127.0.0.1:8511/")
html = req.read().decode("utf-8")
print("Main HTML size:", len(html))

# Actually, the component URL is passed in the websocket. 
# We can't see it without WS client.
# Let's look at the component registry.
p.terminate()
