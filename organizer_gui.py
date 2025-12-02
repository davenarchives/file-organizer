"""
Simple Tkinter GUI wrapper for organizer.py.

Lets you pick source and target folders, toggle dry-run, and run the organizer
with a styled interface.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from organizer import DEFAULT_SOURCE, DEFAULT_TARGET_ROOT, organize


# Simple, high-contrast palette and clear typography.
BG = "#0f172a"
CARD = "#111827"
ACCENT = "#38bdf8"
ACCENT_DARK = "#0ea5e9"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI Semibold", 11)


def browse_path(initial: Path) -> Path | None:
    """Open a folder picker and return the selected path or None."""
    picked = filedialog.askdirectory(initialdir=str(initial))
    return Path(picked) if picked else None


def append_log(widget: tk.Text, message: str) -> None:
    """Append a line to the log text widget."""
    widget.configure(state="normal")
    widget.insert("end", message + "\n")
    widget.see("end")
    widget.configure(state="disabled")


def run_organizer(
    source: Path, target: Path, dry_run: bool, log_widget: tk.Text
) -> None:
    """Execute the organizer and stream output to the log area."""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            organize(source, target, dry_run=dry_run, create_source=True)
        output = buf.getvalue().strip()
        append_log(log_widget, output or "Done. No files needed moving.")
        messagebox.showinfo("Organizer", "Finished.")
    except Exception as exc:  # pylint: disable=broad-except
        append_log(log_widget, f"Error: {exc}")
        messagebox.showerror("Organizer", str(exc))
    finally:
        buf.close()


def build_ui() -> None:
    root = tk.Tk()
    root.title("File Organizer")
    root.configure(bg=BG)
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TEXT, fieldbackground=CARD)
    style.configure(
        "Card.TFrame",
        background=CARD,
        relief="flat",
        padding=16,
    )
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#0b1224",
        padding=(12, 6),
        font=FONT_BOLD,
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_DARK)],
        foreground=[("active", "#0b1224")],
    )
    style.configure(
        "Muted.TLabel",
        background=CARD,
        foreground=MUTED,
        font=FONT,
    )

    container = ttk.Frame(root, style="Card.TFrame")
    container.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")

    title = ttk.Label(
        container,
        text="Organize your files in three clicks",
        font=("Segoe UI Semibold", 14),
        foreground=TEXT,
        background=CARD,
    )
    subtitle = ttk.Label(
        container,
        text="Choose where your files are, choose where to place the folders, then run.",
        style="Muted.TLabel",
    )
    title.grid(row=0, column=0, columnspan=3, sticky="w")
    subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 14))

    source_var = tk.StringVar(value=str(DEFAULT_SOURCE))
    target_var = tk.StringVar(value=str(DEFAULT_TARGET_ROOT))

    def set_path(var: tk.StringVar, picked: Path | None) -> None:
        if picked:
            var.set(str(picked))

    # Source row
    ttk.Label(
        container, text="1) Where are your files?", font=FONT_BOLD, background=CARD, foreground=TEXT
    ).grid(row=2, column=0, sticky="w", pady=(0, 4))
    ttk.Label(
        container,
        text="Example: Downloads or Desktop",
        style="Muted.TLabel",
    ).grid(row=3, column=0, sticky="w", pady=(0, 6))
    source_entry = ttk.Entry(container, textvariable=source_var, width=52)
    source_entry.grid(row=4, column=0, columnspan=2, sticky="we", padx=(0, 8))
    ttk.Button(
        container,
        text="Choose folder",
        command=lambda: set_path(source_var, browse_path(Path(source_var.get()))),
        style="Accent.TButton",
    ).grid(row=4, column=2, sticky="e")

    # Target row
    ttk.Label(
        container, text="2) Where should organized folders go?", font=FONT_BOLD, background=CARD, foreground=TEXT
    ).grid(row=5, column=0, sticky="w", pady=(14, 4))
    ttk.Label(
        container,
        text="Example: Same as source, or any other folder",
        style="Muted.TLabel",
    ).grid(row=6, column=0, sticky="w", pady=(0, 6))
    target_entry = ttk.Entry(container, textvariable=target_var, width=52)
    target_entry.grid(row=7, column=0, columnspan=2, sticky="we", padx=(0, 8))
    ttk.Button(
        container,
        text="Choose folder",
        command=lambda: set_path(target_var, browse_path(Path(target_var.get()))),
        style="Accent.TButton",
    ).grid(row=7, column=2, sticky="e")

    # Actions row
    # Log area
    ttk.Label(
        container,
        text="What happened",
        font=FONT_BOLD,
        background=CARD,
        foreground=TEXT,
    ).grid(row=9, column=0, sticky="w")
    log = tk.Text(
        container,
        height=10,
        width=62,
        bg=BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=CARD,
        wrap="word",
    )
    log.grid(row=10, column=0, columnspan=3, sticky="we", pady=(6, 4))
    log.configure(state="disabled")

    # Actions row
    buttons_frame = ttk.Frame(container, style="Card.TFrame")
    buttons_frame.grid(row=11, column=0, columnspan=3, pady=(10, 4), sticky="we")
    ttk.Button(
        buttons_frame,
        text="Preview (no changes)",
        style="Accent.TButton",
        command=lambda: run_organizer(
            Path(source_var.get()).expanduser(),
            Path(target_var.get()).expanduser(),
            True,
            log,
        ),
    ).grid(row=0, column=0, padx=(0, 10))
    ttk.Button(
        buttons_frame,
        text="Organize now",
        style="Accent.TButton",
        command=lambda: run_organizer(
            Path(source_var.get()).expanduser(),
            Path(target_var.get()).expanduser(),
            False,
            log,
        ),
    ).grid(row=0, column=1)

    root.mainloop()


if __name__ == "__main__":
    build_ui()
