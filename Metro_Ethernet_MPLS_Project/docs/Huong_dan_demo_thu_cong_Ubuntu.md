# Hướng dẫn demo thủ công trên Ubuntu

Tài liệu này là runbook demo thủ công cho đồ án `Metro_Ethernet_MPLS_Project`. Mục tiêu là demo đúng thứ tự, đúng lệnh, đúng bằng chứng, và bám sát yêu cầu của đề: topology Mininet, 3 LAN khác nhau, kết nối nội bộ và liên chi nhánh, OSPF, LDP, Linux kernel MPLS, `tcpdump` MPLS, benchmark thật, chart và báo cáo Word.

Tài liệu này đã được đối chiếu với lần chạy lại pipeline trên máy này ngày `2026-05-07`.

## 1. Những gì cần chứng minh khi demo

Cần lần lượt chỉ ra các ý sau:

1. Branch 1 là `Flat Network`.
2. Branch 2 là `Core - Distribution - Access`.
3. Branch 3 là `Leaf - Spine`.
4. Có provider backbone gồm `CE`, `PE`, `P`.
5. Topology chạy thật trên `Mininet`, switch là `OVS`, router là `Linux node`.
6. Ping nội bộ mỗi chi nhánh thành công.
7. Ping liên chi nhánh thành công.
8. `traceroute` liên chi nhánh chạy được.
9. `OSPF` hội tụ.
10. `LDP` hội tụ.
11. Linux kernel MPLS có bằng `ip route encap mpls` và `ip -f mpls route show`.
12. `tcpdump` bắt được gói có `ethertype MPLS (0x8847)`.
13. Có log `results/*.txt`, `results/results.csv`, chart trong `images/`, và report Word trong `report/`.

## 2. Chuẩn bị terminal

Mở terminal và vào đúng thư mục project:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
pwd
ls
```

Lấy quyền sudo trước:

```bash
sudo -v
```

Làm sạch Mininet cũ:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```

Nếu vừa demo lỗi, chạy lại thêm lần nữa:

```bash
sudo mn -c
```

## 3. Kiểm tra môi trường trước demo

Chạy script kiểm tra/cài đặt:

```bash
sudo bash code/install_environment.sh
```

Kiểm tra nhanh lại bằng tay:

```bash
mn --version
ovs-vsctl --version
iperf3 --version
traceroute --version
tcpdump --version
python3 --version
vtysh -c "show version" || true
```

Kiểm tra kernel MPLS:

```bash
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
sudo modprobe mpls_gso || true
lsmod | grep '^mpls'
sysctl net.mpls.platform_labels
```

Kiểm tra file log môi trường:

```bash
ls -lh results/environment_check.txt
tail -n 20 results/environment_check.txt
```

Kết quả mong đợi:

- Có `mpls_router` và `mpls_iptunnel`.
- `net.mpls.platform_labels = 100000` hoặc ít nhất lớn hơn `0`.
- `results/environment_check.txt` được tạo và không rỗng.

## 4. Vẽ lại sơ đồ topology

Tạo lại hình vẽ từ source:

```bash
python3 code/draw_topology.py
ls -lh output
ls -lh images/topology_overview.png images/branch1_flat.png images/branch2_three_tier.png images/branch3_leaf_spine.png images/mpls_backbone.png
```

Dùng để chỉ trên màn hình:

- `output/so_do_tong_hop.png`: toàn bộ hệ thống.
- `output/chi_nhanh_1.png`: Branch 1.
- `output/chi_nhanh_2.png`: Branch 2.
- `output/chi_nhanh_3.png`: Branch 3.
- `images/mpls_backbone.png`: backbone CE/PE/P.

## 5. Khởi động topology để demo thủ công

Khởi động Mininet ở mode MPLS:

```bash
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 20
```

Sau khi thấy dấu nhắc `mininet>`, thực hiện đúng thứ tự các mục 6 đến 14.

Lưu ý:

- Khi topology khởi động có thể thấy nhiều dòng `sch_htb: quantum ...`. Đây là warning của `TCLink`, không phải lỗi hư topology.
- FRRouting trong project này chạy với custom `--vty_socket`, vì vậy không dùng `pe1 vtysh -c ...` kiểu mặc định. Phải dùng lệnh có `--vty_socket` như mục 12 và 13.

## 6. Bước 1: Chứng minh topology và thành phần mạng

Trong Mininet CLI:

```text
nodes
links
net
```

Cần chỉ rõ:

- Branch 1: `host1`, `host2`, `host3`, `host4`, `b1_ce`.
- Branch 2: `admin1`, `admin2`, `user1`, `user2`, `guest1`, `guest2`, `b2_ce`.
- Branch 3: `svr1`, `svr2`, `svr3a`, `svr3b`, `svr4`, `os1`, `os2`, `b3_ce`.
- PE: `pe1`, `pe2`, `pe3`.
- P: `p1`, `p2`, `p3`, `p4`.

