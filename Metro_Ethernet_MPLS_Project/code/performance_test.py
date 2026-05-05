#!/usr/bin/env python3
"""Chay kiem thu hieu nang that trong Mininet va ghi results.csv."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_DIR / "results"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from mininet.log import setLogLevel

from network_config import HOST_IP, TEST_PAIRS, TestPair, connectivity_checks
from topology_mininet import start_configured_network


PING_TIMEOUT_SECONDS = 25
TRACEROUTE_TIMEOUT_SECONDS = 20
IPERF_CLIENT_TIMEOUT_SECONDS = 18
IPERF_SERVER_TIMEOUT_SECONDS = 25

CSV_FIELDS = [
    "timestamp",
    "source_branch",
    "destination_branch",
    "source_host",
    "destination_host",
    "throughput_mbps",
    "avg_delay_ms",
    "packet_loss_percent",
    "jitter_ms",
    "udp_packet_loss_percent",
    "test_tool",
    "note",
]


def append_log(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


def progress(message: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} | {message}"
    print(line, flush=True)
    append_log(RESULTS_DIR / "command_history.txt", line)


def record_command(command: str) -> None:
    append_log(RESULTS_DIR / "command_history.txt", f"{datetime.now().isoformat(timespec='seconds')} | {command}")


def parse_ping(output: str) -> Tuple[Optional[float], Optional[float]]:
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss", output)
    avg_match = re.search(r"rtt min/avg/max/(?:mdev|stddev) = [\d.]+/([\d.]+)/", output)
    loss = float(loss_match.group(1)) if loss_match else None
    avg = float(avg_match.group(1)) if avg_match else None
    return avg, loss


def parse_iperf_tcp(json_text: str) -> Optional[float]:
    data = json.loads(json_text)
    bps = data.get("end", {}).get("sum_received", {}).get("bits_per_second")
    if bps is None:
        bps = data.get("end", {}).get("sum_sent", {}).get("bits_per_second")
    return round(float(bps) / 1_000_000, 3) if bps is not None else None


def parse_iperf_udp(json_text: str) -> Tuple[Optional[float], Optional[float]]:
    data = json.loads(json_text)
    udp_sum = data.get("end", {}).get("sum")
    if not udp_sum:
        streams = data.get("end", {}).get("streams", [])
        udp_sum = streams[0].get("udp") if streams else None
    if not udp_sum:
        return None, None
    jitter = udp_sum.get("jitter_ms")
    loss = udp_sum.get("lost_percent")
    parsed_jitter = round(float(jitter), 3) if jitter is not None and math.isfinite(float(jitter)) else None
    parsed_loss = round(float(loss), 3) if loss is not None and math.isfinite(float(loss)) else None
    return parsed_jitter, parsed_loss


def run_ping(src, dst_ip: str) -> Tuple[Optional[float], Optional[float], str]:
    cmd = f"timeout {PING_TIMEOUT_SECONDS}s ping -c 8 -W 2 {dst_ip}"
    record_command(f"{src.name}: {cmd}")
    output = src.cmd(cmd)
    append_log(RESULTS_DIR / "ping_results.txt", f"\n===== {src.name} -> {dst_ip} =====\n{output}")
    avg, loss = parse_ping(output)
    return avg, loss, output


def run_traceroute(src, dst_ip: str) -> str:
    cmd = f"timeout {TRACEROUTE_TIMEOUT_SECONDS}s traceroute -n -w 2 -q 1 {dst_ip}"
    record_command(f"{src.name}: {cmd}")
    output = src.cmd(cmd)
    append_log(RESULTS_DIR / "traceroute_results.txt", f"\n===== {src.name} -> {dst_ip} =====\n{output}")
    return output


def run_iperf3_tcp(src, dst, dst_ip: str, port: int) -> Tuple[Optional[float], str]:
    dst.cmd("pkill -f 'iperf3 -s' || true")
    server_cmd = f"timeout {IPERF_SERVER_TIMEOUT_SECONDS}s iperf3 -s -1 -p {port}"
    client_cmd = f"timeout {IPERF_CLIENT_TIMEOUT_SECONDS}s iperf3 -c {dst_ip} -p {port} -t 5 -J"
    record_command(f"{dst.name}: {server_cmd}")
    dst.cmd(f"{server_cmd} >/tmp/{dst.name}_{port}_tcp.log 2>&1 &")
    record_command(f"{src.name}: {client_cmd}")
    output = src.cmd(client_cmd)
    server_output = dst.cmd(f"cat /tmp/{dst.name}_{port}_tcp.log 2>/dev/null")
    append_log(
        RESULTS_DIR / "iperf_results.txt",
        f"\n===== TCP {src.name} -> {dst.name} ({dst_ip}) =====\nCLIENT:\n{output}\nSERVER:\n{server_output}",
    )
    try:
        return parse_iperf_tcp(output), output
    except Exception as exc:
        return None, f"{output}\nPARSE_ERROR: {exc}"


def run_iperf3_udp_jitter(src, dst, dst_ip: str, port: int) -> Tuple[Optional[float], Optional[float], str]:
    dst.cmd("pkill -f 'iperf3 -s' || true")
    server_cmd = f"timeout {IPERF_SERVER_TIMEOUT_SECONDS}s iperf3 -s -1 -p {port}"
    client_cmd = f"timeout {IPERF_CLIENT_TIMEOUT_SECONDS}s iperf3 -u -b 10M -c {dst_ip} -p {port} -t 5 -J"
    record_command(f"{dst.name}: {server_cmd}")
    dst.cmd(f"{server_cmd} >/tmp/{dst.name}_{port}_udp.log 2>&1 &")
    record_command(f"{src.name}: {client_cmd}")
    output = src.cmd(client_cmd)
    server_output = dst.cmd(f"cat /tmp/{dst.name}_{port}_udp.log 2>/dev/null")
    append_log(
        RESULTS_DIR / "iperf_results.txt",
        f"\n===== UDP JITTER {src.name} -> {dst.name} ({dst_ip}) =====\nCLIENT:\n{output}\nSERVER:\n{server_output}",
    )
    try:
        jitter, udp_loss = parse_iperf_udp(output)
        return jitter, udp_loss, output
    except Exception as exc:
        return None, None, f"{output}\nPARSE_ERROR: {exc}"


def row_for_pair(net, pair: TestPair, port_base: int) -> Dict[str, object]:
    src = net.get(pair.source_host)
    dst = net.get(pair.destination_host)
    dst_ip = HOST_IP[pair.destination_host]
    timestamp = datetime.now().isoformat(timespec="seconds")

    progress(f"Testing {pair.source_branch} -> {pair.destination_branch}: {pair.source_host} -> {pair.destination_host}")
    avg_delay, loss, ping_output = run_ping(src, dst_ip)
    traceroute_output = run_traceroute(src, dst_ip)

    notes = []
    throughput = None
    jitter = None
    udp_loss = None
    if loss is None:
        notes.append("ping_parse_failed")
    if loss is None or loss >= 100:
        throughput = 0.0
        jitter = 0.0
        udp_loss = 100.0
        notes.append("ping_failed_or_timed_out; iperf_skipped")
    else:
        progress(f"Running iperf3 TCP for {pair.source_host} -> {pair.destination_host}")
        throughput, tcp_output = run_iperf3_tcp(src, dst, dst_ip, port_base)
        if throughput is None:
            throughput = 0.0
            notes.append("iperf_tcp_failed")
        progress(f"Running iperf3 UDP jitter for {pair.source_host} -> {pair.destination_host}")
        jitter, udp_loss, udp_output = run_iperf3_udp_jitter(src, dst, dst_ip, port_base + 100)
        if jitter is None:
            jitter = 0.0
            notes.append("iperf_udp_jitter_failed")
        if udp_loss is None:
            udp_loss = 0.0
            notes.append("iperf_udp_loss_parse_failed")

    if "traceroute to" not in traceroute_output:
        notes.append("traceroute_failed")
    if not notes:
        notes.append("success")
    elif not notes[0].startswith("fail"):
        notes.insert(0, "fail")

    return {
        "timestamp": timestamp,
        "source_branch": pair.source_branch,
        "destination_branch": pair.destination_branch,
        "source_host": pair.source_host,
        "destination_host": pair.destination_host,
        "throughput_mbps": throughput if throughput is not None else 0.0,
        "avg_delay_ms": avg_delay if avg_delay is not None else 0.0,
        "packet_loss_percent": loss if loss is not None else 100.0,
        "jitter_ms": jitter if jitter is not None else 0.0,
        "udp_packet_loss_percent": udp_loss if udp_loss is not None else 0.0,
        "test_tool": "ping; iperf3 TCP; iperf3 UDP; traceroute",
        "note": "; ".join(notes),
    }


def reset_logs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("ping_results.txt", "iperf_results.txt", "traceroute_results.txt", "command_history.txt"):
        (RESULTS_DIR / name).write_text("", encoding="utf-8")


def run_all_tests() -> int:
    setLogLevel("warning")
    reset_logs()
    append_log(RESULTS_DIR / "command_history.txt", f"Test run started: {datetime.now().isoformat(timespec='seconds')}")
    net = None
    rows = []
    try:
        progress("Starting Mininet topology for real performance tests")
        net = start_configured_network()
        progress("Topology started and configured; running precheck pings")
        for src, dst, ok, output in connectivity_checks(net):
            append_log(RESULTS_DIR / "ping_results.txt", f"\n===== PRECHECK {src} -> {dst} =====\n{output}")
            if not ok:
                append_log(RESULTS_DIR / "command_history.txt", f"PRECHECK_FAIL {src}->{dst}")
            progress(f"Precheck {src} -> {dst}: {'OK' if ok else 'FAIL'}")
        for index, pair in enumerate(TEST_PAIRS, start=1):
            rows.append(row_for_pair(net, pair, 5200 + index))
    except Exception as exc:
        progress(f"ERROR: performance test aborted: {exc}")
        append_log(RESULTS_DIR / "ping_results.txt", f"\n===== TEST ABORTED =====\n{exc}\n")
        raise
    finally:
        if net is not None:
            progress("Stopping Mininet topology")
            net.stop()

    csv_path = RESULTS_DIR / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    append_log(RESULTS_DIR / "command_history.txt", f"Test run finished: {datetime.now().isoformat(timespec='seconds')}")
    print(f"Wrote real test results to {csv_path}")
    return 0 if rows else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real Mininet performance tests")
    parser.parse_args()
    return run_all_tests()


if __name__ == "__main__":
    raise SystemExit(main())
