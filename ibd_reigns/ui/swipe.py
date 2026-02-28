import os
import streamlit as st
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "swipe_component")

if _RELEASE:
    _component_func = components.declare_component("swipe_card_component", path=build_dir)
else:
    _component_func = components.declare_component(
        "swipe_card_component",
        url="http://localhost:3001",
    )

def swipe_card_component(
    card_id: str,
    character_line: str,
    text: str,
    left_label: str,
    right_label: str,
    left_effect: dict,
    right_effect: dict,
    current_stats: dict,
    silhouette_svg: str,
    season: str = "spring",
    week: int | None = None,
    key=None,
):
    """Create a new instance of "swipe_card_component"."""
    if key is None:
        key = f"swipe_card_{card_id}_{week}"

    component_value = _component_func(
        card_id=card_id,
        character_line=character_line,
        text=text,
        left_label=left_label,
        right_label=right_label,
        left_effect=left_effect,
        right_effect=right_effect,
        current_stats=current_stats,
        silhouette_svg=silhouette_svg,
        season=season,
        week=week,
        key=key,
        default=None,
    )

    return component_value
