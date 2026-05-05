# Metro Ethernet MPLS Project

Project mon hoc: **Thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep**.

## Muc tieu

- Mo phong 3 chi nhanh doanh nghiep tren Mininet.
- Ket noi cac chi nhanh qua provider backbone gom CE, PE va P router.
- Kiem thu that bang ping, iperf3, traceroute va tcpdump MPLS.
- Do UDP packet loss theo nhieu muc tai 5M, 20M, 50M, 80M, 120M.
- Tao `results/results.csv`, bieu do, bao cao Word, bao cao LaTeX va tai lieu van dap.

## Yeu cau he thong

- Ubuntu/Linux.
- Quyen sudo.
- Mininet, Open vSwitch, Linux kernel MPLS, iperf/iperf3, traceroute, tcpdump, Python 3.

## Cai moi truong

```bash
cd Metro_Ethernet_MPLS_Project
chmod +x code/install_environment.sh
sudo bash code/install_environment.sh
```

Nhap mat khau sudo khi he thong yeu cau. Project khong luu mat khau sudo trong source code, README, bao cao hay log.

## Chay tu dong

```bash
cd Metro_Ethernet_MPLS_Project
chmod +x code/run_all.sh
sudo bash code/run_all.sh
```

Script se cleanup Mininet, ve topology, chay test that, tao chart va tao bao cao Word.

## Chay thu cong

```bash
sudo mn -c
python3 draw_network_topology.py
python3 code/draw_topology.py
sudo python3 code/topology_mininet.py --mode mpls
```

`topology_mininet.py` hien tu goi `mn -c` luc khoi dong de giam rui ro demo fail do namespace cu, nhung van nen giu quen cleanup thu cong neu ban vua dung Mininet cho bai khac.

Trong Mininet CLI co the demo:

```text
nodes
links
host1 ping -c 3 10.2.0.21
host2 traceroute -n 10.3.0.11
exit
```

De chay do kiem tu dong:

```bash
sudo python3 code/performance_test.py --mode mpls
python3 code/plot_results.py
python3 code/generate_report.py
```

## Mo GUI

```bash
sudo -v
python3 code/gui_monitor.py
```

GUI goi dung loai test that theo cap host ban chon. Nen chay `sudo -v` truoc khi mo GUI de cac nut test co quyen tao Mininet namespace.
Neu may demo khong co desktop/display, bo qua GUI va dung `performance_test.py --action ...` de chay tung phep do trong terminal.

## Tao bao cao

Bao cao duoc tao tai:

```text
report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
../latex_report/main.tex
```

`generate_report.py` chi tao bao cao khi da co `results/results.csv` co du lieu.

Huong dan build ban LaTeX nam trong:

```text
../latex_report/README.md
docs/Huong_dan_chay_theo_rubric.md
```

## Cleanup Mininet

```bash
sudo mn -c
```

Nen cleanup sau moi lan demo CLI de tranh namespace/interface cu anh huong lan chay sau.

## Ghi chu ve MPLS

Project nay dung Linux kernel MPLS native trong mode `mpls`. Backbone PE/P chay FRRouting OSPF/LDP de tao route loopback va label dong; bang route co ca `proto ospf`, `proto ldp` va `encap mpls`. Luu luong LAN lien chi nhanh di qua CE WAN chung `172.16.100.0/24`, duoc bridge vao service VPLS/L2VPN tren cac PE. Data-plane L2VPN trong Mininet dung Linux GRETAP pseudowire full-mesh, bat port isolation tren cac pseudowire de tao split-horizon nhu VPLS va tranh loop L2; underlay cua pseudowire di qua backbone MPLS. Bang chung nam trong:

```text
results/mpls_routes.txt
results/frr_control_plane.txt
results/tcpdump_mpls.txt
```

Neu muon so sanh baseline IP routing, chay:

```bash
sudo python3 code/performance_test.py --mode ip
```

## Kiem tra ket qua that

**Du lieu trong results/results.csv duoc tao tu kiem thu thuc te bang ping/iperf/traceroute va UDP load sweep trong Mininet. Neu file nay chua ton tai, can chay performance_test.py hoac run_all.sh.**

Kiem tra log:

```bash
cat results/ping_results.txt
cat results/iperf_results.txt
cat results/traceroute_results.txt
cat results/mpls_routes.txt
cat results/frr_control_plane.txt
cat results/tcpdump_mpls.txt
cat results/command_history.txt
```

Cot `test_type=baseline` la bo phep do co ban; cot `test_type=udp_load_sweep` la packet loss/jitter do bang iperf3 UDP khi tang tai.

## Tai lieu nop va thuyet trinh

```text
docs/Huong_dan_chay_theo_rubric.md
docs/Kich_ban_thuyet_trinh.md
docs/rubric_TKM_2026_checklist.md
```

Kiem tra khong luu mat khau:

```bash
grep -R "mat_khau_can_kiem_tra" . || echo "OK: password not found in project files"
```
