import tkinter as tk
from tkinter import filedialog, messagebox
from designer import Designer
from right_panel import RightPanel
from font_manager import FontManager
from pdf_engine import export_certificates
import pandas as pd
import os

# Theme (forest green based)
THEME = {
    "bg": "#f3fff5",
    "panel_bg": "#eaf7ec",
    "accent": "#228B22",       # forest green
    "accent_dark": "#1f7a1f",
    "text": "#08331a",
    "button_fg": "#ffffff",
    "canvas_bg": "#ffffff",
}

def show_welcome(root, on_start):
    w = tk.Toplevel(root)
    w.title("NYLP Certificate generator - Welcome")
    w.configure(bg=THEME["bg"])
    tk.Label(w, text="NYLP Certificate generator", font=("Arial", 16, "bold"), bg=THEME["bg"], fg=THEME["text"]).pack(padx=20, pady=10)
    tk.Label(w, text="Made by Nalain-e-Muhammad", font=("Arial", 10), bg=THEME["bg"], fg=THEME["text"]).pack(padx=20)
    tk.Label(w, text="Click Start Designing to begin.", bg=THEME["bg"], fg=THEME["text"]).pack(padx=20, pady=8)
    def start():
        w.destroy()
        on_start()
    tk.Button(w, text="Start Designing", command=start, bg=THEME["accent"], fg=THEME["button_fg"], activebackground=THEME["accent_dark"]).pack(pady=15)
    w.transient(root)
    w.grab_set()
    root.wait_window(w)

def main():
    root = tk.Tk()
    root.title("NYLP Certificate generator")
    root.geometry("1200x800")
    root.configure(bg=THEME["bg"])

    fm = FontManager(os.path.join(os.getcwd(), "fonts"))
    fm.scan_fonts()

    toolbar = tk.Frame(root, bg=THEME["panel_bg"])
    toolbar.pack(side="top", fill="x", padx=4, pady=4)
    pdf_path_var = tk.StringVar()
    csv_path_var = tk.StringVar()
    csv_store = {"df": None}

    def select_pdf():
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            pdf_path_var.set(path)
            designer.load_pdf(path)

    def select_csv():
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            csv_path_var.set(path)
            try:
                df = pd.read_csv(path)
                csv_store["df"] = df
                designer.set_csv(df, list(df.columns))
            except Exception as e:
                messagebox.showerror("CSV Error", str(e))

    def do_export():
        if not pdf_path_var.get() or not csv_path_var.get() or not designer.mappings:
            messagebox.showwarning("Missing", "Select PDF, CSV and map at least one field.")
            return
        outdir = filedialog.askdirectory(title="Select Output Directory")
        if not outdir:
            return
        total = len(csv_store["df"]) if csv_store["df"] is not None else "unknown"
        messagebox.showinfo("Exporting", f"Exporting {total} certificates...\nThis may take a while.")
        try:
            generated = export_certificates(pdf_path_var.get(), csv_path_var.get(), designer.mappings, (designer.canvas_width, designer.canvas_height), outdir, fm)
            msg = f"Export completed. {len(generated)} certificates written."
            messagebox.showinfo("Success", msg)
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    btn_style = {"bg": THEME["accent"], "fg": THEME["button_fg"], "activebackground": THEME["accent_dark"]}
    tk.Button(toolbar, text="Select PDF", command=select_pdf, **btn_style).pack(side="left", padx=4)
    tk.Button(toolbar, text="Select CSV", command=select_csv, **btn_style).pack(side="left", padx=4)
    tk.Button(toolbar, text="Export", command=do_export, **btn_style).pack(side="left", padx=4)

    main_frame = tk.Frame(root, bg=THEME["bg"])
    main_frame.pack(fill="both", expand=True)

    designer = Designer(main_frame, font_manager=fm, theme=THEME)
    designer.pack(side="left", fill="both", expand=True)

    right = RightPanel(main_frame, font_manager=fm, on_update=designer.update_box_properties, theme=THEME)
    right.pack(side="right", fill="y")

    def on_selection_changed(box):
        right.set_selected_box(box, designer.excel_columns if hasattr(designer, "excel_columns") else [])
    designer.on_select = on_selection_changed
    designer.on_new_box = right.create_box_from_dialog

    show_welcome(root, lambda: None)
    root.mainloop()

if __name__ == "__main__":
    main()