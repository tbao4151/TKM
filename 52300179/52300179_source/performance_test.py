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

from network_config import (
    HOST_IP,
    TEST_PAIRS,
    TestPair,
    capture_mpls_packets,
    collect_frr_state,
    collect_mpls_state,
    connectivity_checks,
)
from topology_mininet import start_configured_network


PING_TIMEOUT_SECONDS = 25
TRACEROUTE_TIMEOUT_SECONDS = 20
IPERF_CLIENT_TIMEOUT_SECONDS = 18
IPERF_SERVER_TIMEOUT_SECONDS = 25

CSV_FIELDS = [
    "timestamp",
    "mode",
    "test_type",
    "load_mbps",
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

UDP_LOAD_LEVELS = [5, 20, 50, 80, 120]
CROSS_BRANCH_SWEEP_PAIRS = [pair for pair in TEST_PAIRS if pair.source_branch != pair.destination_branch]


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


def run_iperf3_udp(src, dst, dst_ip: str, port: int, bandwidth_mbps: int, label: str) -> Tuple[Optional[float], Optional[float], str]:
    dst.cmd("pkill -f 'iperf3 -s' || true")
    server_cmd = f"timeout {IPERF_SERVER_TIMEOUT_SECONDS}s iperf3 -s -1 -p {port}"
    client_cmd = f"timeout {IPERF_CLIENT_TIMEOUT_SECONDS}s iperf3 -u -b {bandwidth_mbps}M -c {dst_ip} -p {port} -t 5 -J"
    record_command(f"{dst.name}: {server_cmd}")
    dst.cmd(f"{server_cmd} >/tmp/{dst.name}_{port}_udp.log 2>&1 &")
    record_command(f"{src.name}: {client_cmd}")
    output = src.cmd(client_cmd)
    server_output = dst.cmd(f"cat /tmp/{dst.name}_{port}_udp.log 2>/dev/null")
    append_log(
        RESULTS_DIR / "iperf_results.txt",
        f"\n===== {label} {src.name} -> {dst.name} ({dst_ip}) @ {bandwidth_mbps}M =====\nCLIENT:\n{output}\nSERVER:\n{server_output}",
    )
    try:
        jitter, udp_loss = parse_iperf_udp(output)
        return jitter, udp_loss, output
    except Exception as exc:
        return None, None, f"{output}\nPARSE_ERROR: {exc}"


def run_iperf3_udp_jitter(src, dst, dst_ip: str, port: int) -> Tuple[Optional[float], Optional[float], str]:
    return run_iperf3_udp(src, dst, dst_ip, port, bandwidth_mbps=10, label="UDP JITTER")


def row_for_pair(net, pair: TestPair, port_base: int, mode: str) -> Dict[str, object]:
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
        if throughput is None or throughput <= 0:
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
        "mode": mode,
        "test_type": "baseline",
        "load_mbps": None,
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


def udp_load_sweep_rows(net, pair: TestPair, port_base: int, mode: str) -> list[Dict[str, object]]:
    src = net.get(pair.source_host)
    dst = net.get(pair.destination_host)
    dst_ip = HOST_IP[pair.destination_host]
    rows = []

    for offset, bandwidth_mbps in enumerate(UDP_LOAD_LEVELS, start=1):
        progress(
            "Running UDP load sweep "
            f"{pair.source_host} -> {pair.destination_host} at {bandwidth_mbps} Mbps"
        )
        jitter, udp_loss, _ = run_iperf3_udp(
            src,
            dst,
            dst_ip,
            port_base + offset,
            bandwidth_mbps=bandwidth_mbps,
            label="UDP LOAD SWEEP",
        )
        note = "success"
        if jitter is None or udp_loss is None:
            note = "fail; iperf_udp_load_sweep_failed"
        rows.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "mode": mode,
                "test_type": "udp_load_sweep",
                "load_mbps": bandwidth_mbps,
                "source_branch": pair.source_branch,
                "destination_branch": pair.destination_branch,
                "source_host": pair.source_host,
                "destination_host": pair.destination_host,
                "throughput_mbps": None,
                "avg_delay_ms": None,
                "packet_loss_percent": None,
                "jitter_ms": jitter,
                "udp_packet_loss_percent": udp_loss,
                "test_tool": "iperf3 UDP",
                "note": note,
            }
        )

    return rows


def reset_logs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in (
        "ping_results.txt",
        "iperf_results.txt",
        "traceroute_results.txt",
        "mpls_routes.txt",
        "frr_control_plane.txt",
        "tcpdump_mpls.txt",
        "command_history.txt",
    ):
        (RESULTS_DIR / name).write_text("", encoding="utf-8")


def save_mpls_verification(net) -> None:
    progress("Saving Linux kernel MPLS route tables")
    mpls_state = collect_mpls_state(net)
    append_log(RESULTS_DIR / "mpls_routes.txt", mpls_state)
    progress("Saving FRRouting OSPF/LDP control-plane state")
    frr_state = collect_frr_state(net)
    append_log(RESULTS_DIR / "frr_control_plane.txt", frr_state)
    if "Full" not in frr_state or "OPERATIONAL" not in frr_state:
        raise RuntimeError("FRRouting OSPF/LDP chua hoi tu du: khong thay OSPF Full hoac LDP OPERATIONAL")
    progress("Capturing real MPLS packets on p3-eth0")
    capture_output = capture_mpls_packets(net)
    append_log(RESULTS_DIR / "tcpdump_mpls.txt", capture_output)
    if "MPLS" not in capture_output:
        raise RuntimeError("tcpdump khong bat duoc goi MPLS tren p3-eth0")


