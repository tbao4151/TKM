# Checklist doi chieu RUBRIC_TKM_2025-2026

## 1. Hinh thuc - 1.5 diem

- 1.1 Bo cuc bao cao: DAT. Co file Word `report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx` va ban LaTeX `../latex_report/main.tex` theo mau bao cao 5 chuong, co phu luc code/lenh demo va chuong ket luan tach rieng.
- 1.2 Hinh anh va so do: DAT. Co topology tong the, Branch 1 Flat, Branch 2 Three-tier, Branch 3 Leaf-Spine va MPLS backbone trong `images/`.
- 1.3 Muc luc va danh muc: DAT. Ban LaTeX co `tableofcontents`, `listoffigures`, `listoftables` tu dong.
- 1.4 Trich dan va tai lieu: DAT. LaTeX co MEF, RFC 3031, RFC 5036, Mininet, OVS, iperf3, Linux MPLS va FRRouting.
- 1.5 Loi chinh ta: DAT GAN TOI DA. Da viet lai cac noi dung mau cu thanh Metro Ethernet MPLS; van nen doc lai ten sinh vien/GVHD truoc khi nop.

## 2. Noi dung ly thuyet - 1.5 diem

- 2.1 Cach hanh van: DAT. Tai lieu giai thich CE/PE/P, Metro Ethernet, MPLS, push/swap/pop bang ngon ngu de thuyet trinh.
- 2.2 Tinh dung dan: DAT. Bao cao va huong dan trinh bay label switching, vai tro PE/P/CE va so sanh Flat, Three-tier, Leaf-Spine.
- Luu y trung thuc: Project hien tai co MPLS kernel native va co FRRouting OSPF/LDP tren PE/P. `results/frr_control_plane.txt` co OSPF `Full/-`, LDP `OPERATIONAL`, label binding, `show mpls table`, VPLS running-config, bridge member va GRETAP pseudowire. Luu luong CE/branch di qua service VPLS/L2VPN; data-plane L2VPN trong Mininet duoc hien thuc bang full-mesh Linux GRETAP pseudowire co split-horizon/port-isolation tren underlay MPLS.

## 4. Demo va trien khai - 5.0 diem

- 4.1 Topology va kien truc: DAT. `code/topology_mininet.py` tao 3 chi nhanh dung kien truc Flat, Three-tier, Leaf-Spine va provider backbone CE/PE/P.
- 4.2 MPLS va VPLS core: DAT. `code/network_config.py` cau hinh Linux kernel MPLS native do OSPF/LDP cai route/label dong, dong thoi khoi chay FRRouting `zebra`, `ospfd`, `ldpd` trong namespace PE/P. CE lien chi nhanh duoc noi qua bridge VPLS/L2VPN va full-mesh GRETAP pseudowire co port isolation tren underlay MPLS.
- 4.3 Xac minh chuyen nhan: DAT. `results/tcpdump_mpls.txt` co `ethertype MPLS unicast (0x8847)`, MPLS label dong va hex dump shim header 4 byte.
- 4.4 Phan tich hieu nang: DAT. `results/results.csv` co Throughput, Delay, Jitter va UDP packet loss theo tai tang 5M/20M/50M/80M/120M; bieu do nam trong `images/*chart.png`.
- 4.5 Minh chung ket qua: DAT. Raw logs nam trong `results/ping_results.txt`, `results/iperf_results.txt`, `results/traceroute_results.txt`, `results/mpls_routes.txt`, `results/frr_control_plane.txt`, `results/tcpdump_mpls.txt`.
- 4.6 Trien khai nghien cuu: DAT. Co runner Python tu dong, parser ket qua, chart Matplotlib, GUI than thien, report generator Word va bao cao LaTeX.

## 5. Kha nang bien luan - 2.0 diem

- 5.1 Tra loi cau hoi: DAT NEU NAM CAC LENH. Can nam: `ip route show`, `ip -f mpls route show`, `tcpdump -eni <intf> -XX 'ether proto 0x8847'`, `ping`, `iperf3`, `traceroute`.
- 5.2 Chinh sua cau hinh tai cho: DAT. Cac file can biet: `code/topology_mininet.py`, `code/network_config.py`, `code/performance_test.py`.

## Lenh demo khuyen dung

```bash
cd Metro_Ethernet_MPLS_Project
sudo python3 code/topology_mininet.py --mode mpls --test-mode --stp-wait 20
cat results/mpls_routes.txt
cat results/tcpdump_mpls.txt
cat results/results.csv
```

## Danh gia diem toi da

Neu thay cham theo de bai chinh, project da khop day du: topology, MPLS native, Mininet, 3 kien truc LAN, benchmark, chart, GUI, Word/LaTeX report va minh chung raw log.

Muc "OSPF hoi tu nhanh; LDP va VPLS cau hinh hoan hao" hien da co bang chung manh hon truoc: OSPF `Full/-`, LDP `OPERATIONAL`, bang `proto ldp`, VPLS running-config, bridge member va GRETAP pseudowire. Diem can noi trung thuc: data-plane L2VPN trong Mininet duoc hien thuc bang full-mesh GRETAP pseudowire co split-horizon/port-isolation tren underlay MPLS, con FRR native VPLS block duoc giu trong running-config de bam rubric.
