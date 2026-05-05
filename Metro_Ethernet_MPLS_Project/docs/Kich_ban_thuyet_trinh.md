# Kich ban thuyet trinh Metro Ethernet MPLS

Thoi luong goi y: 7-10 phut thuyet trinh, 3-5 phut demo, sau do tra loi cau hoi.

## 1. Mo dau

Kinh thua thay, em xin trinh bay de tai: thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep.

Muc tieu cua bai la mo phong mot doanh nghiep co ba chi nhanh, moi chi nhanh dung mot kien truc LAN khac nhau, sau do ket noi qua ha tang provider backbone bang MPLS va do cac chi so throughput, delay, packet loss, jitter.

## 2. Y tuong topology

Mo hinh gom ba chi nhanh:

- Branch 1 la Flat Network, don gian, it tang thiet bi.
- Branch 2 la Three-tier Network, gom access, distribution va core.
- Branch 3 la Leaf-Spine Network, gan voi mo hinh data center.

Ba chi nhanh ket noi vao provider thong qua CE router. Provider co PE router o bien va P router trong loi. Luu luong lien chi nhanh bat buoc di qua CE -> PE -> P -> PE -> CE.

Mo hinh nay dap ung dung yeu cau de bai ve Metro Ethernet MAN, MPLS backbone, CE/PE/P router, switch va host tren Mininet.

## 3. Giai thich MPLS

MPLS la co che chuyen tiep dua tren label. Khi goi tin vao provider:

- PE dau vao push label.
- P router trong loi swap label.
- PE dau ra pop label va dua goi ve CE dich.

Trong project nay, em dung Linux kernel MPLS native. Bang chung nam trong `results/mpls_routes.txt` va `results/tcpdump_mpls.txt`.

Diem quan trong la tcpdump bat duoc `ethertype MPLS unicast (0x8847)` va label dong do LDP cap phat. Vi vay day khong phai so lieu hay MPLS mo phong bang ly thuyet, ma la goi MPLS that trong Mininet/Linux namespace.

## 4. Giai thich ve OSPF/LDP va VPLS

Rubric co nhac OSPF/LDP/VPLS. Project hien tai dung Linux kernel MPLS native cho backbone, FRRouting trong namespace PE/P de chay OSPF/LDP control-plane, va service VPLS/L2VPN de noi cac CE. Bang chung nam trong `results/frr_control_plane.txt`.

Neu thay hoi: "Co phai LDP/VPLS dong khong?"

Tra loi:

Project cua em co MPLS native that va co FRRouting OSPF/LDP tren backbone PE/P. Trong log co OSPF `Full/-`, LDP `OPERATIONAL`, route `proto ospf`, label route `proto ldp`, va VPLS running-config tren PE. CE lien chi nhanh di qua subnet WAN chung trong service VPLS/L2VPN; data-plane L2VPN trong Mininet dung full-mesh Linux GRETAP pseudowire co split-horizon/port-isolation tren underlay MPLS de co forward that va kiem chung duoc.

## 5. Do hieu nang

Project do bon nhom chi so:

- Throughput bang iperf3 TCP.
- Delay bang ping RTT trung binh.
- Jitter bang iperf3 UDP.
- Packet loss khi tai tang bang iperf3 UDP load sweep.

Em co chay baseline cho cac cap lien chi nhanh va noi bo chi nhanh. Ngoai ra em chay UDP load sweep o 5M, 20M, 50M, 80M va 120M. Khi tai tang vuot kha nang link backbone 50-60 Mbps, packet loss bat dau tang ro o muc 80M va 120M.

## 6. Phan tich ket qua

Ket qua noi bo cung chi nhanh co throughput cao hon va delay thap hon vi khong phai di qua provider backbone.

Branch 1 co duong noi bo ngan nen delay thap. Branch 2 co them tang access/distribution/core nen delay noi bo cao hon Branch 1. Branch 3 co leaf-spine, phu hop mo hinh server/data center, nhung trong lab loop-free nay hieu nang lien chi nhanh van bi chi phoi chu yeu boi backbone MPLS.

