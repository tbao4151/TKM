# Huong dan demo thu cong tren Ubuntu

Tai lieu nay chi dung cho luc thuyet trinh/demo truc tiep. Tat ca lenh ben duoi chay tren Ubuntu, trong thu muc `Metro_Ethernet_MPLS_Project`, va tao lai ket qua moi tu Mininet thay vi dung log san co.

## 1. Muc tieu can chung minh theo de va rubric

Khi demo, can lan luot chung minh cac y sau:

1. Co 3 chi nhanh doanh nghiep voi 3 kien truc LAN khac nhau:
   - Branch 1: Flat Network.
   - Branch 2: Core - Distribution - Access.
   - Branch 3: Leaf - Spine.
2. Co provider Metro Ethernet/MPLS backbone gom CE, PE va P router.
3. Topology chay tren Mininet, router la Linux node, switch la Open vSwitch.
4. Ket noi lien chi nhanh hoat dong qua backbone.
5. MPLS label switching co bang chung that:
   - kernel MPLS route/label table tren PE/P.
   - FRRouting OSPF/LDP hoi tu.
   - tcpdump bat duoc goi MPLS tren core link.
6. Co so lieu hieu nang that:
   - Throughput.
   - Delay.
   - Packet loss.
   - Jitter.
7. Co bang CSV, bieu do va bao cao Word sinh tu ket qua do moi.

## 2. Chuan bi terminal

Mo terminal va vao dung thu muc project:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
pwd
ls
```

Ket qua mong doi: terminal dang o `.../Metro_Ethernet_MPLS_Project` va thay cac thu muc `code`, `docs`, `images`, `output`, `results`, `report`.

Lam sach trang thai Mininet cu:

```bash
sudo mn -c
```

Neu vua demo loi hoac vua dung Mininet cho bai khac, chay them:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```
## 3. Kiem tra moi truong truoc demo

Chay script cai dat/kiem tra moi truong:

```bash
sudo bash code/install_environment.sh
```

Script nay kiem tra/cai cac thanh phan can cho demo:

```bash
mn --version
ovs-vsctl --version
iperf3 --version
traceroute --version
tcpdump --version
python3 --version
vtysh --version
```

Kiem tra kernel MPLS:

```bash
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
sudo modprobe mpls_gso || true
lsmod | grep '^mpls'
sysctl net.mpls.platform_labels
```

Ket qua mong doi:

- Co module `mpls_router` va `mpls_iptunnel`.
- `net.mpls.platform_labels` lon hon 0.
- File `results/environment_check.txt` duoc tao moi.

## 4. Ve lai so do topology tu source

Lenh nay tao lai so do tong hop va tung vung mang:

```bash
python3 code/draw_topology.py
ls -lh output
ls -lh images/topology_overview.png images/branch1_flat.png images/branch2_three_tier.png images/branch3_leaf_spine.png images/mpls_backbone.png
```

Dung de noi khi thuyet trinh:

- `output/so_do_tong_hop.png`: so do tong the.
- `output/chi_nhanh_1.png`: Flat Network.
- `output/chi_nhanh_2.png`: Three-tier Network.
- `output/chi_nhanh_3.png`: Leaf-Spine Network.
- `output/mpls_backbone.png`: PE/P provider backbone.

## 5. Khoi dong topology Mininet de demo thu cong

Mo topology o che do MPLS:

```bash
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 20
```

Sau khi thay dong `mininet>`, demo cac lenh sau trong Mininet CLI.

### 5.1. Chung minh cac node dung yeu cau

Trong Mininet CLI:

```text
nodes
links
net
```

Diem can chi tren man hinh:

- Host Branch 1: `host1`, `host2`, `host3`, `host4`.
- Host Branch 2: `admin1`, `admin2`, `user1`, `user2`, `guest1`, `guest2`.
- Host Branch 3: `svr1`, `svr2`, `svr3a`, `svr3b`, `svr4`, `os1`, `os2`.
- CE: `b1_ce`, `b2_ce`, `b3_ce`.
- PE: `pe1`, `pe2`, `pe3`.
- P router: `p1`, `p2`, `p3`, `p4`.

### 5.2. Chung minh IP va gateway noi bo

Trong Mininet CLI:

```text
host1 ip addr show host1-eth0
host1 ip route
admin1 ip addr show admin1-eth0
admin1 ip route
svr1 ip addr show svr1-eth0
svr1 ip route
b1_ce ip addr
b2_ce ip addr
b3_ce ip addr
```

Diem can noi:

- Branch 1 dung mang `10.1.0.0/24`, gateway `10.1.0.1`.
- Branch 2 dung mang `10.2.0.0/24`, gateway `10.2.0.1`.
- Branch 3 dung mang `10.3.0.0/24`, gateway `10.3.0.1`.

### 5.3. Kiem tra ket noi noi bo va lien chi nhanh

Trong Mininet CLI:

```text
host1 ping -c 3 10.1.0.1
admin1 ping -c 3 10.2.0.1
svr1 ping -c 3 10.3.0.1
host1 ping -c 5 10.2.0.21
host2 ping -c 5 10.3.0.11
user1 ping -c 5 10.3.0.12
admin1 ping -c 5 10.1.0.11
```

Ket qua mong doi: cac lenh lien chi nhanh co `0% packet loss` hoac ty le mat goi chap nhan duoc neu may demo dang tai nang.

### 5.4. Chung minh duong di qua CE/PE/P

Trong Mininet CLI:

```text
host1 traceroute -n 10.2.0.21
host2 traceroute -n 10.3.0.11
user1 traceroute -n 10.3.0.12
```

Diem can noi:

- Goi tin tu host di len CE cua chi nhanh.
- Sau do vao PE cua nha cung cap.
- Backbone PE/P chuyen tiep giua cac chi nhanh.
- Cuoi cung ve CE va host dich.

