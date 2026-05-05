# Huong dan chay theo tung yeu cau rubric

Tai lieu nay dung de demo va kiem tra tung yeu cau cua de tai Metro Ethernet MPLS. Tat ca lenh ben duoi chay trong thu muc project:

```bash
cd Metro_Ethernet_MPLS_Project
```

## 0. Kiem tra moi truong

Muc tieu: chung minh may co Mininet, OVS, iperf3, tcpdump va Linux kernel MPLS.

```bash
sudo bash code/install_environment.sh
cat results/environment_check.txt
```

Can thay:

- `OK: mn`
- `OK: ovs-vsctl`
- `OK: iperf3`
- `mpls_router`
- `mpls_iptunnel`
- `net.mpls.platform_labels = 100000`

## 1. Chay toan bo pipeline

Muc tieu: mot lenh tao lai topology, ket qua do, bieu do va bao cao.

```bash
sudo bash code/run_all.sh
```

Can thay cuoi output:

```text
OK: pipeline completed with real Mininet measurements.
```

File can co:

```bash
ls -lh results/results.csv images/*chart.png report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

## 2. Kiem tra topology Mininet

Muc tieu: chung minh co 3 chi nhanh, CE/PE/P router va backbone provider.

```bash
sudo mn -c
sudo python3 code/topology_mininet.py --mode mpls --test-mode --stp-wait 20
```

Can thay cac precheck ping thanh cong va in bang MPLS route.
`topology_mininet.py` hien tu goi them `mn -c` o dau lan chay de giam rui ro fail do namespace cu, nhung van nen giu buoc cleanup thu cong de dung luc demo.

Neu muon vao CLI de demo thu cong:

```bash
sudo python3 code/topology_mininet.py --mode mpls
```

Trong Mininet CLI:

```text
nodes
links
host1 ping -c 3 10.2.0.21
host2 traceroute -n 10.3.0.11
exit
```

Sau khi thoat CLI:

```bash
sudo mn -c
```

## 3. Kiem tra MPLS label switching

Muc tieu: chung minh co push, swap, pop label that bang Linux kernel MPLS.

```bash
cat results/mpls_routes.txt
cat results/tcpdump_mpls.txt
```

Can chi ra trong `mpls_routes.txt`:

```text
encap mpls
proto ldp
as to
```

Can chi ra trong `tcpdump_mpls.txt`:

```text
ethertype MPLS unicast (0x8847)
MPLS (label ...)
```

Giai thich khi demo:

- `encap mpls`: ingress PE push label.
- `as to`: P router swap label.
- `via inet`: egress PE pop label va dua goi ve CE.

## 4. Kiem tra connectivity lien chi nhanh

Muc tieu: chung minh cac chi nhanh thong nhau qua backbone.

```bash
cat results/ping_results.txt
cat results/traceroute_results.txt
```

Lenh demo nhanh trong CLI:

```text
host1 ping -c 5 10.2.0.21
host2 ping -c 5 10.3.0.11
user1 ping -c 5 10.3.0.12
```

## 5. Do throughput

Muc tieu: throughput do bang iperf3 TCP that, khong phai so lieu mau.

```bash
cat results/iperf_results.txt
cat results/results.csv
```

Lenh chay rieng mot cap:

```bash
sudo python3 code/performance_test.py --action throughput --source-host host1 --destination-host user1 --mode mpls
```

Can thay JSON iperf3 va dong:

```text
SUMMARY: throughput_mbps=...
```

## 6. Do delay va packet loss baseline

Muc tieu: delay va ping packet loss lay tu ping that.

```bash
sudo python3 code/performance_test.py --action delay --source-host host1 --destination-host user1 --mode mpls
cat results/ping_results.txt
```

Can thay:

```text
8 packets transmitted, 8 received
rtt min/avg/max/mdev = ...
```

## 7. Do jitter

Muc tieu: jitter lay tu iperf3 UDP that.

```bash
sudo python3 code/performance_test.py --action jitter --source-host host1 --destination-host user1 --mode mpls
```

Can thay JSON iperf3 UDP va:

```text
SUMMARY: jitter_ms=...
```

## 8. Packet loss khi tai mang tang

Muc tieu: dap ung yeu cau packet loss khi tai tang bang UDP load sweep.

```bash
sudo python3 code/performance_test.py --action packet-loss --source-host host1 --destination-host user1 --mode mpls
```

Hoac xem ket qua da chay:

```bash
awk -F, '$3=="udp_load_sweep"{print}' results/results.csv
```

Can thay cac muc tai:

```text
5M, 20M, 50M, 80M, 120M
```

Can giai thich: khi offered load vuot link backbone 50-60 Mbps, UDP packet loss tang ro o muc 80M va 120M.

## 9. Ve bieu do

Muc tieu: bieu do sinh tu `results/results.csv`.

```bash
python3 code/plot_results.py
ls -lh images/throughput_chart.png images/delay_chart.png images/packet_loss_chart.png images/jitter_chart.png
```

Noi dung bieu do:

- `throughput_chart.png`: iperf3 TCP.
- `delay_chart.png`: ping RTT trung binh.
- `packet_loss_chart.png`: UDP loss khi tai tang.
- `jitter_chart.png`: iperf3 UDP jitter.

## 10. Tao bao cao Word

Muc tieu: bao cao Word duoc tao tu ket qua that.

```bash
python3 code/generate_report.py
ls -lh report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

