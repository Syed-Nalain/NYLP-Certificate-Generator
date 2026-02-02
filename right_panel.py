import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox

class RightPanel(tk.Frame):
    def __init__(self, master, font_manager, on_update, theme=None):
        super().__init__(master, width=300, bg=theme.get("panel_bg") if theme else None)
        self.font_manager = font_manager
        self.on_update = on_update
        self.selected_box = None
        self.theme = theme or {}
        header_bg = self.theme.get("accent", "#228B22")
        header_fg = self.theme.get("button_fg", "#ffffff")

        tk.Label(self, text="Box Properties", font=("Arial", 12, "bold"), bg=header_bg, fg=header_fg).pack(fill="x", pady=6)
        tk.Label(self, text="Field:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        self.field_var = tk.StringVar()
        self.field_menu = tk.OptionMenu(self, self.field_var, "")
        self.field_menu.config(bg="white")
        self.field_menu.pack(fill="x", padx=6)

        tk.Label(self, text="Font:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6, pady=(6,0))
        self.font_var = tk.StringVar()
        self.font_menu = tk.OptionMenu(self, self.font_var, *self.font_manager.font_names)
        self.font_menu.config(bg="white")
        self.font_menu.pack(fill="x", padx=6)

        tk.Label(self, text="Size:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6, pady=(6,0))
        self.size_var = tk.IntVar(value=24)
        tk.Spinbox(self, from_=6, to=200, textvariable=self.size_var).pack(fill="x", padx=6)

        tk.Button(self, text="Pick Color", command=self._pick_color, bg=self.theme.get("accent"), fg=self.theme.get("button_fg"), activebackground=self.theme.get("accent_dark")).pack(padx=6, pady=6, fill="x")
        tk.Label(self, text="Alignment:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        self.align_var = tk.StringVar(value="center")
        tk.OptionMenu(self, self.align_var, "left","center","right").pack(fill="x", padx=6)

        tk.Label(self, text="Vertical Align:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        self.valign_var = tk.StringVar(value="middle")
        tk.OptionMenu(self, self.valign_var, "top","middle","bottom").pack(fill="x", padx=6)

        tk.Button(self, text="Apply to Selected", command=self.apply, bg=self.theme.get("accent"), fg=self.theme.get("button_fg"), activebackground=self.theme.get("accent_dark")).pack(padx=6, pady=10, fill="x")

    def set_selected_box(self, box, columns):
        self.selected_box = box
        # update field menu
        menu = self.field_menu["menu"]
        menu.delete(0, "end")
        for c in columns:
            menu.add_command(label=c, command=lambda v=c: self.field_var.set(v))
        # populate values from box props
        props = box['props']
        self.field_var.set(props.get("field",""))
        self.font_var.set(props.get("font", self.font_manager.font_names[0] if self.font_manager.font_names else "Helvetica"))
        self.size_var.set(props.get("size", 24))
        self.align_var.set(props.get("align","center"))
        self.valign_var.set(props.get("valign","middle"))
        self.color = props.get("color", self.theme.get("accent","#228B22"))

    def _pick_color(self):
        c = colorchooser.askcolor()
        if c and c[1]:
            self.color = c[1]
            messagebox.showinfo("Color", f"Selected {self.color}")

    def apply(self):
        if not self.selected_box:
            messagebox.showwarning("No selection", "Select a box first.")
            return
        props = {"field": self.field_var.get(), "font": self.font_var.get(), "size": int(self.size_var.get()), "align": self.align_var.get(), "valign": self.valign_var.get(), "color": getattr(self, "color", self.theme.get("accent","#228B22"))}
        self.on_update(self.selected_box, props)

    def create_box_from_dialog(self, coords, columns):
        # single small modal to gather initial props
        dlg = tk.Toplevel(self)
        dlg.title("Box Properties")
        dlg.configure(bg=self.theme.get("panel_bg"))
        tk.Label(dlg, text="Field:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        field_var = tk.StringVar()
        if columns:
            field_menu = tk.OptionMenu(dlg, field_var, *columns)
        else:
            field_menu = tk.Entry(dlg, textvariable=field_var)
        field_menu.pack(fill="x", padx=6)
        tk.Label(dlg, text="Font:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6, pady=(6,0))
        font_var = tk.StringVar(value=self.font_manager.font_names[0] if self.font_manager.font_names else "Helvetica")
        tk.OptionMenu(dlg, font_var, *self.font_manager.font_names).pack(fill="x", padx=6)
        tk.Label(dlg, text="Size:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        size_var = tk.IntVar(value=24)
        tk.Spinbox(dlg, from_=6, to=200, textvariable=size_var).pack(fill="x", padx=6)
        color_var = tk.StringVar(value=self.theme.get("accent","#228B22"))
        def pick():
            c = colorchooser.askcolor()
            if c and c[1]:
                color_var.set(c[1])
        tk.Button(dlg, text="Pick Color", command=pick, bg=self.theme.get("accent"), fg=self.theme.get("button_fg"), activebackground=self.theme.get("accent_dark")).pack(padx=6, pady=6)
        tk.Label(dlg, text="Alignment:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        align_var = tk.StringVar(value="center")
        tk.OptionMenu(dlg, align_var, "left","center","right").pack(fill="x", padx=6)
        tk.Label(dlg, text="Vertical Align:", bg=self.theme.get("panel_bg"), fg=self.theme.get("text")).pack(anchor="w", padx=6)
        valign_var = tk.StringVar(value="middle")
        tk.OptionMenu(dlg, valign_var, "top","middle","bottom").pack(fill="x", padx=6)
        result = {}
        def ok():
            result.update({"field": field_var.get(), "font": font_var.get(), "size": int(size_var.get()), "color": color_var.get(), "align": align_var.get(), "valign": valign_var.get()})
            dlg.destroy()
        tk.Button(dlg, text="OK", command=ok, bg=self.theme.get("accent"), fg=self.theme.get("button_fg"), activebackground=self.theme.get("accent_dark")).pack(pady=8)
        dlg.transient(self)
        dlg.grab_set()
        self.wait_window(dlg)
        return result if result.get("field") else None