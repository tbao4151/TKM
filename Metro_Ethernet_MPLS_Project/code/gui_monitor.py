#!/usr/bin/env python3
"""GUI Tkinter demo: chay script kiem thu that va hien thi log/ket qua."""

from __future__ import annotations

import csv
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_DIR / "results"
CSV_PATH = RESULTS_DIR / "results.csv"


class MonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metro Ethernet MPLS-like Monitor")
        self.geometry("980x640")
        self.source = tk.StringVar(value="host1")
        self.destination = tk.StringVar(value="admin1")
        self.status = tk.StringVar(value="San sang. Cac nut se chay performance_test.py that trong Mininet.")
        self._build_ui()
        self.load_results()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Source host").grid(row=0, column=0, sticky=tk.W)
        hosts = ["host1", "host2", "host3", "host4", "admin1", "admin2", "user1", "user2", "guest1", "guest2", "svr1", "svr2", "svr3a", "svr3b", "svr4", "os1", "os2"]
        ttk.Combobox(top, textvariable=self.source, values=hosts, width=12).grid(row=0, column=1, padx=6)
        ttk.Label(top, text="Destination host").grid(row=0, column=2, sticky=tk.W)
        ttk.Combobox(top, textvariable=self.destination, values=hosts, width=12).grid(row=0, column=3, padx=6)

        buttons = [
            ("Ping", self.run_real_tests),
            ("Traceroute", self.run_real_tests),
            ("Throughput Test", self.run_real_tests),
            ("Delay Test", self.run_real_tests),
            ("Packet Loss Test", self.run_real_tests),
            ("Jitter Test", self.run_real_tests),
            ("Mo bieu do", self.open_images_dir),
        ]
        for idx, (text, cmd) in enumerate(buttons):
            ttk.Button(top, text=text, command=cmd).grid(row=1, column=idx, padx=4, pady=8)

        ttk.Label(self, textvariable=self.status).pack(fill=tk.X, padx=10)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        cols = ("pair", "throughput", "delay", "loss", "jitter", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for col, text in zip(cols, ["Pair", "Throughput Mbps", "Delay ms", "Loss %", "Jitter ms", "Note"]):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=140 if col != "note" else 260)
        self.tree.pack(fill=tk.X)

        self.log = tk.Text(table_frame, height=18)
        self.log.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.log.insert(tk.END, "Phai co quyen sudo de performance_test.py tao topology Mininet va chay lenh do that.\n")

    def run_real_tests(self):
        self.status.set("Dang chay performance_test.py that trong Mininet...")
        self.log.insert(tk.END, "\n=== Chay full test that: sudo python3 code/performance_test.py ===\n")
        thread = threading.Thread(target=self._run_real_tests_worker, daemon=True)
        thread.start()

    def _run_real_tests_worker(self):
        cmd = ["sudo", sys.executable, str(PROJECT_DIR / "code" / "performance_test.py")]
        proc = subprocess.run(cmd, cwd=PROJECT_DIR, text=True, capture_output=True)
        output = (proc.stdout or "") + (proc.stderr or "")
        self.after(0, lambda: self._finish_run(proc.returncode, output))

    def _finish_run(self, returncode: int, output: str):
        self.log.insert(tk.END, output + "\n")
        self.status.set("Hoan tat." if returncode == 0 else f"Loi khi chay test, ma loi {returncode}.")
        self.load_results()

    def load_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not CSV_PATH.exists():
            return
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pair = f"{row['source_branch']} -> {row['destination_branch']}"
                self.tree.insert("", tk.END, values=(pair, row["throughput_mbps"], row["avg_delay_ms"], row["packet_loss_percent"], row["jitter_ms"], row["note"]))

    def open_images_dir(self):
        subprocess.Popen(["xdg-open", str(PROJECT_DIR / "images")])


if __name__ == "__main__":
    app = MonitorApp()
    app.mainloop()
