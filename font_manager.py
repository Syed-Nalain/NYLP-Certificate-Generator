import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class FontManager:
    def __init__(self, fonts_dir="fonts"):
        self.fonts_dir = fonts_dir
        self.font_names = ["Helvetica","Times-Roman","Courier"]
        if not os.path.isdir(self.fonts_dir):
            os.makedirs(self.fonts_dir, exist_ok=True)

    def scan_fonts(self):
        for fn in os.listdir(self.fonts_dir):
            if fn.lower().endswith(".ttf"):
                path = os.path.join(self.fonts_dir, fn)
                name = os.path.splitext(fn)[0]
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    if name not in self.font_names:
                        self.font_names.append(name)
                except Exception:
                    # skip bad fonts
                    pass