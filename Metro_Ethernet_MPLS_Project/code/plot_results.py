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


def baseline_results(df: pd.DataFrame) -> pd.DataFrame:
    if "test_type" not in df.columns:
        return df
    filtered = df[df["test_type"].fillna("baseline") == "baseline"].copy()
    if filtered.empty:
        raise SystemExit("ERROR: results.csv khong co du lieu baseline de ve throughput/delay/jitter.")
    return filtered


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


def packet_loss_chart(df: pd.DataFrame) -> None:
    if "test_type" in df.columns:
        loss_df = df[df["test_type"] == "udp_load_sweep"].copy()
    else:
        loss_df = pd.DataFrame()

    if not loss_df.empty and "load_mbps" in loss_df.columns:
        loss_df["load_mbps"] = pd.to_numeric(loss_df["load_mbps"], errors="coerce")
        loss_df["udp_packet_loss_percent"] = pd.to_numeric(loss_df["udp_packet_loss_percent"], errors="coerce")
        plt.figure(figsize=(9, 5))
        for pair, group in loss_df.groupby("pair"):
            group = group.sort_values("load_mbps")
            plt.plot(
                group["load_mbps"],
                group["udp_packet_loss_percent"],
                marker="o",
                linewidth=2,
                label=pair,
            )
        plt.title("UDP packet loss khi tai mang tang", fontweight="bold")
        plt.xlabel("UDP offered load (Mbps)")
        plt.ylabel("UDP packet loss (%)")
        plt.grid(True, linestyle="--", alpha=0.35)
        plt.legend()
        plt.tight_layout()
        plt.savefig(IMAGE_DIR / "packet_loss_chart.png", dpi=180)
        plt.close()
        return

    baseline_df = baseline_results(df)
    bar_chart(
        baseline_df,
        "packet_loss_percent",
        "Packet loss (%)",
        "Ti le mat goi do bang ping",
        "packet_loss_chart.png",
        "#e86f61",
    )


def main():
    df = load_results()
    baseline_df = baseline_results(df)
    bar_chart(baseline_df, "throughput_mbps", "Throughput (Mbps)", "Throughput do bang iperf3 TCP", "throughput_chart.png", "#4aa3df")
    bar_chart(baseline_df, "avg_delay_ms", "Delay trung binh (ms)", "Delay trung binh do bang ping", "delay_chart.png", "#f2b84b")
    packet_loss_chart(df)
    bar_chart(baseline_df, "jitter_ms", "Jitter (ms)", "Jitter do bang iperf3 UDP", "jitter_chart.png", "#7cc36b")
    print(f"Charts saved to {IMAGE_DIR}")


if __name__ == "__main__":
    main()
