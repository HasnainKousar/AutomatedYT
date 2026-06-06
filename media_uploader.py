# ============================================================
#  media_uploader.py — Upload videos/images from your computer
#  into the output/images/ folder used by the pipeline.
#  Uses only built-in Python libraries (tkinter + shutil).
# ============================================================

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config import IMAGES_DIR

os.makedirs(IMAGES_DIR, exist_ok=True)

SUPPORTED = (
    ("Video & Image files",
     "*.mp4 *.mov *.avi *.webm *.mkv *.jpg *.jpeg *.png *.webp"),
    ("Video files",  "*.mp4 *.mov *.avi *.webm *.mkv"),
    ("Image files",  "*.jpg *.jpeg *.png *.webp"),
    ("All files",    "*.*"),
)


class UploaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📂 Media Uploader — YouTube Pipeline")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self._selected_files: list[str] = []
        self._build_ui()

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        PAD = dict(padx=16, pady=8)

        # Title
        tk.Label(
            self, text="📂 Media Uploader",
            font=("Helvetica", 18, "bold"),
            fg="#cdd6f4", bg="#1e1e2e",
        ).pack(**PAD, pady=(16, 4))

        # Destination label
        dest = os.path.abspath(IMAGES_DIR)
        tk.Label(
            self, text=f"Destination: {dest}",
            font=("Helvetica", 9), fg="#a6adc8", bg="#1e1e2e", wraplength=420,
        ).pack()

        # Click-to-browse zone
        drop_frame = tk.Frame(
            self, bg="#313244", relief="flat",
            width=440, height=120, cursor="hand2",
        )
        drop_frame.pack(padx=16, pady=12)
        drop_frame.pack_propagate(False)

        tk.Label(
            drop_frame,
            text="🖱️  Click here to browse files",
            font=("Helvetica", 13), fg="#89b4fa", bg="#313244",
        ).place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(
            drop_frame,
            text="Supports: MP4  MOV  AVI  WEBM  JPG  PNG  WEBP",
            font=("Helvetica", 9), fg="#585b70", bg="#313244",
        ).place(relx=0.5, rely=0.72, anchor="center")

        drop_frame.bind("<Button-1>", lambda _: self._browse())

        # File list
        list_frame = tk.Frame(self, bg="#1e1e2e")
        list_frame.pack(padx=16, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.file_list = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            bg="#181825", fg="#cdd6f4", selectbackground="#45475a",
            font=("Courier", 9), height=8, relief="flat",
            activestyle="none",
        )
        scrollbar.config(command=self.file_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_list.pack(fill="both", expand=True)

        # Progress bar
        self.progress = ttk.Progressbar(self, mode="determinate", length=440)
        self.progress.pack(padx=16, pady=(8, 0))

        # Status label
        self.status_var = tk.StringVar(value="No files selected.")
        tk.Label(
            self, textvariable=self.status_var,
            font=("Helvetica", 9), fg="#a6e3a1", bg="#1e1e2e",
        ).pack()

        # Buttons
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=12)

        tk.Button(
            btn_frame, text="📁  Browse Files",
            command=self._browse,
            bg="#89b4fa", fg="#1e1e2e", font=("Helvetica", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            btn_frame, text="✅  Copy to Pipeline",
            command=self._copy_files,
            bg="#a6e3a1", fg="#1e1e2e", font=("Helvetica", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).grid(row=0, column=1, padx=6)

        tk.Button(
            btn_frame, text="🗑️  Clear List",
            command=self._clear,
            bg="#f38ba8", fg="#1e1e2e", font=("Helvetica", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).grid(row=0, column=2, padx=6)

    # ── Actions ──────────────────────────────────────────
    def _browse(self):
        paths = filedialog.askopenfilenames(
            title="Select your Meta AI videos or images",
            filetypes=SUPPORTED,
        )
        if not paths:
            return

        for p in paths:
            if p not in self._selected_files:
                self._selected_files.append(p)
                self.file_list.insert("end", f"  {os.path.basename(p)}")

        self.status_var.set(f"{len(self._selected_files)} file(s) selected — ready to copy.")
        self.progress["value"] = 0

    def _copy_files(self):
        if not self._selected_files:
            messagebox.showwarning("No files", "Please browse and select files first.")
            return

        total   = len(self._selected_files)
        copied  = 0
        skipped = 0

        self.progress["maximum"] = total

        for i, src in enumerate(self._selected_files, 1):
            filename = os.path.basename(src)
            dest     = os.path.join(IMAGES_DIR, filename)

            # Auto-rename if file already exists
            if os.path.exists(dest):
                name, ext = os.path.splitext(filename)
                dest = os.path.join(IMAGES_DIR, f"{name}_{i}{ext}")
                skipped += 1

            shutil.copy2(src, dest)
            copied += 1
            self.progress["value"] = i
            self.status_var.set(f"Copying {i}/{total}: {filename}")
            self.update_idletasks()

        self.status_var.set(
            f"✅ Done! {copied} file(s) copied to output/images/"
            + (f"  ({skipped} renamed to avoid overwrite)" if skipped else "")
        )
        messagebox.showinfo(
            "Upload Complete",
            f"{copied} file(s) successfully copied to:\n{os.path.abspath(IMAGES_DIR)}"
        )

    def _clear(self):
        self._selected_files.clear()
        self.file_list.delete(0, "end")
        self.progress["value"] = 0
        self.status_var.set("List cleared.")


# ── Entry point ──────────────────────────────────────────
if __name__ == "__main__":
    app = UploaderApp()
    app.mainloop()