## 11. Tao bao cao LaTeX

Muc tieu: dung mau LaTeX de tao bao cao nop.

Neu may chua co `pdflatex`, cai bo goi LaTeX truoc:

```bash
sudo apt update
sudo apt install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-lang-other texlive-fonts-recommended
```

```bash
cd ../latex_report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

File dau ra:

```text
main.pdf
```

## 12. Chay GUI demo

Nen chay truoc de sudo khong hoi mat khau trong GUI:

```bash
sudo -v
python3 code/gui_monitor.py
```

Trong GUI:

- Chon source `host1`, destination `user1`.
- Bam `Ping`, `Throughput`, `Packet Loss` hoac `Jitter`.
- Bam `Run Full Benchmark` neu muon chay lai toan bo.
- Bam `Open Charts` de mo thu muc bieu do.

Neu may demo khong co desktop/display, bo qua GUI va chay tung phep do bang `performance_test.py --action ...`.

## 13. Kiem tra khong co du lieu gia

```bash
rg -n "fake|mock|random|placeholder|sample data" .
```

Chap nhan neu khong co ket qua, hoac chi xuat hien trong tai lieu noi rang khong dung du lieu gia.

## 14. Diem can noi ro khi bi hoi ve LDP/VPLS

Project nay chay MPLS kernel native va co FRRouting OSPF/LDP trong namespace PE/P. Co goi MPLS that, co label push/swap/pop that, co tcpdump ethertype 0x8847, va co `results/frr_control_plane.txt` chung minh OSPF `Full/-`, LDP `OPERATIONAL`, label binding, `show mpls table`.

Neu thay hoi ve VPLS:

```text
CE cua ba chi nhanh nam tren subnet WAN chung 172.16.100.0/24 va route den LAN tu xa qua CE remote. PE access interface bi flush IP va dua vao bridge VPLS/L2VPN. Data-plane L2VPN trong Mininet dung Linux GRETAP pseudowire full-mesh; cac pseudowire port bat isolation de tao split-horizon nhu VPLS va tranh loop L2. Underlay cua pseudowire la route PE-loopback do OSPF/LDP/MPLS sinh ra. FRR running-config van co block l2vpn type vpls de bam rubric.
```

Khi tra loi, noi chinh xac: `MPLS native + FRRouting OSPF/LDP control-plane; CE lien chi nhanh di qua service VPLS/L2VPN; data-plane L2VPN trong Mininet dung full-mesh GRETAP pseudowire co split-horizon/port-isolation tren underlay MPLS`.
