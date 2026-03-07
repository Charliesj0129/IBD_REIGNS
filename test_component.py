import urllib.request
import time
import subprocess

# Let's run a small streamlit app with just the component
app_code = """
import streamlit as st
from ibd_reigns.ui.swipe import swipe_card_component
st.write("Hello")
swipe_card_component("c1", "char", "text", "left", "right", {}, {}, {}, "<svg></svg>")
"""
with open("test_app.py", "w") as f:
    f.write(app_code)

p = subprocess.Popen(["uv", "run", "streamlit", "run", "test_app.py", "--server.port=8505", "--server.headless=true"])
time.sleep(5)
try:
    print("Checking health...")
    health = urllib.request.urlopen("http://127.0.0.1:8505/_stcore/health").read()
    print("Health:", health)
    
    print("Fetching component list...")
    # There is no component list, we can just fetch the page and extract iframe
    req = urllib.request.urlopen("http://127.0.0.1:8505/")
    html = req.read().decode("utf-8")
    print("Main HTML size:", len(html))
except Exception as e:
    print("Error:", e)
finally:
    p.terminate()
