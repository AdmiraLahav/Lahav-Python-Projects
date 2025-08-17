import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import imgstego


class StegoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IMG Stego (LSB + optional XOR)")
        self.geometry("820x640")

        # Global state
        self.password = tk.StringVar()

        # Hide state
        self.hide_cover = tk.StringVar()
        self.hide_payload_mode = tk.StringVar(value="text")  # text | file
        self.hide_text = tk.StringVar()
        self.hide_file = tk.StringVar()

        # Reveal state
        self.reveal_stego = tk.StringVar()
        self.reveal_dest = tk.StringVar(value="gui")  # gui | file
        self.reveal_output_file = tk.StringVar()

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Tabs
        self.tab_hide = ttk.Frame(nb)
        self.tab_reveal = ttk.Frame(nb)
        nb.add(self.tab_hide, text="Hide (Text/File)")
        nb.add(self.tab_reveal, text="Reveal (Decoder)")

        self._build_hide_tab(self.tab_hide)
        self._build_reveal_tab(self.tab_reveal)

    def _build_hide_tab(self, root):
        # Cover image
        ioframe = ttk.LabelFrame(root, text="Cover image")
        ioframe.pack(fill="x", padx=10, pady=8)
        self._path_row(ioframe, "Cover:", self.hide_cover, open_image=True)

        # Payload mode
        mode_frame = ttk.LabelFrame(root, text="Payload")
        mode_frame.pack(fill="x", padx=10, pady=8)
        ttk.Radiobutton(mode_frame, text="Text", value="text", variable=self.hide_payload_mode,
                        command=self._sync_hide_controls).pack(side="left", padx=6)
        ttk.Radiobutton(mode_frame, text="File", value="file", variable=self.hide_payload_mode,
                        command=self._sync_hide_controls).pack(side="left", padx=6)

        # Text entry
        text_line = ttk.Frame(root)
        text_line.pack(fill="x", padx=18, pady=6)
        ttk.Label(text_line, text="Text:").pack(side="left")
        self.hide_text_entry = ttk.Entry(text_line, textvariable=self.hide_text)
        self.hide_text_entry.pack(side="left", fill="x", expand=True)

        # File selection
        file_line = ttk.Frame(root)
        file_line.pack(fill="x", padx=18, pady=6)
        ttk.Label(file_line, text="File:").pack(side="left")
        self.hide_file_entry = ttk.Entry(file_line, textvariable=self.hide_file)
        self.hide_file_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(file_line, text="Browse…", command=lambda: self._browse_file(self.hide_file)).pack(side="left", padx=6)

        # Password (shared)
        pass_frame = ttk.Frame(root)
        pass_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(pass_frame, text="Password (optional XOR):").pack(side="left")
        ttk.Entry(pass_frame, textvariable=self.password, show="*").pack(side="left", fill="x", expand=True)

        # Actions
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10, pady=10)
        ttk.Button(btns, text="Hide", command=self.run_hide).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear_hide).pack(side="left", padx=6)

        self._sync_hide_controls()

    def _build_reveal_tab(self, root):
        # Stego image
        ioframe = ttk.LabelFrame(root, text="Stego image")
        ioframe.pack(fill="x", padx=10, pady=8)
        self._path_row(ioframe, "Stego:", self.reveal_stego, open_image=True)

        # Destination
        dest_frame = ttk.LabelFrame(root, text="Destination")
        dest_frame.pack(fill="x", padx=10, pady=8)
        ttk.Radiobutton(dest_frame, text="Show in GUI", value="gui", variable=self.reveal_dest,
                        command=self._sync_reveal_dest).pack(side="left", padx=6)
        ttk.Radiobutton(dest_frame, text="Save to file", value="file", variable=self.reveal_dest,
                        command=self._sync_reveal_dest).pack(side="left", padx=6)

        # Output file (enabled only when dest=file)
        out_frame = ttk.Frame(root)
        out_frame.pack(fill="x", padx=18, pady=6)
        ttk.Label(out_frame, text="Output file:").pack(side="left")
        self.reveal_out_entry = ttk.Entry(out_frame, textvariable=self.reveal_output_file)
        self.reveal_out_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(out_frame, text="Browse…", command=self._browse_save_output).pack(side="left", padx=6)

        # Password (shared)
        pass_frame = ttk.Frame(root)
        pass_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(pass_frame, text="Password (optional XOR):").pack(side="left")
        ttk.Entry(pass_frame, textvariable=self.password, show="*").pack(side="left", fill="x", expand=True)

        # Preview (Reveal only)
        viewer_frame = ttk.LabelFrame(root, text="Preview")
        viewer_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.preview = scrolledtext.ScrolledText(viewer_frame, height=14, wrap="word", state="disabled")
        self.preview.pack(fill="both", expand=True, padx=8, pady=6)

        # Actions
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10, pady=10)
        ttk.Button(btns, text="Reveal", command=self.run_reveal).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear_reveal).pack(side="left", padx=6)

        self._sync_reveal_dest()

    # ------------- shared helpers -------------
    def _path_row(self, parent, label, var, open_image=False):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=8, pady=6)
        ttk.Label(row, text=label).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        def browse():
            if open_image:
                fp = filedialog.askopenfilename(title="Select image",
                                                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.webp"), ("All files", "*.*")])
            else:
                fp = filedialog.askopenfilename()
            if fp:
                var.set(fp)
        ttk.Button(row, text="Browse…", command=browse).pack(side="left", padx=6)
        return row

    def _browse_file(self, var):
        fp = filedialog.askopenfilename()
        if fp:
            var.set(fp)

    def _browse_save_output(self):
        fp = filedialog.asksaveasfilename(filetypes=[("Text", "*.txt"), ("Binary", "*.bin"), ("All files", "*.*")])
        if fp:
            self.reveal_output_file.set(fp)

    def _set_preview(self, content: str):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        if content:
            self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")

    # ------------- hide logic -------------
    def _sync_hide_controls(self):
        mode = self.hide_payload_mode.get()
        self.hide_text_entry.configure(state=("normal" if mode == "text" else "disabled"))
        state_file = ("normal" if mode == "file" else "disabled")
        for w in self.hide_file_entry.master.winfo_children():
            if isinstance(w, (ttk.Entry, ttk.Button, ttk.Label)):
                w.configure(state=state_file)

    def _auto_hide_output(self, cover: str) -> str:
        base = os.path.splitext(os.path.basename(cover))[0] + "_stego.png"
        return os.path.join(os.path.dirname(cover), base)

    def clear_hide(self):
        self.hide_cover.set("")
        self.hide_payload_mode.set("text")
        self.hide_text.set("")
        self.hide_file.set("")
        self.password.set("")
        self._sync_hide_controls()

    def run_hide(self):
        cover = self.hide_cover.get()
        if not cover:
            messagebox.showwarning("Missing cover", "Choose a cover image.")
            return
        payload_mode = self.hide_payload_mode.get()
        pwd = self.password.get() or ""
        outp = self._auto_hide_output(cover)
        try:
            if payload_mode == "text":
                text = self.hide_text.get()
                if not text:
                    messagebox.showwarning("Missing text", "Enter text to hide.")
                    return
                imgstego.hide(cover, outp, text.encode("utf-8"), pwd)
            else:
                infile = self.hide_file.get()
                if not infile:
                    messagebox.showwarning("Missing file", "Choose a file to hide.")
                    return
                with open(infile, "rb") as f:
                    data = f.read()
                imgstego.hide(cover, outp, data, pwd)
            messagebox.showinfo("Done", f"Saved stego image:\n{outp}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------- reveal logic -------------
    def _sync_reveal_dest(self):
        state = ("normal" if self.reveal_dest.get() == "file" else "disabled")
        for w in (self.reveal_out_entry, self.reveal_out_entry.master.winfo_children()[-1]):
            w.configure(state=state)

    def clear_reveal(self):
        self.reveal_stego.set("")
        self.reveal_dest.set("gui")
        self.reveal_output_file.set("")
        self.password.set("")
        self._set_preview("")
        self._sync_reveal_dest()

    def run_reveal(self):
        stego = self.reveal_stego.get()
        if not stego:
            messagebox.showwarning("Missing stego image", "Choose the stego image to decode.")
            return
        pwd = self.password.get() or ""
        try:
            payload = imgstego.reveal(stego, pwd)
            if self.reveal_dest.get() == "gui":
                try:
                    self._set_preview(payload.decode("utf-8"))
                except Exception:
                    self._set_preview(f"[binary payload] {len(payload)} bytes (choose 'Save to file' to write to disk)")
            else:
                outp = self.reveal_output_file.get().strip()
                if not outp:
                    messagebox.showwarning("Missing output file", "Pick a file path to save the extracted payload.")
                    return
                parent = os.path.dirname(outp)
                if parent and not os.path.isdir(parent):
                    messagebox.showerror("Save failed", "Parent folder does not exist.")
                    return
                with open(outp, "wb") as f:
                    f.write(payload)
                messagebox.showinfo("Saved", f"Extracted payload saved to:\n{outp}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = StegoGUI()
    app.mainloop()
