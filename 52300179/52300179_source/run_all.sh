#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$PROJECT_DIR/results"
mkdir -p "$RESULTS_DIR"
COMMAND_LOG="$RESULTS_DIR/command_history.txt"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run: sudo bash code/run_all.sh"
  exit 1
fi

cd "$PROJECT_DIR"
echo "run_all started: $(date -Iseconds)" > "$COMMAND_LOG"

log_cmd() {
  echo "$(date -Iseconds) | $*" >> "$COMMAND_LOG"
  "$@"
}

log_cmd bash code/install_environment.sh
log_cmd mn -c
log_cmd python3 code/draw_topology.py
log_cmd python3 code/performance_test.py --mode mpls
log_cmd python3 code/plot_results.py
log_cmd python3 code/generate_report.py

required_files=(
  "results/results.csv"
  "results/ping_results.txt"
  "results/iperf_results.txt"
  "results/traceroute_results.txt"
  "results/mpls_routes.txt"
  "results/frr_control_plane.txt"
  "results/tcpdump_mpls.txt"
  "images/topology_overview.png"
  "output/so_do_tong_hop.png"
  "output/so_do_tong_hop.svg"
  "output/so_do_tong_hop.pdf"
  "output/chi_nhanh_1.png"
  "output/chi_nhanh_2.png"
  "output/chi_nhanh_3.png"
  "images/branch1_flat.png"
  "images/branch2_three_tier.png"
  "images/branch3_leaf_spine.png"
  "images/mpls_backbone.png"
  "images/throughput_chart.png"
  "images/delay_chart.png"
  "images/packet_loss_chart.png"
  "images/jitter_chart.png"
  "report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx"
  "docs/Huong_dan_chay_va_thuyet_trinh.md"
  "README.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -s "$file" ]]; then
    echo "Missing or empty required output: $file" | tee -a "$COMMAND_LOG"
    exit 1
  fi
done

echo "run_all finished: $(date -Iseconds)" >> "$COMMAND_LOG"
echo "OK: pipeline completed with real Mininet measurements."
