
import streamlit as st
from ibd_reigns.ui.swipe import swipe_card_component
st.write("Hello")
swipe_card_component("c1", "char", "text", "left", "right", {}, {}, {}, "<svg></svg>")
