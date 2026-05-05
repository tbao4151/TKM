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

apt update
apt install -y \
  mininet openvswitch-switch openvswitch-common iperf iperf3 traceroute \
  net-tools iproute2 python3 python3-pip python3-venv git curl \
  python3-networkx python3-matplotlib python3-pandas python3-docx

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
  for cmd in mn ovs-vsctl iperf iperf3 traceroute python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "OK: $cmd -> $(command -v "$cmd")"
      "$cmd" --version 2>&1 | head -n 1 || true
    else
      echo "MISSING: $cmd"
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
