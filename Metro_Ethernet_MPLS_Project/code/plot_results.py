#!/usr/bin/env python3
"""Ve bieu do tu results/results.csv that."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_CSV = PROJECT_DIR / "results" / "results.csv"
IMAGE_DIR = PROJECT_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def load_results() -> pd.DataFrame:
    if not RESULTS_CSV.exists() or RESULTS_CSV.stat().st_size == 0:
        raise SystemExit(f"ERROR: {RESULTS_CSV} chua ton tai hoac rong. Hay chay performance_test.py truoc.")
    df = pd.read_csv(RESULTS_CSV)
    if df.empty:
        raise SystemExit("ERROR: results.csv khong co dong du lieu that.")
    required = {"source_branch", "destination_branch", "throughput_mbps", "avg_delay_ms", "packet_loss_percent", "jitter_ms"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"ERROR: results.csv thieu cot: {', '.join(sorted(missing))}")
    df["pair"] = df["source_branch"] + " -> " + df["destination_branch"]
    if "mode" in df.columns:
        df["pair"] = df["mode"].astype(str).str.upper() + ": " + df["pair"]
    return df


def bar_chart(df: pd.DataFrame, column: str, ylabel: str, title: str, filename: str, color: str) -> None:
    plt.figure(figsize=(9, 5))
    bars = plt.bar(df["pair"], df[column], color=color, edgecolor="#22313f")
    plt.title(title, fontweight="bold")
    plt.ylabel(ylabel)
    plt.xlabel("Cap chi nhanh kiem thu")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.xticks(rotation=18, ha="right")
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.3g}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / filename, dpi=180)
    plt.close()


def main():
    df = load_results()
    bar_chart(df, "throughput_mbps", "Throughput (Mbps)", "Throughput do bang iperf3 TCP", "throughput_chart.png", "#4aa3df")
    bar_chart(df, "avg_delay_ms", "Delay trung binh (ms)", "Delay trung binh do bang ping", "delay_chart.png", "#f2b84b")
    loss_column = "udp_packet_loss_percent" if "udp_packet_loss_percent" in df.columns else "packet_loss_percent"
    loss_title = "UDP packet loss do bang iperf3" if loss_column == "udp_packet_loss_percent" else "Ti le mat goi do bang ping"
    bar_chart(df, loss_column, "Packet loss (%)", loss_title, "packet_loss_chart.png", "#e86f61")
    bar_chart(df, "jitter_ms", "Jitter (ms)", "Jitter do bang iperf3 UDP", "jitter_chart.png", "#7cc36b")
    print(f"Charts saved to {IMAGE_DIR}")


if __name__ == "__main__":
    main()
