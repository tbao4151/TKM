# Checklist doi chieu RUBRIC_TKM_2025-2026

## 1. Hinh thuc - 1.5 diem

- 1.1 Bo cuc bao cao: DAT. File Word `report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx` co trang bia, muc luc noi dung, ly thuyet, thiet ke, trien khai, ket qua va ket luan.
- 1.2 Hinh anh va so do: DAT. Co topology tong the, Branch 1 Flat, Branch 2 Three-tier, Branch 3 Leaf-Spine va MPLS backbone trong `images/`.
- 1.3 Muc luc va danh muc: DAT MOT PHAN. Bao cao co muc luc noi dung, nhung muc luc/danh muc hinh bang chua phai auto-update cua Word.
- 1.4 Trich dan va tai lieu: DAT. Bao cao co RFC 3031, Mininet, OVS, iperf3 va Metro Ethernet Forum.
- 1.5 Loi chinh ta: CAN DOC LAI LAN CUOI. Noi dung da viet theo phong cach ky thuat, nhung nen doc lai Word truoc khi nop.

## 2. Noi dung ly thuyet - 1.5 diem

- 2.1 Cach hanh van: DAT. Tai lieu giai thich CE/PE/P, Metro Ethernet, MPLS, push/swap/pop bang ngon ngu de thuyet trinh.
- 2.2 Tinh dung dan: DAT. Bao cao va huong dan trinh bay label switching, vai tro PE/P/CE va so sanh Flat, Three-tier, Leaf-Spine.
- Luu y: Rubric nhac OSPF/LDP/VPLS. Project hien tai dung static Linux kernel LSP de dam bao MPLS native va tcpdump that; chua cau hinh dynamic LDP/VPLS.

## 4. Demo va trien khai - 5.0 diem

- 4.1 Topology va kien truc: DAT. `code/topology_mininet.py` tao 3 chi nhanh dung kien truc Flat, Three-tier, Leaf-Spine va provider backbone CE/PE/P.
- 4.2 MPLS va VPLS core: DAT VE MPLS KERNEL, RUI RO VE LDP/VPLS. `code/network_config.py` cau hinh Linux kernel MPLS native bang `ip route encap mpls` va `ip -f mpls route`. Chua dung LDP/VPLS dong.
- 4.3 Xac minh chuyen nhan: DAT. `results/tcpdump_mpls.txt` co `ethertype MPLS unicast (0x8847)`, label 120/211 va hex dump shim header 4 byte.
- 4.4 Phan tich hieu nang: DAT. `results/results.csv` co Throughput, Delay, Packet loss, Jitter, UDP packet loss; bieu do nam trong `images/*chart.png`.
- 4.5 Minh chung ket qua: DAT. Raw logs nam trong `results/ping_results.txt`, `results/iperf_results.txt`, `results/traceroute_results.txt`, `results/mpls_routes.txt`, `results/tcpdump_mpls.txt`.
- 4.6 Trien khai nghien cuu: DAT. Co runner Python tu dong, parser ket qua, chart Matplotlib, GUI va report generator.

## 5. Kha nang bien luan - 2.0 diem

- 5.1 Tra loi cau hoi: DAT NEU NAM CAC LENH. Can nam: `ip route show`, `ip -f mpls route show`, `tcpdump -eni <intf> -XX 'ether proto 0x8847'`, `ping`, `iperf3`, `traceroute`.
- 5.2 Chinh sua cau hinh tai cho: DAT. Cac file can biet: `code/topology_mininet.py`, `code/network_config.py`, `code/performance_test.py`.

## Lenh demo khuyen dung

```bash
cd Metro_Ethernet_MPLS_Project
sudo python3 code/topology_mininet.py --mode mpls --test-mode --stp-wait 1
cat results/mpls_routes.txt
cat results/tcpdump_mpls.txt
cat results/results.csv
```

## Diem rui ro duy nhat

Rubric ghi muc toi da cho "OSPF loi hoi tu nhanh; LDP va VPLS cau hinh hoan hao". Project hien tai da co MPLS kernel native that, nhung dung static LSP thay cho LDP/VPLS dong. Neu thay bat buoc dung LDP/VPLS dung nghia, can cai va cau hinh FRRouting hoac bo cong cu tuong duong.