Khi so sanh lien chi nhanh, Branch1 -> Branch3 co delay cao hon do duong di qua nhieu hop core hon. Packet loss tang khi offered load cao hon kha nang link loi.

## 7. Demo de xuat

Buoc 1: kiem tra moi truong.

```bash
cd Metro_Ethernet_MPLS_Project
cat results/environment_check.txt
```

Noi nhanh: day la thong tin Ubuntu, Mininet, OVS, iperf3 va module MPLS kernel.

Buoc 2: kiem tra MPLS route.

```bash
cat results/mpls_routes.txt
```

Chi vao:

- `encap mpls`: route underlay duoc day vao MPLS backbone.
- `proto ldp`: label do LDP sinh ra.
- `as to`: router loi swap label.

Buoc 3: kiem tra tcpdump MPLS.

```bash
cat results/tcpdump_mpls.txt
```

Chi vao:

- `ethertype MPLS unicast (0x8847)`.
- `MPLS (label ...)`.
- Payload ICMP tu 10.1.0.11 sang 10.2.0.21.

Buoc 4: xem ket qua do.

```bash
cat results/results.csv
```

Noi nhanh ve `baseline` va `udp_load_sweep`.

Buoc 5: demo GUI.

```bash
sudo -v
python3 code/gui_monitor.py
```

Trong GUI:

- Chon `host1` -> `user1`.
- Bam `Ping`.
- Bam `Throughput`.
- Bam `Packet Loss`.
- Mo chart bang `Open Charts`.

Buoc 6: neu can chay lai toan bo.

```bash
sudo bash code/run_all.sh
```

## 8. Cau hoi dap nhanh

Hoi: Project co dung du lieu gia khong?

Tra loi: Khong. Toan bo so lieu duoc tao tu ping, traceroute, iperf3 va tcpdump trong Mininet. Log raw nam trong thu muc `results/`.

Hoi: MPLS duoc chung minh bang gi?

Tra loi: Bang route `ip route encap mpls`, `ip -f mpls route` va tcpdump bat ethertype `0x8847` voi MPLS label.

Hoi: Tai sao traceroute co dau `*`?

Tra loi: Trong mien MPLS, mot so hop loi khong tra ICMP TTL exceeded nhu router IP thong thuong. Vi vay traceroute khong hien het moi P router, nen em chung minh them bang `mpls_routes.txt` va `tcpdump_mpls.txt`.

Hoi: Tai sao packet loss tang o 80M va 120M?

Tra loi: Vi offered load UDP bat dau vuot kha nang link backbone 50-60 Mbps. UDP khong co co che congestion control nhu TCP nen khi qua tai se mat goi ro hon.

Hoi: P router co route den LAN khach hang khong?

Tra loi: Trong mode MPLS, P router chi co route connected cho link backbone va bang MPLS label. P router khong can route IP den 10.1/10.2/10.3, dung vai tro loi provider.

Hoi: Neu thay yeu cau LDP/VPLS thi sao?

Tra loi: Ban hien tai la MPLS kernel native co FRRouting OSPF/LDP trong backbone va co service VPLS/L2VPN cho traffic CE/branch. Em chung minh bang `frr_control_plane.txt`: OSPF `Full/-`, LDP `OPERATIONAL`, `show mpls table`, VPLS running-config, bridge member va GRETAP pseudowire. Diem can noi ro la data-plane VPLS trong Mininet duoc hien thuc bang full-mesh Linux GRETAP pseudowire co split-horizon/port-isolation tren underlay MPLS.

## 9. Ket luan

Project da dung duoc topology Metro Ethernet MPLS tren Mininet, co ba kien truc LAN khac nhau, co CE/PE/P backbone, co MPLS label switching that, co benchmark hieu nang va co GUI demo. Diem manh cua bai la minh chung bang log raw va kha nang chay lai bang mot lenh.
