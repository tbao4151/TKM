# Metro Ethernet MPLS Project

Project mon hoc: **Thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep**.

## Tai lieu demo

- `docs/Huong_dan_demo_thu_cong_Ubuntu.md`: tai lieu chinh de thuyet trinh va chay demo bang lenh Ubuntu/Mininet CLI.
- `docs/Huong_dan_su_dung_gui_monitor.md`: tai lieu rieng cho giao dien `code/gui_monitor.py`.

GUI khong thay the hoan toan demo thu cong. GUI giup chay nhanh ping/traceroute/throughput/delay/packet loss/jitter, nhung van nen dung terminal de chung minh topology, route MPLS, FRRouting OSPF/LDP va tcpdump MPLS theo rubric.

## Chay nhanh pipeline

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo bash code/run_all.sh
```

Pipeline se cai/kiem tra moi truong, cleanup Mininet, ve lai topology, chay benchmark MPLS that, tao chart va tao bao cao Word.

## Demo thu cong

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo bash code/install_environment.sh
sudo mn -c
python3 code/draw_topology.py
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 20
```

Trong Mininet CLI:

```text
nodes
links
net
host1 ping -c 5 10.2.0.21
host2 traceroute -n 10.3.0.11
pe1 ip -f mpls route show
pe1 vtysh -c "show mpls ldp neighbor"
p3 tcpdump -i p3-eth0 -e -n -c 5 mpls &
host1 ping -c 5 10.3.0.11
exit
```

Xem chi tiet tung buoc trong `docs/Huong_dan_demo_thu_cong_Ubuntu.md`.

## Mo GUI

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo -v
python3 code/gui_monitor.py
```

Xem chi tiet trong `docs/Huong_dan_su_dung_gui_monitor.md`.

## File ket qua duoc sinh lai khi demo

```text
results/results.csv
results/ping_results.txt
results/iperf_results.txt
results/traceroute_results.txt
results/mpls_routes.txt
results/frr_control_plane.txt
results/tcpdump_mpls.txt
images/throughput_chart.png
images/delay_chart.png
images/packet_loss_chart.png
images/jitter_chart.png
report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

Neu can cleanup cuoi buoi:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```