def run_all_tests(mode: str = "mpls", stp_wait: int = 20) -> int:
    setLogLevel("warning")
    reset_logs()
    append_log(RESULTS_DIR / "command_history.txt", f"Test run started: {datetime.now().isoformat(timespec='seconds')} | mode={mode}")
    net = None
    rows = []
    try:
        progress(f"Starting Mininet topology for real performance tests in {mode} mode")
        net = start_configured_network(mode=mode, stp_wait=stp_wait)
        progress("Topology started and configured; running precheck pings")
        for src, dst, ok, output in connectivity_checks(net):
            append_log(RESULTS_DIR / "ping_results.txt", f"\n===== PRECHECK {src} -> {dst} =====\n{output}")
            if not ok:
                append_log(RESULTS_DIR / "command_history.txt", f"PRECHECK_FAIL {src}->{dst}")
            progress(f"Precheck {src} -> {dst}: {'OK' if ok else 'FAIL'}")
        if mode == "mpls":
            save_mpls_verification(net)
        for index, pair in enumerate(TEST_PAIRS, start=1):
            rows.append(row_for_pair(net, pair, 5200 + index, mode))
        for sweep_index, pair in enumerate(CROSS_BRANCH_SWEEP_PAIRS, start=1):
            rows.extend(udp_load_sweep_rows(net, pair, 6200 + sweep_index * 10, mode))
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
    append_log(RESULTS_DIR / "command_history.txt", f"Test run finished: {datetime.now().isoformat(timespec='seconds')} | mode={mode}")
    print(f"Wrote real test results to {csv_path}")
    return 0 if rows else 1


def run_single_action(
    mode: str,
    source_host: str,
    destination_host: str,
    action: str,
    stp_wait: int = 20,
) -> int:
    if source_host not in HOST_IP:
        raise SystemExit(f"ERROR: unknown source host {source_host}")
    if destination_host not in HOST_IP:
        raise SystemExit(f"ERROR: unknown destination host {destination_host}")
    if source_host == destination_host:
        raise SystemExit("ERROR: source_host va destination_host phai khac nhau.")

    setLogLevel("warning")
    net = None
    try:
        progress(f"Starting Mininet topology for GUI/one-shot action in {mode} mode")
        net = start_configured_network(mode=mode, stp_wait=stp_wait)
        src = net.get(source_host)
        dst = net.get(destination_host)
        dst_ip = HOST_IP[destination_host]

        if action == "ping":
            avg_delay, loss, output = run_ping(src, dst_ip)
            print(output)
            print(f"SUMMARY: avg_delay_ms={avg_delay} packet_loss_percent={loss}")
        elif action == "traceroute":
            print(run_traceroute(src, dst_ip))
        elif action == "throughput":
            throughput, output = run_iperf3_tcp(src, dst, dst_ip, 7201)
            print(output)
            print(f"SUMMARY: throughput_mbps={throughput}")
        elif action == "delay":
            avg_delay, loss, output = run_ping(src, dst_ip)
            print(output)
            print(f"SUMMARY: avg_delay_ms={avg_delay} packet_loss_percent={loss}")
        elif action == "jitter":
            jitter, udp_loss, output = run_iperf3_udp_jitter(src, dst, dst_ip, 7301)
            print(output)
            print(f"SUMMARY: jitter_ms={jitter} udp_packet_loss_percent={udp_loss}")
        elif action == "packet-loss":
            print(f"UDP packet loss sweep for {source_host} -> {destination_host}")
            for bandwidth_mbps in UDP_LOAD_LEVELS:
                jitter, udp_loss, output = run_iperf3_udp(
                    src,
                    dst,
                    dst_ip,
                    7400 + bandwidth_mbps,
                    bandwidth_mbps=bandwidth_mbps,
                    label="UDP LOAD SWEEP",
                )
                print(f"\n===== UDP LOAD {bandwidth_mbps}M =====")
                print(output)
                print(
                    f"load_mbps={bandwidth_mbps}, jitter_ms={jitter}, "
                    f"udp_packet_loss_percent={udp_loss}"
                )
        else:
            raise SystemExit(f"ERROR: unsupported action {action}")
        return 0
    finally:
        if net is not None:
            progress("Stopping Mininet topology")
            net.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real Mininet performance tests")
    parser.add_argument("--mode", choices=("ip", "mpls"), default="mpls", help="forwarding mode")
    parser.add_argument("--stp-wait", type=int, default=20, help="seconds to wait after OVS startup")
    parser.add_argument(
        "--action",
        choices=("full", "ping", "traceroute", "throughput", "delay", "packet-loss", "jitter"),
        default="full",
        help="run the full benchmark pipeline or a single real test",
    )
    parser.add_argument("--source-host", help="optional source host for single-test mode")
    parser.add_argument("--destination-host", help="optional destination host for single-test mode")
    args = parser.parse_args()
    if args.action == "full":
        return run_all_tests(mode=args.mode, stp_wait=args.stp_wait)
    if not args.source_host or not args.destination_host:
        raise SystemExit("ERROR: --source-host va --destination-host bat buoc trong single-test mode.")
    return run_single_action(
        mode=args.mode,
        source_host=args.source_host,
        destination_host=args.destination_host,
        action=args.action,
        stp_wait=args.stp_wait,
    )


if __name__ == "__main__":
    raise SystemExit(main())
