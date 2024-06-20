from pyrevit import forms
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"


class VIKTORWindow(forms.WPFWindow):
    """VIKTOR  window"""

    def __init__(self, xaml_source):
        forms.WPFWindow.__init__(self, xaml_source)
        self.set_icon(str(ASSETS_DIR / "viktor-light.ico"))
        self.set_image_source(self.logo, str(ASSETS_DIR / "viktor-light.png"))