Đây là bằng chứng yêu cầu "3 chi nhánh, 3 kiến trúc LAN, và nhà cung cấp Metro Ethernet/MPLS".

## 7. Bước 2: Chứng minh IP và default gateway

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

Cần nói:

- Branch 1 dùng `10.1.0.0/24`, gateway `10.1.0.1`.
- Branch 2 dùng `10.2.0.0/24`, gateway `10.2.0.1`.
- Branch 3 dùng `10.3.0.0/24`, gateway `10.3.0.1`.
- CE ở mỗi chi nhánh đóng vai trò gateway.

## 8. Bước 3: Ping nội bộ từng chi nhánh

Trong Mininet CLI:

```text
host1 ping -c 3 10.1.0.14
admin1 ping -c 3 10.2.0.31
svr1 ping -c 3 10.3.0.21
```

Ý nghĩa:

- `host1 -> host4`: nội bộ Branch 1.
- `admin1 -> guest1`: nội bộ Branch 2.
- `svr1 -> os1`: nội bộ Branch 3.

Kết quả mong đợi:

- `0% packet loss`.
- TTL nội bộ thường là `64`.
- Lần chạy benchmark ngày `2026-05-07` cho thấy delay nội bộ trung bình:
  - Branch 1: khoảng `6.624 ms`
  - Branch 2: khoảng `13.076 ms`
  - Branch 3: khoảng `10.805 ms`

## 9. Bước 4: Ping liên chi nhánh

Trong Mininet CLI:

```text
host1 ping -c 3 10.2.0.21
host2 ping -c 3 10.3.0.11
user1 ping -c 3 10.3.0.12
admin1 ping -c 3 10.1.0.11
```

Ý nghĩa:

- `host1 -> user1`: Branch 1 sang Branch 2.
- `host2 -> svr1`: Branch 1 sang Branch 3.
- `user1 -> svr2`: Branch 2 sang Branch 3.
- `admin1 -> host1`: Branch 2 quay về Branch 1.

Kết quả mong đợi:

- `0% packet loss`.
- TTL liên chi nhánh thường là `62`.
- Lần benchmark ngày `2026-05-07` cho thấy delay trung bình:
  - `host1 -> user1`: `33.726 ms`
  - `host2 -> svr1`: `39.835 ms`
  - `user1 -> svr2`: `36.056 ms`

## 10. Bước 5: Chứng minh đường đi bằng traceroute

Trong Mininet CLI:

```text
host1 traceroute -n 10.2.0.21
host2 traceroute -n 10.3.0.11
user1 traceroute -n 10.3.0.12
```

Cần giải thích đúng bản chất:

- Project này dùng `VPLS/L2VPN` trên underlay MPLS.
- Vì vậy `traceroute` liên chi nhánh không nhất thiết lộ đầy đủ từng hop `PE/P` như IP routing thuần.
- Traceroute thường hiện:
  - hop 1: CE local, ví dụ `10.1.0.1`
  - hop 2: địa chỉ service WAN của CE xa, ví dụ `172.16.100.2` hoặc `172.16.100.3`
  - hop cuối: host đích

Mẫu thực tế trên máy này:

```text
host1 traceroute -n 10.2.0.21
1  10.1.0.1
2  172.16.100.2
3  10.2.0.21
```

Cho nên:

- `traceroute` dùng để chứng minh traffic đã ra khỏi LAN và đi qua service liên chi nhánh.
- Bằng chứng chi tiết cho backbone MPLS phải lấy từ OSPF, LDP, `ip -f mpls route show`, và `tcpdump`.

## 11. Bước 6: Chứng minh Linux kernel MPLS route và label switching

Trong Mininet CLI:

```text
pe1 ip route show
pe1 ip -f mpls route show
pe2 ip -f mpls route show
pe3 ip -f mpls route show
p1 ip -f mpls route show
p2 ip -f mpls route show
p3 ip -f mpls route show
pe1 sysctl net.mpls.platform_labels
p3 sysctl net.mpls.platform_labels
```

Cần tìm và chỉ rõ:

- Dòng `encap mpls` trong `ip route show`.
- Dòng `proto ldp` trong `ip -f mpls route show`.
- Dòng `as to <label>` để chứng minh swap label.
- `net.mpls.platform_labels = 100000`.

Ví dụ thật trong lần benchmark `2026-05-07`:

```text
2.2.2.2 encap mpls 24 via 172.20.11.2 dev pe1-eth1 proto ospf
24 as to 22 via inet 172.20.11.2 dev pe1-eth1 proto ldp
```

