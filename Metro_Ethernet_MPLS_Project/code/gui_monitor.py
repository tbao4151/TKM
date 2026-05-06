#!/usr/bin/env python3
"""GUI Tkinter de demo va chay cac phep do that trong Mininet."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
CSV_PATH = RESULTS_DIR / "results.csv"

HIDDEN_WARNING_MARKERS = (
    "warning:",
    "userwarning",
    "deprecationwarning",
    "*** warning",
)

HOSTS = [
    "host1",
    "host2",
    "host3",
    "host4",
    "admin1",
    "admin2",
    "user1",
    "user2",
    "guest1",
    "guest2",
    "svr1",
    "svr2",
    "svr3a",
    "svr3b",
    "svr4",
    "os1",
    "os2",
]

ACTION_LABELS = {
    "ping": "Ping",
    "traceroute": "Traceroute",
    "throughput": "Throughput",
    "delay": "Delay",
    "packet-loss": "Packet Loss",
    "jitter": "Jitter",
}

COLORS = {
    "bg": "#eef3f6",
    "surface": "#ffffff",
    "panel": "#15333f",
    "panel_soft": "#214b5c",
    "text": "#10262f",
    "muted": "#5b727c",
    "accent": "#0f8b8d",
    "accent_dark": "#0a6668",
    "line": "#d7e2e7",
    "ok": "#2f9e44",
    "warn": "#c47f17",
}


class MonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metro Ethernet MPLS Monitor")
        self.geometry("1180x760")
        self.minsize(1040, 680)

        self.source = tk.StringVar(value="host1")
        self.destination = tk.StringVar(value="user1")
        self.status = tk.StringVar(value="San sang chay kiem thu that tren Mininet.")
        self.last_run = tk.StringVar(value="-")
        self.baseline_count = tk.StringVar(value="0")
        self.sweep_count = tk.StringVar(value="0")
        self.success_count = tk.StringVar(value="0")
        self.last_log_line = tk.StringVar(value="Chua co log.")
        self.is_running = False
        self.action_buttons: list[ttk.Button] = []
        self.log_buffer = ""
        self.log_window: tk.Toplevel | None = None
        self.log_text: tk.Text | None = None

        self._configure_style()
        self._build_ui()
        self.load_results()

    def _configure_style(self) -> None:
        self.configure(bg=COLORS["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("Surface.TFrame", background=COLORS["surface"], relief="flat")
        style.configure("Title.TLabel", background=COLORS["panel"], foreground="#ffffff", font=("DejaVu Sans", 19, "bold"))
        style.configure("Panel.TLabel", background=COLORS["panel"], foreground="#cfe3ea", font=("DejaVu Sans", 10))
        style.configure("Section.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("DejaVu Sans", 13, "bold"))
        style.configure("Body.TLabel", background=COLORS["surface"], foreground=COLORS["muted"], font=("DejaVu Sans", 10))
        style.configure("Metric.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("DejaVu Sans", 18, "bold"))
        style.configure("MetricName.TLabel", background=COLORS["surface"], foreground=COLORS["muted"], font=("DejaVu Sans", 9))
        style.configure("Status.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("DejaVu Sans", 10))
        style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff", arrowsize=16)
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="#ffffff", font=("DejaVu Sans", 10, "bold"), padding=(12, 8))
        style.map("Accent.TButton", background=[("active", COLORS["accent_dark"]), ("disabled", "#94b7bb")])
        style.configure("Ghost.TButton", background="#e5eef1", foreground=COLORS["text"], font=("DejaVu Sans", 10), padding=(12, 8))
        style.map("Ghost.TButton", background=[("active", "#d5e4e9"), ("disabled", "#edf2f4")])
        style.configure("Treeview", rowheight=30, background="#ffffff", fieldbackground="#ffffff", foreground=COLORS["text"], bordercolor=COLORS["line"])
        style.configure("Treeview.Heading", background="#dce9ed", foreground=COLORS["text"], font=("DejaVu Sans", 10, "bold"))
        style.map("Treeview", background=[("selected", COLORS["accent"])], foreground=[("selected", "#ffffff")])

    def _build_ui(self) -> None:
        shell = ttk.Frame(self, style="Root.TFrame")
        shell.pack(fill=tk.BOTH, expand=True)
        shell.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)

        canvas = tk.Canvas(shell, bg=COLORS["bg"], highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")

        page_scrollbar = ttk.Scrollbar(shell, orient=tk.VERTICAL, command=canvas.yview)
        page_scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=page_scrollbar.set)

        root = ttk.Frame(canvas, style="Root.TFrame", padding=18)
        window_id = canvas.create_window((0, 0), window=root, anchor="nw")

        def update_scroll_region(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_content_width(event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def scroll_page(event) -> None:
            widget = event.widget
            nested_scroll_widgets = (getattr(self, "tree", None),)
            while widget is not None:
                if widget in nested_scroll_widgets:
                    return
                widget = getattr(widget, "master", None)

            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        root.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_content_width)
        canvas.bind_all("<MouseWheel>", scroll_page)
        canvas.bind_all("<Button-4>", scroll_page)
        canvas.bind_all("<Button-5>", scroll_page)

        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, style="Panel.TFrame", padding=22)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text="Metro Ethernet\nMPLS Monitor", style="Title.TLabel", justify=tk.LEFT).grid(row=0, column=0, sticky="ew")
        ttk.Label(
            sidebar,
            text="Cong cu demo do ping, traceroute, throughput, jitter va packet loss that trong Mininet.",
            style="Panel.TLabel",
            wraplength=250,
            justify=tk.LEFT,
        ).grid(row=1, column=0, sticky="ew", pady=(10, 28))

        ttk.Label(sidebar, text="Source host", style="Panel.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Combobox(sidebar, textvariable=self.source, values=HOSTS, width=24, state="readonly").grid(row=3, column=0, sticky="ew", pady=(4, 14))
        ttk.Label(sidebar, text="Destination host", style="Panel.TLabel").grid(row=4, column=0, sticky="w")
        ttk.Combobox(sidebar, textvariable=self.destination, values=HOSTS, width=24, state="readonly").grid(row=5, column=0, sticky="ew", pady=(4, 18))

        self.action_buttons.clear()
        for index, (action, label) in enumerate(ACTION_LABELS.items(), start=6):
            button = ttk.Button(sidebar, text=label, style="Accent.TButton", command=lambda a=action: self.run_real_test(a))
            button.grid(row=index, column=0, sticky="ew", pady=4)
            self.action_buttons.append(button)

        full_button = ttk.Button(sidebar, text="Run Full Benchmark", style="Ghost.TButton", command=self.run_full_benchmark)
        full_button.grid(row=12, column=0, sticky="ew", pady=(18, 4))
        self.action_buttons.append(full_button)

        ttk.Button(sidebar, text="Open Charts", style="Ghost.TButton", command=self.open_images_dir).grid(row=13, column=0, sticky="ew", pady=4)
        ttk.Button(sidebar, text="Reload Results", style="Ghost.TButton", command=self.load_results).grid(row=14, column=0, sticky="ew", pady=4)

        content = ttk.Frame(root, style="Root.TFrame")
        content.grid(row=0, column=1, sticky="nsew")
        content.rowconfigure(2, weight=1)
        content.columnconfigure(0, weight=1)

        metrics = ttk.Frame(content, style="Root.TFrame")
        metrics.grid(row=0, column=0, sticky="ew")
        for col in range(4):
            metrics.columnconfigure(col, weight=1)
        self._metric_card(metrics, 0, "Baseline rows", self.baseline_count)
        self._metric_card(metrics, 1, "Load sweep rows", self.sweep_count)
        self._metric_card(metrics, 2, "Success rows", self.success_count)
        self._metric_card(metrics, 3, "Last run", self.last_run)

        status_bar = ttk.Frame(content, style="Root.TFrame")
        status_bar.grid(row=1, column=0, sticky="ew", pady=(16, 12))
        status_bar.columnconfigure(0, weight=1)
        ttk.Label(status_bar, textvariable=self.status, style="Status.TLabel").grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_bar, mode="indeterminate", length=210)
        self.progress.grid(row=0, column=1, sticky="e")

        table_panel = ttk.Frame(content, style="Surface.TFrame", padding=16)
        table_panel.grid(row=2, column=0, sticky="nsew")
        table_panel.rowconfigure(1, weight=1)
        table_panel.columnconfigure(0, weight=1)
        ttk.Label(table_panel, text="Ket qua do gan nhat", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(table_panel, text="Doc truc tiep tu results/results.csv", style="Body.TLabel").grid(row=0, column=1, sticky="e")

        columns = ("type", "load", "pair", "throughput", "delay", "loss", "jitter", "note")
        self.tree = ttk.Treeview(table_panel, columns=columns, show="headings", height=12)
        headings = {
            "type": "Type",
            "load": "Load",
            "pair": "Pair",
            "throughput": "Throughput",
            "delay": "Delay",
            "loss": "Loss",
            "jitter": "Jitter",
            "note": "Note",
        }
        widths = {"type": 112, "load": 70, "pair": 180, "throughput": 110, "delay": 80, "loss": 80, "jitter": 80, "note": 170}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=tk.CENTER if col != "pair" and col != "note" else tk.W)
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(12, 0))

        scrollbar = ttk.Scrollbar(table_panel, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky="ns", pady=(12, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)

        log_panel = ttk.Frame(content, style="Surface.TFrame", padding=16)
        log_panel.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        log_panel.columnconfigure(1, weight=1)
        ttk.Label(log_panel, text="Log chay lenh", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(log_panel, text="Open Log Window", style="Ghost.TButton", command=self.open_log_window).grid(row=0, column=2, sticky="e")
        ttk.Label(log_panel, textvariable=self.last_log_line, style="Body.TLabel").grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

    def _metric_card(self, parent: ttk.Frame, col: int, label: str, variable: tk.StringVar) -> None:
        card = ttk.Frame(parent, style="Surface.TFrame", padding=16)
        card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0 if col == 3 else 8))
        ttk.Label(card, text=label, style="MetricName.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable, style="Metric.TLabel").pack(anchor="w", pady=(6, 0))

    def command_prefix(self) -> list[str]:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            return [sys.executable]
        return ["sudo", "-n", sys.executable]

    def set_running(self, running: bool) -> None:
        self.is_running = running
        for button in self.action_buttons:
            button.configure(state=tk.DISABLED if running else tk.NORMAL)
        if running:
            self.progress.start(10)
        else:
            self.progress.stop()

    def run_full_benchmark(self) -> None:
        if self.is_running:
            return
        self.status.set("Dang chay full benchmark that trong Mininet...")
        cmd = self.command_prefix() + [str(PROJECT_DIR / "code" / "performance_test.py"), "--mode", "mpls"]
        self.start_worker(cmd, "full benchmark")

    def run_real_test(self, action: str) -> None:
        if self.is_running:
            return
        source = self.source.get().strip()
        destination = self.destination.get().strip()
        if source == destination:
            self.status.set("Source va destination phai khac nhau.")
            return
        self.status.set(f"Dang chay {ACTION_LABELS[action]} cho {source} -> {destination}...")
        cmd = self.command_prefix() + [
            str(PROJECT_DIR / "code" / "performance_test.py"),
            "--action",
            action,
            "--source-host",
            source,
            "--destination-host",
            destination,
            "--mode",
            "mpls",
        ]
        self.start_worker(cmd, f"{ACTION_LABELS[action]} {source}->{destination}")

    def start_worker(self, cmd: list[str], label: str) -> None:
        self.set_running(True)
        self.append_log(f"\n=== {label} ===\n{' '.join(cmd)}\n")
        thread = threading.Thread(target=self._run_command_worker, args=(cmd,), daemon=True)
        thread.start()

    def _run_command_worker(self, cmd: list[str]) -> None:
        proc = subprocess.run(cmd, cwd=PROJECT_DIR, text=True, capture_output=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.after(0, lambda: self._finish_run(proc.returncode, output))

    def _finish_run(self, returncode: int, output: str) -> None:
        display_output = self.clean_command_output(output)
        if display_output:
            self.append_log(display_output + "\n")
        self.set_running(False)
        if returncode == 0:
            self.status.set("Hoan tat. Ket qua vua chay la lenh that trong namespace Mininet.")
        else:
            self.status.set("Lenh chua chay duoc. Neu loi sudo, hay chay `sudo -v` trong terminal truoc.")
        self.load_results()

    def load_results(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not CSV_PATH.exists():
            self.status.set("Chua co results/results.csv. Hay chay full benchmark truoc.")
            return

        baseline = 0
        sweep = 0
        success = 0
        last_timestamp = "-"
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                test_type = row.get("test_type") or "baseline"
                if test_type == "baseline":
                    baseline += 1
                elif test_type == "udp_load_sweep":
                    sweep += 1
                if row.get("note") == "success":
                    success += 1
                last_timestamp = row.get("timestamp") or last_timestamp
                pair = f"{row.get('source_branch', '')} -> {row.get('destination_branch', '')}"
                load = f"{row.get('load_mbps')}M" if row.get("load_mbps") else "-"
                values = (
                    test_type,
                    load,
                    pair,
                    self.clean_value(row.get("throughput_mbps")),
                    self.clean_value(row.get("avg_delay_ms")),
                    self.clean_value(row.get("udp_packet_loss_percent") or row.get("packet_loss_percent")),
                    self.clean_value(row.get("jitter_ms")),
                    row.get("note", "-"),
                )
                self.tree.insert("", tk.END, values=values)

        self.baseline_count.set(str(baseline))
        self.sweep_count.set(str(sweep))
        self.success_count.set(str(success))
        self.last_run.set(last_timestamp.split("T")[-1] if "T" in last_timestamp else last_timestamp)

    @staticmethod
    def clean_value(value: str | None) -> str:
        if value is None or value == "":
            return "-"
        try:
            return f"{float(value):.3g}"
        except ValueError:
            return value

    @staticmethod
    def clean_command_output(output: str) -> str:
        cleaned_lines = []
        for line in output.splitlines():
            lowered = line.lower()
            if any(marker in lowered for marker in HIDDEN_WARNING_MARKERS):
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def append_log(self, text: str) -> None:
        self.log_buffer += text
        last_line = next((line for line in reversed(self.log_buffer.splitlines()) if line.strip()), "Chua co log.")
        self.last_log_line.set(last_line[:140])
        if self.log_text is None:
            return
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.configure(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def clear_log(self) -> None:
        self.log_buffer = ""
        self.last_log_line.set("Chua co log.")
        if self.log_text is None:
            return
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def open_log_window(self) -> None:
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.lift()
            self.log_window.focus_force()
            return

        window = tk.Toplevel(self)
        window.title("Log chay lenh")
        window.geometry("980x620")
        window.minsize(720, 420)
        window.configure(bg=COLORS["bg"])
        window.rowconfigure(1, weight=1)
        window.columnconfigure(0, weight=1)

        toolbar = ttk.Frame(window, style="Root.TFrame", padding=(14, 12, 14, 8))
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(0, weight=1)
        ttk.Label(toolbar, text="Log chay lenh", style="Status.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(toolbar, text="Clear", style="Ghost.TButton", command=self.clear_log).grid(row=0, column=1, sticky="e")

        log_frame = ttk.Frame(window, style="Root.TFrame", padding=(14, 0, 14, 14))
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        text = tk.Text(
            log_frame,
            bg="#0f222a",
            fg="#e8f3f7",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            font=("DejaVu Sans Mono", 10),
            padx=12,
            pady=10,
            wrap=tk.NONE,
        )
        text.grid(row=0, column=0, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=text.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar = ttk.Scrollbar(log_frame, orient=tk.HORIZONTAL, command=text.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        text.insert(tk.END, self.log_buffer)
        text.configure(state=tk.DISABLED)
        text.see(tk.END)

        self.log_window = window
        self.log_text = text

        def on_close() -> None:
            self.log_text = None
            self.log_window = None
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

    def open_images_dir(self) -> None:
        subprocess.Popen(["xdg-open", str(PROJECT_DIR / "images")])


if __name__ == "__main__":
    app = MonitorApp()
    app.mainloop()
