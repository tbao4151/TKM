#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$PROJECT_DIR/results"
LOG_FILE="$RESULTS_DIR/environment_check.txt"
mkdir -p "$RESULTS_DIR"

{
  echo "Environment check time: $(date -Iseconds)"
  echo "OS information:"
  if command -v lsb_release >/dev/null 2>&1; then
    lsb_release -a || true
  else
    cat /etc/os-release || true
  fi
  echo
} > "$LOG_FILE"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run with sudo: sudo bash code/install_environment.sh" | tee -a "$LOG_FILE"
  exit 1
fi

required_cmds=(mn ovs-vsctl iperf3 traceroute tcpdump python3 vtysh)
missing_cmd=0
for cmd in "${required_cmds[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing_cmd=1
  fi
done

if [[ "$missing_cmd" -eq 1 ]]; then
  apt update || echo "WARNING: apt update failed for one or more repositories; continuing with apt install"
  apt install -y \
    mininet openvswitch-switch openvswitch-common iperf iperf3 traceroute \
    tcpdump tshark ethtool mtr net-tools iproute2 frr python3 python3-pip python3-venv \
    git curl python3-networkx python3-matplotlib python3-pandas python3-docx
else
  echo "Required system commands already installed; skipping apt install." | tee -a "$LOG_FILE"
fi

modprobe mpls_router
modprobe mpls_iptunnel
modprobe mpls_gso || true
sysctl -w net.mpls.platform_labels=100000

if ! python3 - <<'PY'
import importlib
for name in ["networkx", "matplotlib", "pandas", "docx"]:
    importlib.import_module(name)
PY
then
  if ! timeout 180 python3 -m pip install -r "$PROJECT_DIR/requirements.txt" --break-system-packages; then
    python3 -m venv "$PROJECT_DIR/venv"
    "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
  fi
fi

{
  echo
  echo "Command availability:"
  for cmd in mn ovs-vsctl iperf iperf3 traceroute tcpdump python3 vtysh; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "OK: $cmd -> $(command -v "$cmd")"
      "$cmd" --version 2>&1 | head -n 1 || true
    else
      echo "MISSING: $cmd"
    fi
  done
  echo
  echo "Linux MPLS kernel status:"
  lsmod | grep '^mpls' || true
  sysctl net.mpls.platform_labels || true
  echo
  echo "FRRouting daemon status:"
  for daemon in zebra ospfd ldpd; do
    if [[ -x "/usr/lib/frr/$daemon" ]]; then
      echo "OK: /usr/lib/frr/$daemon"
    else
      echo "MISSING: /usr/lib/frr/$daemon"
    fi
  done
  echo
  echo "Python package check:"
  python3 - <<'PY'
import importlib
for name in ["networkx", "matplotlib", "pandas", "docx"]:
    try:
        importlib.import_module(name)
        print(f"OK: {name}")
    except Exception as exc:
        print(f"MISSING: {name}: {exc}")
PY
} | tee -a "$LOG_FILE"

echo "Environment check saved to $LOG_FILE"
