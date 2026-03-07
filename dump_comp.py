import streamlit.components.v1.component_registry as component_registry
import sys
import threading

sys.path.append("/home/charlie/IBD_REIGNS")
from ibd_reigns.ui.swipe import _component_func
import urllib.request
import time
import subprocess

app_code = """
import streamlit as st
import streamlit.components.v1.components as components
from ibd_reigns.ui.swipe import swipe_card_component

st.write("Components:")
for comp in components.ComponentRegistry.instance().get_components():
    st.write(comp.name, comp.path, comp.url)
swipe_card_component("c1", "char", "text", "1", "2", {}, {}, {}, "<svg></svg>")
"""
with open("test_urls.py", "w") as f:
    f.write(app_code)

def run_app():
    # Use Popen instead of check_call so it doesn't wait
    import subprocess
    global p
    p = subprocess.Popen(["uv", "run", "streamlit", "run", "test_urls.py", "--server.port=8517", "--server.headless=true"])

run_app()
time.sleep(5)
try:
    # Query something if needed. Since we just want the console component registry output, 
    # wait... st.write doesn't write to console.
    # Let's print properties directly.
    print("Registered Component:")
    for comp in component_registry.ComponentRegistry.instance().get_components():
        print(f"Name: {comp.name}")
        print(f"Path: {comp.path}")
        print(f"URL: {comp.url}")
except Exception as e:
    print("Error:", e)
finally:
    p.terminate()
