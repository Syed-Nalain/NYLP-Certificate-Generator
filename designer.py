import tkinter as tk
from PIL import Image, ImageTk
import fitz
import os

class Designer(tk.Frame):
    def __init__(self, master, font_manager=None, max_w=900, max_h=700, theme=None):
        super().__init__(master, bg=theme.get("bg") if theme else None)
        self.theme = theme or {}
        self.font_manager = font_manager
        self.max_preview_width = max_w
        self.max_preview_height = max_h
        self.canvas = tk.Canvas(self, bg=self.theme.get("canvas_bg","#ffffff"), highlightthickness=1, highlightbackground=self.theme.get("accent","#228B22"))
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.v_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.page_image = None
        self.canvas_image = None
        self.canvas_width = 600
        self.canvas_height = 800
        self.preview_scale = 1.0

        self.rect_start = None
        self.rect_id = None
        self.boxes = []  # list of mappings: {'rect_id','coords','props'}
        self.selected = None

        # Callbacks to be set by app
        self.on_select = None
        self.on_new_box = None

        self.excel_columns = []

    def load_pdf(self, path):
        doc = fitz.open(path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pdf_w, pdf_h = pix.width, pix.height
        scale = min(self.max_preview_width / pdf_w, self.max_preview_height / pdf_h, 1.0)
        disp_w, disp_h = int(pdf_w * scale), int(pdf_h * scale)
        self.canvas_width, self.canvas_height = disp_w, disp_h
        self.preview_scale = scale
        self.canvas.config(scrollregion=(0,0,self.canvas_width,self.canvas_height))
        img = img.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.page_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas_image = self.canvas.create_image(0,0,anchor="nw",image=self.page_image)

    def set_csv(self, df, columns):
        self.excel_columns = columns

    def _on_press(self, event):
        # select existing box?
        for b in self.boxes:
            x0,y0,x1,y1 = b['coords']
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                self.selected = b
                sel_color = self.theme.get("accent_dark","#1f7a1f")
                self.canvas.itemconfig(b['rect_id'], outline=sel_color, width=2)
                if self.on_select:
                    self.on_select(b)
                return
        # start new rect
        self.selected = None
        self.rect_start = (event.x, event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(event.x,event.y,event.x,event.y, outline=self.theme.get("accent","#228B22"), width=2)

    def _on_drag(self, event):
        if self.rect_start and self.rect_id:
            x0,y0 = self.rect_start
            self.canvas.coords(self.rect_id, x0,y0,event.x,event.y)

    def _on_release(self, event):
        if self.rect_start and self.rect_id:
            x0,y0,x1,y1 = self.canvas.coords(self.rect_id)
            coords = (min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1))
            # ask for initial properties via callback
            if self.on_new_box:
                props = self.on_new_box(coords, self.excel_columns)
            else:
                props = None
            if props:
                self.canvas.itemconfig(self.rect_id, outline=self.theme.get("accent","#228B22"), width=2)
                self.boxes.append({'rect_id': self.rect_id, 'coords': coords, 'props': props})
                self.canvas.create_text((coords[0]+coords[2])//2, (coords[1]+coords[3])//2, text=props.get("field",""), fill=props.get("color",self.theme.get("accent","#228B22")))
            else:
                self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.rect_start = None

    def update_box_properties(self, box, props):
        # update properties dict and redraw label color/text
        box['props'].update(props)
        x0,y0,x1,y1 = box['coords']
        # simple: remove any existing text by drawing over (could be improved)
        self.canvas.create_rectangle(x0,y0,x1,y1, outline=self.theme.get("accent","#228B22"), width=2)
        self.canvas.create_text((x0+x1)//2,(y0+y1)//2, text=box['props'].get("field",""), fill=box['props'].get("color",self.theme.get("accent","#228B22")))

    @property
    def mappings(self):
        out = []
        for b in self.boxes:
            m = {'coords': b['coords'], 'field': b['props'].get('field'), 'font': b['props'].get('font'), 'max_font_size': b['props'].get('size',48), 'alignment': b['props'].get('align','center'), 'valign': b['props'].get('valign','middle'), 'color': b['props'].get('color',self.theme.get("accent","#228B22"))}
            out.append(m)
        return out