### 5.5. Chung minh MPLS route/label tren PE va P router

Trong Mininet CLI:

```text
pe1 ip -f mpls route show
pe2 ip -f mpls route show
pe3 ip -f mpls route show
p1 ip -f mpls route show
p3 ip -f mpls route show
pe1 ip route show
p3 ip route show
```

Neu can xem control-plane FRRouting:

```text
pe1 vtysh -c "show ip ospf neighbor"
pe1 vtysh -c "show mpls ldp neighbor"
pe2 vtysh -c "show mpls ldp binding"
p3 vtysh -c "show mpls ldp binding"
```

Ket qua mong doi:

- OSPF neighbor co trang thai `Full`.
- LDP neighbor co trang thai `OPERATIONAL`.
- Bang route co dong MPLS/label, vi du `encap mpls`, `proto ldp`, hoac route trong family `mpls`.

### 5.6. Bat goi MPLS that bang tcpdump

Trong Mininet CLI, bat tcpdump tren core link va tao traffic:

```text
p3 tcpdump -i p3-eth0 -e -n -c 5 mpls &
host1 ping -c 5 10.3.0.11
```

Neu chua thay goi ngay, lap lai:

```text
p3 tcpdump -i p3-eth0 -e -n -c 10 mpls &
user1 ping -c 8 10.3.0.12
```

Ket qua mong doi: tcpdump in ra goi co chu `MPLS` hoac ethertype MPLS tren link core. Day la phan bang chung quan trong nhat cho yeu cau MPLS label switching.

### 5.7. Thoat CLI va cleanup

Trong Mininet CLI:

```text
exit
```

Sau khi ve terminal Ubuntu:

```bash
sudo mn -c
```

## 6. Chay tung phep do hieu nang bang lenh Ubuntu

Cac lenh sau chay ngoai Mininet CLI. Moi lenh se tu khoi dong topology, chay phep do that, ghi log, roi dung topology.

Ping/delay:

```bash
sudo python3 code/performance_test.py --mode mpls --action ping --source-host host1 --destination-host user1
sudo python3 code/performance_test.py --mode mpls --action delay --source-host host2 --destination-host svr1
```

Traceroute:

```bash
sudo python3 code/performance_test.py --mode mpls --action traceroute --source-host host1 --destination-host svr1
```

Throughput TCP bang iperf3:

```bash
sudo python3 code/performance_test.py --mode mpls --action throughput --source-host host1 --destination-host user1
```

Jitter UDP bang iperf3:

```bash
sudo python3 code/performance_test.py --mode mpls --action jitter --source-host user1 --destination-host svr2
```

Packet loss khi tang tai UDP:

```bash
sudo python3 code/performance_test.py --mode mpls --action packet-loss --source-host host2 --destination-host svr1
```

Ghi chu khi thuyet trinh:

- `ping` sinh delay va packet loss co ban.
- `iperf3 TCP` sinh throughput.
- `iperf3 UDP` sinh jitter.
- `packet-loss` sweep cac muc 5M, 20M, 50M, 80M, 120M de thay mat goi khi tai tang.

## 7. Chay full benchmark de tao bang, chart va report

Day la lenh nen chay trong demo chinh neu du thoi gian:

```bash
sudo python3 code/performance_test.py --mode mpls --stp-wait 20
python3 code/plot_results.py
python3 code/generate_report.py
```

Hoac chay pipeline mot lenh:

```bash
sudo bash code/run_all.sh
```

Sau khi chay xong, kiem tra file ket qua:

```bash
ls -lh results
ls -lh images/*_chart.png
ls -lh report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

Mo nhanh CSV:

```bash
column -s, -t < results/results.csv | less -S
```

Xem log raw:

```bash
less results/ping_results.txt
less results/iperf_results.txt
less results/traceroute_results.txt
less results/mpls_routes.txt
less results/frr_control_plane.txt
less results/tcpdump_mpls.txt
```

## 8. Kich ban noi ngan khi demo

1. "Day la mo hinh Metro Ethernet ket noi 3 chi nhanh qua provider backbone."
2. "Ba chi nhanh dung ba kien truc LAN khac nhau: Flat, Three-tier, Leaf-Spine."
3. "Provider co CE, PE va P router; CE thuoc phia khach hang, PE/P thuoc phia nha cung cap."
4. "Em khoi dong topology tren Mininet va kiem tra node/link bang `nodes`, `links`, `net`."
5. "Em ping lien chi nhanh de chung minh ket noi thong suot."
6. "Em traceroute de chung minh traffic di qua CE/PE/P."
7. "Em xem route MPLS va FRRouting LDP/OSPF de chung minh control-plane."
8. "Em bat tcpdump tren core link de chung minh co goi MPLS that."
9. "Em chay benchmark bang ping/iperf3/traceroute de tao throughput, delay, packet loss, jitter."
10. "Cuoi cung em tao chart va report Word tu ket qua moi."

## 9. Xu ly loi nhanh khi demo

Neu Mininet khong start:

```bash
sudo mn -c
sudo systemctl restart openvswitch-switch
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 25
```

Neu thieu MPLS module:

```bash
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
sudo sysctl -w net.mpls.platform_labels=100000
```

Neu thieu FRRouting:

```bash
sudo apt update
sudo apt install -y frr
sudo bash code/install_environment.sh
```

Neu GUI/benchmark bao loi sudo:

```bash
sudo -v
sudo python3 code/performance_test.py --mode mpls --action ping --source-host host1 --destination-host user1
```

Neu chart/report khong tao duoc:

```bash
ls -lh results/results.csv
python3 code/plot_results.py
python3 code/generate_report.py
```

## 10. Cleanup cuoi buoi

Sau khi demo xong:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```
