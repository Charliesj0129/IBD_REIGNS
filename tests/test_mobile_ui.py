from ibd_reigns.ui_styles import MOBILE_CSS


def test_mobile_css_button_height():
    assert "min-height: 50px" in MOBILE_CSS


def test_mobile_css_single_column_hint():
    assert "max-width: 768px" in MOBILE_CSS