Đây là bằng chứng Linux kernel đang push/swap label thật, không phải log mô phỏng.

## 12. Bước 7: Chứng minh OSPF hội tụ

Trong Mininet CLI:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show ip ospf neighbor"
pe2 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe2/vty -c "show ip ospf neighbor"
p3 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/p3/vty -c "show ip ospf neighbor"
```

Cần tìm:

- Trạng thái `Full`.
- Neighbor ID của router core/provider.

Mẫu thực tế trên `pe1`:

```text
11.11.11.11  Full/-
33.33.33.33  Full/-
```

Nếu muốn chỉ thêm route học được bởi OSPF:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show ip route ospf"
```

## 13. Bước 8: Chứng minh LDP hội tụ

Trong Mininet CLI:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show mpls ldp neighbor"
pe2 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe2/vty -c "show mpls ldp neighbor"
p3 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/p3/vty -c "show mpls ldp neighbor"
```

Nếu cần thêm bảng binding:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show mpls ldp ipv4 binding"
```

Cần tìm:

- Trạng thái `OPERATIONAL`.
- Remote label / local label.

Mẫu thực tế trên `pe1`:

```text
ipv4 2.2.2.2         OPERATIONAL
ipv4 3.3.3.3         OPERATIONAL
ipv4 11.11.11.11     OPERATIONAL
ipv4 33.33.33.33     OPERATIONAL
```

## 14. Bước 9: Bắt tcpdump để chứng minh gói MPLS thật

Trong Mininet CLI, bật capture trên link core `p3-eth0`, sau đó tạo traffic liên chi nhánh:

```text
p3 tcpdump -i p3-eth0 -e -n -c 5 mpls &
host1 ping -c 5 10.3.0.11
```

Nếu muốn tạo thêm traffic:

```text
p3 tcpdump -i p3-eth0 -e -n -c 10 mpls &
user1 ping -c 8 10.3.0.12
```

Cần tìm trong output:

- `ethertype MPLS unicast (0x8847)`
- `MPLS (label ... )`

Mẫu đã bắt được trong lần benchmark `2026-05-07`:

```text
ethertype MPLS unicast (0x8847)
MPLS (label 24, tc 0, [S], ttl 255)
10.1.0.11 > 10.2.0.21: ICMP echo request
```

Đây là bằng chứng quan trọng nhất cho yêu cầu "MPLS label switching thật".

Nếu output nền của `tcpdump` hiện hơi rối hoặc không dễ đọc trong buổi demo, vẫn có thể mở lại bằng chứng đã lưu từ lần benchmark full:

```bash
less results/tcpdump_mpls.txt
```

## 15. Bước 10: Thoát Mininet sau khi xong phần topology/MPLS

Trong Mininet CLI:

```text
exit
```

Sau khi về terminal Ubuntu:

```bash
sudo mn -c
```

## 16. Bước 11: Chạy từng phép đo hiệu năng bằng lệnh Ubuntu

Mỗi lệnh bên dưới sẽ tự khởi động topology, chạy phép đo thật, in output, rồi tắt topology.

Delay và packet loss cơ bản:

```bash
sudo python3 code/performance_test.py --mode mpls --action ping --source-host host1 --destination-host user1
sudo python3 code/performance_test.py --mode mpls --action delay --source-host host2 --destination-host svr1
```

Traceroute:

```bash
sudo python3 code/performance_test.py --mode mpls --action traceroute --source-host host1 --destination-host user1
```

Throughput TCP:

```bash
sudo python3 code/performance_test.py --mode mpls --action throughput --source-host host1 --destination-host user1
```

Jitter UDP:

```bash
sudo python3 code/performance_test.py --mode mpls --action jitter --source-host user1 --destination-host svr2
```

Packet loss sweep UDP 5M, 20M, 50M, 80M, 120M:

```bash
sudo python3 code/performance_test.py --mode mpls --action packet-loss --source-host host2 --destination-host svr1
```

Cần nói khi demo:

- `ping` và `delay` lấy số liệu từ `ping` thật.
- `throughput` lấy từ `iperf3 TCP`.
- `jitter` và `udp_packet_loss_percent` lấy từ `iperf3 UDP`.
- Số liệu không phải dữ liệu nhập tay.

## 17. Bước 12: Chạy full benchmark để sinh toàn bộ kết quả của đề

Chạy theo từng bước:

```bash
sudo python3 code/performance_test.py --mode mpls --stp-wait 20
python3 code/plot_results.py
python3 code/generate_report.py
```

Hoặc chạy một lệnh full pipeline:

```bash
sudo bash code/run_all.sh
```

