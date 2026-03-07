import streamlit.components.v1.components as components
import sys

# load our code
sys.path.append("/home/charlie/IBD_REIGNS")
from ibd_reigns.ui.swipe import _component_func
import urllib.request, time, subprocess

# start a background thread to check registry? No, we need a streamlit app.
app_code = """
import streamlit as st
from ibd_reigns.ui.swipe import swipe_card_component
import streamlit.components.v1.components as components

st.write("Components:")
for comp in components.ComponentRegistry.instance().get_components():
    st.write(comp.name, comp.path, comp.url)
swipe_card_component("c1", "char", "text", "1", "2", {}, {}, {}, "<svg></svg>")
"""
with open("test_registry.py", "w") as f: f.write(app_code)

subprocess.check_call(["uv", "run", "streamlit", "run", "test_registry.py", "--server.port=8515", "--server.headless=true"], timeout=7)
