from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

from ibd_reigns.cta import CtaContent


@dataclass
class RenderCall:
    name: str
    payload: dict


class Renderer:
    def __init__(self) -> None:
        self.calls: List[RenderCall] = []

    def progress(self, stat: str, value: int) -> None:
        self.calls.append(RenderCall("progress", {"stat": stat, "value": value}))

    def card_text(self, text: str, emoji: Optional[str] = None) -> None:
        self.calls.append(RenderCall("card_text", {"text": text, "emoji": emoji}))

    def buttons(self, left_label: str, right_label: str, locks: Dict[str, Optional[str]]) -> None:
        self.calls.append(RenderCall("buttons", {"left": left_label, "right": right_label, "locks": locks}))

    def feedback(self, message: str, blocking: bool) -> None:
        self.calls.append(RenderCall("feedback", {"message": message, "blocking": blocking}))

    def disclaimer(self, text: str) -> None:
        self.calls.append(RenderCall("disclaimer", {"text": text}))

    def cta(self, content: CtaContent) -> None:
        self.calls.append(RenderCall("cta", {"title": content.title, "actions": content.actions, "footer": content.footer}))


class StreamlitRenderer(Renderer):
    def progress(self, stat: str, value: int) -> None:  # pragma: no cover
        if st:
            st.caption(stat)
            st.progress(value / 100)

    def card_text(self, text: str, emoji: Optional[str] = None) -> None:  # pragma: no cover
        if st:
            if emoji:
                st.markdown(f"### {emoji}")
            st.markdown(f"#### {text}")

    def buttons(self, left_label: str, right_label: str, locks: Dict[str, Optional[str]]) -> None:  # pragma: no cover
        if not st:
            return
        col1, col2 = st.columns(2)
        with col1:
            st.button(left_label, disabled=locks.get("left") is not None, use_container_width=True)
            if locks.get("left"):
                st.caption(locks["left"])
        with col2:
            st.button(right_label, disabled=locks.get("right") is not None, use_container_width=True)
            if locks.get("right"):
                st.caption(locks["right"])

    def feedback(self, message: str, blocking: bool) -> None:  # pragma: no cover
        if not st:
            return
        if blocking:
            st.info(message)
        else:
            st.toast(message)

    def disclaimer(self, text: str) -> None:  # pragma: no cover
        if st:
            st.title("免責聲明")
            st.warning(text)

    def cta(self, content: CtaContent) -> None:  # pragma: no cover
        if not st:
            return
        st.markdown(f"### {content.title}")
        col1, col2 = st.columns(2)
        for idx, action in enumerate(content.actions):
            col = col1 if idx == 0 else col2
            with col:
                if action.action_type == "link":
                    st.link_button(action.label, action.url or "#", use_container_width=True)
                else:
                    st.button(action.label, use_container_width=True)
        st.caption(content.footer)
