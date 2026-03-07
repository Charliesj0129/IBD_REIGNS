
import streamlit as st
from ibd_reigns.ui.swipe import swipe_card_component
import streamlit.components.v1.components as components

st.write("Components:")
for comp in components.ComponentRegistry.instance().get_components():
    st.write(comp.name, comp.path, comp.url)
swipe_card_component("c1", "char", "text", "1", "2", {}, {}, {}, "<svg></svg>")
