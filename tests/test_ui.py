from ibd_reigns.ui import Renderer
from ibd_reigns.cta import build_cta


def test_renderer_records_progress():
    renderer = Renderer()
    renderer.progress("HEALTH", 50)
    assert renderer.calls[0].name == "progress"


def test_renderer_records_buttons():
    renderer = Renderer()
    renderer.buttons("Left", "Right", {"left": None, "right": "Locked"})
    assert renderer.calls[0].payload["locks"]["right"] == "Locked"


def test_renderer_cta():
    renderer = Renderer()
    renderer.cta(build_cta("good"))
    assert renderer.calls[0].name == "cta"