Lần chạy lại ngày `2026-05-07` đã hoàn tất thành công và sinh mới:

- `results/results.csv`
- `results/ping_results.txt`
- `results/iperf_results.txt`
- `results/traceroute_results.txt`
- `results/mpls_routes.txt`
- `results/frr_control_plane.txt`
- `results/tcpdump_mpls.txt`
- `images/*_chart.png`
- `report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx`

## 18. Kiểm tra nhanh các bằng chứng sau khi chạy full benchmark

Kiểm tra file kết quả:

```bash
ls -lh results
ls -lh images/*_chart.png
ls -lh report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

Mở CSV:

```bash
column -s, -t < results/results.csv | less -S
```

Mở log raw:

```bash
less results/ping_results.txt
less results/traceroute_results.txt
less results/iperf_results.txt
less results/mpls_routes.txt
less results/frr_control_plane.txt
less results/tcpdump_mpls.txt
```

Lọc bằng chứng nhanh:

```bash
grep -n "encap mpls" results/mpls_routes.txt | head
grep -n "proto ldp" results/mpls_routes.txt | head
grep -n "Full" results/frr_control_plane.txt | head
grep -n "OPERATIONAL" results/frr_control_plane.txt | head
grep -n "MPLS unicast" results/tcpdump_mpls.txt | head
grep -n "0x8847" results/tcpdump_mpls.txt | head
```

## 19. Số liệu tham khảo từ lần chạy ngày 2026-05-07

Kết quả baseline trong `results/results.csv`:

- `host1 -> user1`: throughput `0.208 Mbps`, avg delay `33.726 ms`, packet loss `0.0%`, jitter `0.118 ms`
- `host2 -> svr1`: throughput `0.208 Mbps`, avg delay `39.835 ms`, packet loss `0.0%`, jitter `0.126 ms`
- `user1 -> svr2`: throughput `0.208 Mbps`, avg delay `36.056 ms`, packet loss `0.0%`, jitter `0.111 ms`
- `host1 -> host4`: throughput `94.447 Mbps`, avg delay `6.624 ms`
- `admin1 -> guest1`: throughput `93.959 Mbps`, avg delay `13.076 ms`
- `svr1 -> os1`: throughput `94.288 Mbps`, avg delay `10.805 ms`

Có thể dùng các số này để đối chiếu nhanh lúc demo. Nếu lần chạy mới ra số khác một ít, điều đó bình thường vì đây là benchmark thật.

## 20. Kịch bản nói ngắn khi demo

Bạn có thể nói ngắn gọn theo thứ tự này:

1. "Đây là mô hình Metro Ethernet kết nối 3 chi nhánh qua backbone của nhà cung cấp."
2. "Ba chi nhánh dùng ba kiến trúc LAN khác nhau: Flat, Three-tier, Leaf-Spine."
3. "Em kiểm tra node, link, IP và default gateway trước."
4. "Em ping nội bộ từng chi nhánh để chứng minh LAN hoạt động."
5. "Em ping liên chi nhánh để chứng minh dịch vụ Metro Ethernet thông suốt."
6. "Em dùng traceroute để thấy traffic đã ra khỏi LAN và vào service liên chi nhánh."
7. "Em dùng `ip route encap mpls`, `ip -f mpls route show`, OSPF và LDP để chứng minh backbone MPLS thật."
8. "Em bắt tcpdump trên core link và thấy `ethertype 0x8847`, đây là gói MPLS thật."
9. "Cuối cùng em chạy benchmark thật bằng ping và iperf3 để lấy throughput, delay, packet loss, jitter; sau đó tạo chart và report Word."

## 21. Xử lý lỗi nhanh khi demo

Nếu Mininet không start:

```bash
sudo mn -c
sudo systemctl restart openvswitch-switch
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 25
```

Nếu thiếu module MPLS:

```bash
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
sudo sysctl -w net.mpls.platform_labels=100000
```

Nếu FRRouting không lên:

```bash
sudo apt update
sudo apt install -y frr
sudo bash code/install_environment.sh
```

Nếu `vtysh -c ...` báo không thấy daemon, hãy chạy lại trong Mininet CLI như sau:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show ip ospf neighbor"
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show mpls ldp neighbor"
```

Lý do: project này chạy FRR với custom `--vty_socket`, không dùng socket mặc định của hệ thống.

Nếu benchmark hoặc GUI báo lỗi sudo:

```bash
sudo -v
sudo python3 code/performance_test.py --mode mpls --action ping --source-host host1 --destination-host user1
```

Nếu chart/report không tạo được:

```bash
ls -lh results/results.csv
python3 code/plot_results.py
python3 code/generate_report.py
```

## 22. Cleanup cuối buổi

Sau khi demo xong:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```
