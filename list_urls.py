import urllib.request
import streamlit.components.v1.components as components
import sys
import threading
sys.path.append("/home/charlie/IBD_REIGNS")
from ibd_reigns.ui.swipe import _component_func
print("Components:")
for comp in components.ComponentRegistry.instance().get_components():
    print(comp.name, comp.path, comp.url)
