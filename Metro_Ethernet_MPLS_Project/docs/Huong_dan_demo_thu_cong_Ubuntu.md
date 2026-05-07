# Hướng dẫn demo thủ công trên Ubuntu

Tài liệu này là runbook demo thủ công cho đồ án `Metro_Ethernet_MPLS_Project`. Bản này đã được viết lại sau khi chạy thật lại benchmark trên chính máy này vào ngày `2026-05-07`, từ `19:42` đến `19:47` giờ `Asia/Ho_Chi_Minh`, bằng các lệnh:

```bash
sudo python3 code/performance_test.py --mode mpls --stp-wait 20
python3 code/plot_results.py
```

Mục tiêu của tài liệu:

1. Demo đúng thứ tự các bằng chứng mà thầy thường hỏi.
2. Có sẵn kết quả mẫu vừa chạy thật để đối chiếu khi thuyết trình.
3. Giải thích từng thuộc tính quan trọng trong output và trong các biểu đồ, không chỉ liệt kê lệnh.
4. Giải thích rõ vì sao biểu đồ throughput lệch rất mạnh và phần nào của độ lệch là "đúng theo thiết kế", phần nào là "bất thường của lab TCP hiện tại".

## 1. Những gì cần chứng minh khi demo

Khi demo, nên lần lượt chứng minh đủ các ý sau:

1. Có 3 chi nhánh LAN khác nhau.
2. Branch 1 là `Flat Network`.
3. Branch 2 là `Core - Distribution - Access`.
4. Branch 3 là `Leaf - Spine`.
5. Có miền nhà cung cấp gồm `CE`, `PE`, `P`.
6. Topology chạy thật bằng `Mininet`, switch là `OVS`, router là `Linux node`.
7. Ping nội bộ và liên chi nhánh thành công.
8. `traceroute` liên chi nhánh chạy được.
9. OSPF hội tụ.
10. LDP hội tụ.
11. Linux kernel MPLS có route `encap mpls` và bảng `ip -f mpls route show`.
12. `tcpdump` bắt được gói `ethertype MPLS unicast (0x8847)`.
13. Có benchmark thật bằng `ping`, `iperf3 TCP`, `iperf3 UDP`, `traceroute`.
14. Có file log `results/*.txt`, bảng `results/results.csv` và chart trong `images/`.

## 2. Kết quả mẫu của lần chạy thật ngày 2026-05-07

Đây là 6 dòng baseline vừa được sinh lại từ `results/results.csv`:

| Cặp đo | Throughput (Mbps) | Avg delay (ms) | Ping loss (%) | Jitter (ms) | UDP loss baseline (%) |
|---|---:|---:|---:|---:|---:|
| `host1 -> user1` | `0.208` | `33.445` | `0.0` | `0.206` | `0.0` |
| `host2 -> svr1` | `0.208` | `39.705` | `0.0` | `0.161` | `0.0` |
| `user1 -> svr2` | `0.208` | `35.763` | `0.0` | `0.207` | `0.0` |
| `host1 -> host4` | `94.713` | `6.563` | `0.0` | `0.083` | `0.0` |
| `admin1 -> guest1` | `93.961` | `12.926` | `0.0` | `0.112` | `0.0` |
| `svr1 -> os1` | `94.127` | `10.931` | `0.0` | `0.124` | `0.0` |

Đây là 3 cặp `udp_load_sweep` để vẽ `packet_loss_chart.png`:

| Pair | 5 Mbps | 20 Mbps | 50 Mbps | 80 Mbps | 120 Mbps |
|---|---:|---:|---:|---:|---:|
| `Branch1 -> Branch2` | `0.0%` | `0.0%` | `0.0%` | `23.876%` | `55.714%` |
| `Branch1 -> Branch3` | `0.0%` | `0.0%` | `1.976%` | `30.661%` | `47.704%` |
| `Branch2 -> Branch3` | `0.0%` | `0.0%` | `0.0%` | `22.413%` | `43.611%` |

Nhận xét ngắn từ bộ số liệu này:

- Nội bộ chi nhánh đạt khoảng `94 Mbps`, gần sát các link `100 Mbps`.
- Liên chi nhánh có `delay` cao hơn vì đi qua CE/PE/P và lớp dịch vụ VPLS/MPLS.
- UDP load sweep cho thấy backbone/service path còn mang được tải vài chục Mbps, nhưng bắt đầu mất gói mạnh từ mức `80 Mbps`.
- TCP liên chi nhánh chỉ còn khoảng `0.208 Mbps`, thấp bất thường so với giới hạn danh định của backbone. Phần này sẽ được giải thích kỹ ở mục 11.

## 3. Giải thích từng cột trong `results/results.csv`

File `results/results.csv` là file tổng hợp quan trọng nhất. Thầy hỏi cột nào cũng nên trả lời được:

- `timestamp`: thời điểm dòng kết quả được ghi.
- `mode`: mode forward của topology. Ở lần chạy này là `mpls`.
- `test_type`: loại dòng dữ liệu.
  - `baseline`: phép đo chuẩn cho 1 cặp host.
  - `udp_load_sweep`: phép đo UDP nhiều mức tải để vẽ packet loss theo tải.
- `load_mbps`: chỉ có ý nghĩa với `udp_load_sweep`. Ví dụ `80` nghĩa là client UDP phát với offered load `80 Mbps`.
- `source_branch`, `destination_branch`: chi nhánh nguồn và đích.
- `source_host`, `destination_host`: host cụ thể được dùng để đo.
- `throughput_mbps`: throughput TCP lấy từ `iperf3`.
  - Trong code hiện tại, parser ưu tiên `end.sum_received.bits_per_second`, nếu không có mới dùng `sum_sent`.
  - Vì vậy con số chart là phía nhận thực sự nhận được, không phải chỉ là phía gửi đã cố gửi.
- `avg_delay_ms`: `RTT trung bình` từ `ping`, parse từ dòng `rtt min/avg/max/mdev`.
- `packet_loss_percent`: tỷ lệ mất gói của `ping`.
- `jitter_ms`: jitter từ `iperf3 UDP` baseline `10 Mbps`.
- `udp_packet_loss_percent`: tỷ lệ mất gói của `iperf3 UDP`.
  - Ở baseline: đo khi phát UDP `10 Mbps`.
  - Ở `udp_load_sweep`: đo tại từng mức `5/20/50/80/120 Mbps`.
- `test_tool`: công cụ tạo ra số liệu.
- `note`: trạng thái dòng đo. `success` là thành công. Nếu lỗi sẽ có dạng `fail; ...`.

Điểm rất dễ bị hỏi nhầm:

- `packet_loss_percent` và `udp_packet_loss_percent` không cùng nguồn.
- `packet_loss_percent` là từ `ping`.
- `udp_packet_loss_percent` là từ `iperf3 UDP`.
- `packet_loss_chart.png` ưu tiên vẽ `udp_load_sweep` từ `udp_packet_loss_percent`, chỉ fallback về `packet_loss_percent` nếu không có sweep.

## 4. Chuẩn bị terminal và môi trường

Vào thư mục project:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
pwd
ls
```

Lấy quyền sudo trước:

```bash
sudo -v
```

Dọn Mininet cũ:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
```

Kiểm tra/cài môi trường:

```bash
sudo bash code/install_environment.sh
```

Kiểm tra nhanh:

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

Kết quả mong đợi:

- Có `mpls_router` và `mpls_iptunnel`.
- `net.mpls.platform_labels` lớn hơn `0`, trong project này là `100000`.

## 5. Giải thích từng sơ đồ topology

Nên mở lại hình bằng:

```bash
python3 code/draw_topology.py
ls -lh output
ls -lh images/topology_overview.png images/branch1_flat.png images/branch2_three_tier.png images/branch3_leaf_spine.png images/mpls_backbone.png
```

### 5.1. `output/so_do_tong_hop.png` hoặc `images/topology_overview.png`

Tác dụng:

- Là hình tổng hợp toàn bộ hệ thống.
- Dùng để giới thiệu luồng lớn của bài toán trước khi đi vào từng chi nhánh.

Thuộc tính cần chỉ trên hình:

- Có `3 branch` ở phía khách hàng.
- Có `3 CE` nối branch ra WAN.
- Có `3 PE` và `4 P` tạo backbone nhà cung cấp.
- Traffic liên chi nhánh buộc phải đi qua miền provider.

Ý nghĩa khi vấn đáp:

- Chứng minh đề tài không phải 1 LAN đơn lẻ, mà là mô hình Metro Ethernet/MPLS nhiều chi nhánh.

### 5.2. `output/chi_nhanh_1.png` hoặc `images/branch1_flat.png`

Tác dụng:

- Dùng để chứng minh Branch 1 là mô hình `Flat Network`.

Thuộc tính cần chỉ:

- `host1..host4` nối về 2 switch access.
- Hai switch access nối trực tiếp với nhau.
- `b1_ce` là gateway đi ra WAN.

Ý nghĩa:

- Phù hợp site nhỏ, ít tầng, dễ triển khai.
- Đường nội bộ ngắn nên delay thấp, throughput nội bộ thường cao.

### 5.3. `output/chi_nhanh_2.png` hoặc `images/branch2_three_tier.png`

Tác dụng:

- Dùng để chứng minh Branch 2 là `Core - Distribution - Access`.

Thuộc tính cần chỉ:

- `b2_acc*` là access cho user.
- `b2_dist*` gom lưu lượng.
- `b2_core*` là lõi LAN của chi nhánh.
- `b2_ce` nối LAN ra WAN/MPLS.

Ý nghĩa:

- Phù hợp site doanh nghiệp phân tầng rõ.
- Số hop nội bộ nhiều hơn Branch 1 nên delay nội bộ thường cao hơn Branch 1.

### 5.4. `output/chi_nhanh_3.png` hoặc `images/branch3_leaf_spine.png`

Tác dụng:

- Dùng để chứng minh Branch 3 là `Leaf - Spine`.

Thuộc tính cần chỉ:

- `leaf` kết nối server/host.
- `spine` làm tầng trung gian tốc độ cao.
- `b3_ce` là điểm ra WAN.

Ý nghĩa:

- Mô phỏng kiểu mạng hiện đại, scale tốt cho server farm.
- Trong project này, hình được giữ `loop-free` để Mininet/OVS khởi động ổn định.

### 5.5. `images/mpls_backbone.png`

Tác dụng:

- Đây là hình quan trọng nhất để nói về Metro Ethernet/MPLS.

Thuộc tính cần chỉ:

- `CE`: router phía khách hàng, làm gateway cho LAN chi nhánh.
- `PE`: router biên nhà cung cấp, nơi kết cuối dịch vụ VPLS/L2VPN.
- `P`: router lõi, chỉ quan tâm label switching.
- Các link backbone có `bw` và `delay` riêng trong Mininet:
  - `CE-PE`: `80 Mbps`, `2 ms`
  - `PE-P`: `60 Mbps`, `3 ms`
  - `P1-P2`: `50 Mbps`, `4 ms`

Ý nghĩa:

- Đây là phần giúp giải thích vì sao liên chi nhánh chậm hơn nội bộ.
- Nó cũng là nền để giải thích packet loss tăng khi UDP offered load tăng.

## 6. Khởi động topology thủ công

Khởi động Mininet ở mode MPLS:

```bash
sudo python3 code/topology_mininet.py --mode mpls --stp-wait 20
```

Sau khi thấy `mininet>`, thực hiện các bước dưới đây.

Lưu ý:

- Có thể xuất hiện nhiều dòng `sch_htb: quantum ...`. Đây là warning của `TCLink`, không phải lỗi hỏng topology.
- FRRouting trong project này chạy với `--vty_socket` riêng, nên phải gọi `vtysh --vty_socket ...`.

## 7. Trình tự demo thủ công nên dùng

### 7.1. Chứng minh topology

Trong Mininet CLI:

```text
nodes
links
net
```

Phải chỉ ra:

- Branch 1: `host1`, `host2`, `host3`, `host4`, `b1_ce`
- Branch 2: `admin1`, `admin2`, `user1`, `user2`, `guest1`, `guest2`, `b2_ce`
- Branch 3: `svr1`, `svr2`, `svr3a`, `svr3b`, `svr4`, `os1`, `os2`, `b3_ce`
- Provider: `pe1`, `pe2`, `pe3`, `p1`, `p2`, `p3`, `p4`

### 7.2. Chứng minh IP và gateway

```text
host1 ip addr show host1-eth0
host1 ip route
admin1 ip addr show admin1-eth0
admin1 ip route
svr1 ip addr show svr1-eth0
svr1 ip route
```

Nói ngắn:

- Branch 1 dùng `10.1.0.0/24`, gateway `10.1.0.1`
- Branch 2 dùng `10.2.0.0/24`, gateway `10.2.0.1`
- Branch 3 dùng `10.3.0.0/24`, gateway `10.3.0.1`

### 7.3. Ping nội bộ

```text
host1 ping -c 3 10.1.0.14
admin1 ping -c 3 10.2.0.31
svr1 ping -c 3 10.3.0.21
```

Kết quả mẫu từ lần chạy thật:

- `host1 -> host4`: `avg 6.563 ms`, `0% loss`
- `admin1 -> guest1`: `avg 12.926 ms`, `0% loss`
- `svr1 -> os1`: `avg 10.931 ms`, `0% loss`

### 7.4. Ping liên chi nhánh

```text
host1 ping -c 3 10.2.0.21
host2 ping -c 3 10.3.0.11
user1 ping -c 3 10.3.0.12
```

Kết quả mẫu từ lần chạy thật:

- `host1 -> user1`: `avg 33.445 ms`, `0% loss`
- `host2 -> svr1`: `avg 39.705 ms`, `0% loss`
- `user1 -> svr2`: `avg 35.763 ms`, `0% loss`

### 7.5. Traceroute liên chi nhánh

```text
host1 traceroute -n 10.2.0.21
host2 traceroute -n 10.3.0.11
user1 traceroute -n 10.3.0.12
```

Mẫu thật:

```text
host1 traceroute -n 10.2.0.21
1  10.1.0.1
2  172.16.100.2
3  10.2.0.21
```

Giải thích:

- Hop 1 là CE local.
- Hop 2 là WAN service IP của CE đích trong VPLS.
- Hop 3 là host đích.
- Không phải mọi hop `PE/P` đều lộ ra như IP routing thuần vì project đang dùng VPLS/L2VPN trên MPLS.

### 7.6. Chứng minh Linux kernel MPLS

```text
pe1 ip route show
pe1 ip -f mpls route show
pe2 ip -f mpls route show
pe3 ip -f mpls route show
p3 ip -f mpls route show
```

Mẫu thật:

```text
2.2.2.2 nhid 25 encap mpls 20 via 172.20.13.2 dev pe1-eth2 proto ospf metric 20
24 as to 22 via inet 172.20.11.2 dev pe1-eth1 proto ldp
net.mpls.platform_labels = 100000
```

Ý nghĩa từng thuộc tính:

- `encap mpls 20`: IP route này khi đi ra sẽ push label `20`.
- `via 172.20.13.2`: next-hop IP trên backbone.
- `dev pe1-eth2`: đi ra interface nào.
- `proto ospf`: route IP underlay do OSPF học được.
- `24 as to 22`: label vào `24` sẽ được swap thành `22`.
- `proto ldp`: label mapping do LDP cấp phát.
- `platform_labels = 100000`: kernel cho phép bảng label đủ lớn để xử lý MPLS.

### 7.7. Chứng minh OSPF hội tụ

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show ip ospf neighbor"
pe2 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe2/vty -c "show ip ospf neighbor"
p3  vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/p3/vty  -c "show ip ospf neighbor"
```

Mẫu thật trên `pe1`:

```text
Neighbor ID     Pri State    Up Time  Dead Time Address       Interface
11.11.11.11       1 Full/-   ...
33.33.33.33       1 Full/-   ...
```

Giải thích từng thuộc tính chính:

- `Neighbor ID`: router-id OSPF của hàng xóm.
- `State`: phải là `Full/-` mới chứng minh adjacency đã hoàn tất.
- `Address`: IP của hàng xóm trên link underlay.
- `Interface`: interface cục bộ đang kết nối hàng xóm đó.

Nếu cần sâu hơn:

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show ip route ospf"
```

Ở đây có thể chỉ thêm các route có `label ...`, chứng minh OSPF và MPLS đang đi cùng nhau.

### 7.8. Chứng minh LDP hội tụ

```text
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show mpls ldp neighbor"
pe1 vtysh --vty_socket /tmp/metro_ethernet_mpls_frr/pe1/vty -c "show mpls ldp ipv4 binding"
```

Mẫu thật:

```text
AF   ID              State       Remote Address    Uptime
ipv4 2.2.2.2         OPERATIONAL 2.2.2.2          00:00:12
ipv4 3.3.3.3         OPERATIONAL 3.3.3.3          00:00:12
```

Giải thích:

- `AF`: address-family, ở đây là `ipv4`.
- `ID`: LSR ID của hàng xóm LDP.
- `State`: phải là `OPERATIONAL`.
- `Remote Address`: địa chỉ nhận diện bên kia.
- `Uptime`: thời gian phiên LDP đã sống.

Trong `show mpls ldp ipv4 binding`:

- `Destination`: FEC đích.
- `Local Label`: label router hiện tại cấp cho FEC đó.
- `Remote Label`: label hàng xóm quảng bá cho FEC đó.
- `In Use`: dòng nào `yes` là đang được dùng trong forwarding.

### 7.9. Chứng minh gói MPLS thật bằng tcpdump

```text
p3 tcpdump -i p3-eth0 -e -n -c 5 mpls &
host1 ping -c 5 10.2.0.21
```

Mẫu thật vừa bắt được:

```text
ethertype MPLS unicast (0x8847), length 144: MPLS (label 20, tc 0, [S], ttl 64)
1.1.1.1 > 2.2.2.2: GREv0, Flags [key present], key=0x64, proto TEB (0x6558)
10.1.0.11 > 10.2.0.21: ICMP echo request
```

Giải thích:

- `ethertype MPLS unicast (0x8847)`: gói trên wire là MPLS unicast.
- `label 20`: label đang dùng tại thời điểm bắt.
- `tc 0`: traffic class MPLS.
- `[S]`: bottom-of-stack, tức đây là label cuối trong stack.
- `ttl 64`: TTL của MPLS shim.
- `1.1.1.1 > 2.2.2.2`: outer underlay/IP của tunnel giữa PE.
- `GREv0`, `proto TEB`: payload đang là Ethernet over GRE bridge pseudowire.
- `10.1.0.11 > 10.2.0.21`: payload gốc bên trong vẫn là gói giữa 2 host chi nhánh.

Đây là bằng chứng mạnh nhất để trả lời câu hỏi "MPLS ở đây là thật hay chỉ mô phỏng logic".

## 8. Giải thích từng output mẫu mà thầy hay hỏi sâu

### 8.1. `ping`

Mẫu thật:

```text
64 bytes from 10.2.0.21: icmp_seq=1 ttl=62 time=33.3 ms
...
rtt min/avg/max/mdev = 33.180/33.445/34.226/0.307 ms
```

Giải thích:

- `64 bytes`: kích thước payload ICMP nhận được.
- `icmp_seq`: số thứ tự gói ping.
- `ttl=62`: TTL còn lại khi gói tới đích.
  - Nội bộ thường thấy `64`.
  - Liên chi nhánh thường giảm còn `62` vì đã qua thêm router/service path.
- `time=33.3 ms`: RTT của riêng gói đó.
- `min/avg/max`: RTT nhỏ nhất, trung bình, lớn nhất.
- `mdev`: độ dao động quanh giá trị trung bình.

### 8.2. `traceroute`

Mẫu thật:

```text
1  10.1.0.1       4.222 ms
2  172.16.100.2  25.008 ms
3  10.2.0.21     33.470 ms
```

Giải thích:

- Cột đầu là số hop.
- Cột giữa là địa chỉ node trả lời hop đó.
- Cột cuối là RTT đến hop đó.
- Ở project này, traceroute đang cho thấy gateway nội bộ và service WAN của CE, không nhất thiết lộ toàn bộ PE/P.

### 8.3. `iperf3 TCP`

Mẫu thật của phiên bất thường `host1 -> user1`:

```text
"bytes": 0,
"bits_per_second": 0,
"retransmits": 20,
...
"bytes": 131072,
"bits_per_second": 1048978.779656562,
...
"sum_sent":     419301.42288232141 bps
"sum_received": 208246.9341659694 bps
```

Giải thích:

- `bytes`: lượng dữ liệu truyền trong interval đó.
- `bits_per_second`: throughput của interval đó.
- `retransmits`: số segment TCP phải gửi lại.
- `snd_cwnd`: cửa sổ congestion hiện tại của TCP sender.
- `snd_wnd`: cửa sổ nhận quảng bá từ phía nhận.
- `rtt`: RTT mà TCP stack quan sát.
- `pmtu`: path MTU mà socket đang tin là hợp lệ.
- `sum_sent`: tốc độ phía gửi cố gửi ra.
- `sum_received`: tốc độ phía nhận thực sự nhận được.

Trong code hiện tại, `throughput_mbps` lấy từ `sum_received`, nên dòng CSV/biểu đồ của cặp này ra `0.208 Mbps`, không phải `0.419 Mbps`.

Mẫu thật của phiên bình thường `host1 -> host4`:

```text
"retransmits": 0,
"sum_received": 94712874.141387329
```

Ý nghĩa:

- TCP nội bộ không retransmit.
- Throughput nhận thực khoảng `94.713 Mbps`, phù hợp link `100 Mbps` sau khi trừ overhead.

### 8.4. `iperf3 UDP`

Mẫu baseline UDP:

```text
"bits_per_second": 9998286.9092951864,
"jitter_ms": 0.20643471221139234,
"lost_percent": 0
```

Giải thích:

- UDP baseline đang phát mục tiêu `10 Mbps`.
- `bits_per_second` gần `10 Mbps` nghĩa là sender bắn đúng mức tải.
- `jitter_ms` là độ dao động trễ giữa các datagram.
- `lost_percent` là tỷ lệ datagram UDP bị mất.

### 8.5. `show ip route ospf`

Mẫu thật:

```text
O>* 3.3.3.3/32 [110/30] via 172.20.11.2, pe1-eth1, label 24
```

Giải thích:

- `O`: route do OSPF học được.
- `>*`: đang được chọn và đã vào FIB.
- `[110/30]`: `110` là administrative distance, `30` là metric/cost.
- `via 172.20.11.2`: next hop.
- `pe1-eth1`: interface đi ra.
- `label 24`: khi forward route này, FIB gắn label MPLS tương ứng.

## 9. Chạy benchmark thủ công từng phần

Các lệnh này tự dựng topology, chạy đo, rồi dừng topology:

```bash
sudo python3 code/performance_test.py --mode mpls --action ping --source-host host1 --destination-host user1
sudo python3 code/performance_test.py --mode mpls --action traceroute --source-host host1 --destination-host user1
sudo python3 code/performance_test.py --mode mpls --action throughput --source-host host1 --destination-host user1
sudo python3 code/performance_test.py --mode mpls --action delay --source-host host2 --destination-host svr1
sudo python3 code/performance_test.py --mode mpls --action jitter --source-host user1 --destination-host svr2
sudo python3 code/performance_test.py --mode mpls --action packet-loss --source-host host2 --destination-host svr1
```

Full benchmark:

```bash
sudo python3 code/performance_test.py --mode mpls --stp-wait 20
python3 code/plot_results.py
python3 code/generate_report.py
```

Hoặc:

```bash
sudo bash code/run_all.sh
```

## 10. Giải thích từng biểu đồ trong `images/`

### 10.1. `images/throughput_chart.png`

Nguồn dữ liệu:

- Chỉ lấy các dòng `baseline`.
- Cột dùng là `throughput_mbps`.
- Được vẽ bởi `code/plot_results.py`.

Trục:

- Trục X: cặp chi nhánh kiểm thử, ví dụ `MPLS: Branch1 -> Branch2`.
- Trục Y: throughput TCP, đơn vị `Mbps`.

Tác dụng:

- So sánh hiệu năng TCP giữa nội bộ và liên chi nhánh.
- Dùng để thấy ngay hiệu quả end-to-end của dịch vụ.

Phải nói rõ khi demo:

- Đây là `TCP receiver throughput` của 1 phiên `iperf3` dài `5 giây`.
- Đây không phải "bandwidth danh nghĩa của backbone".
- Nó phản ánh cả route, encapsulation, MTU, queue, retransmission và cơ chế TCP.

### 10.2. `images/delay_chart.png`

Nguồn dữ liệu:

- Dòng `baseline`.
- Cột `avg_delay_ms` từ `ping`.

Trục:

- X: cặp kiểm thử.
- Y: `RTT trung bình (ms)`.

Tác dụng:

- So sánh độ trễ nội bộ và liên chi nhánh.
- Dùng để chứng minh càng nhiều lớp mạng và encapsulation thì RTT càng tăng.

### 10.3. `images/packet_loss_chart.png`

Nguồn dữ liệu:

- Nếu có `udp_load_sweep`, chart dùng `udp_packet_loss_percent`.
- Chỉ khi không có sweep mới fallback sang `packet_loss_percent` của ping.

Trục:

- X: `UDP offered load (Mbps)`.
- Y: `UDP packet loss (%)`.

Tác dụng:

- Đây là biểu đồ quan trọng để nói về ngưỡng chịu tải.
- Nó không nói tốc độ TCP.
- Nó cho thấy khi tăng offered load thì loss tăng dần, đặc biệt từ mức `80 Mbps` trở lên.

### 10.4. `images/jitter_chart.png`

Nguồn dữ liệu:

- Dòng `baseline`.
- Cột `jitter_ms` từ `iperf3 UDP 10 Mbps`.

Trục:

- X: cặp kiểm thử.
- Y: jitter, đơn vị `ms`.

Tác dụng:

- Dùng để đánh giá độ ổn định trễ của dịch vụ.
- Thích hợp để trả lời câu hỏi liên quan đến voice/video hoặc ứng dụng thời gian thực.

## 11. Tại sao biểu đồ throughput lệch rất mạnh

Đây là câu hỏi cần trả lời tách làm 2 phần, không nên trả lời chung chung.

### 11.1. Phần lệch "đúng theo thiết kế"

Nội bộ chi nhánh cao hơn liên chi nhánh là hợp lý vì:

1. Link host-switch và switch-switch trong LAN được đặt `100 Mbps`, `1 ms`.
2. Liên chi nhánh phải đi qua thêm `CE`, `PE`, `P`, rồi thêm lớp `VPLS/GRE/MPLS`.
3. Backbone có link thấp hơn LAN:
   - `CE-PE`: `80 Mbps`
   - `PE-P`: `60 Mbps`
   - `P1-P2`: `50 Mbps`
4. Liên chi nhánh có nhiều hop hơn nên `delay` cao hơn.

Vì vậy, việc nội bộ khoảng `94 Mbps` còn liên chi nhánh thấp hơn nội bộ là đúng về mặt kiến trúc.

### 11.2. Phần lệch "bất thường" của lần chạy hiện tại

Con số `0.208 Mbps` cho cả 3 cặp liên chi nhánh là thấp bất thường nếu so với backbone danh định `50-80 Mbps`.

Bằng chứng từ log thật:

1. Ping liên chi nhánh vẫn `0% loss`, RTT ổn định khoảng `33-40 ms`.
2. OSPF `Full`, LDP `OPERATIONAL`, `tcpdump` bắt được MPLS thật.
3. UDP load sweep vẫn đẩy được `50 Mbps`, `80 Mbps`, `120 Mbps` offered load và chỉ bắt đầu mất gói mạnh ở tải cao.
4. Nhưng `iperf3 TCP` liên chi nhánh có nhiều interval `0 bit/s` và `retransmits` rất cao.

Ví dụ phiên `host1 -> user1`:

```text
interval 0-1s: bytes=0, bits_per_second=0, retransmits=20
interval 2-3s: bytes=0, bits_per_second=0, retransmits=16
interval 3-4s: bytes=0, bits_per_second=0, retransmits=14
sum_sent     = 419301.42288232141 bps
sum_received = 208246.9341659694 bps
```

Diễn giải:

- Đường đi không chết, vì ping/UDP vẫn qua được.
- Vấn đề nằm ở hiệu quả TCP trên service path VPLS hiện tại.
- Đây là throughput end-to-end thật của TCP trong lab này, nhưng là một giá trị "xấu bất thường", không phải năng lực danh định của MPLS backbone.

### 11.3. Nguyên nhân kỹ thuật hợp lý nhất để trả lời

Không nên khẳng định quá tay là do duy nhất một nguyên nhân. Nên trả lời theo hướng:

- Project đang dùng `VPLS/L2VPN` bằng `Linux bridge + gretap pseudowire` trên `MPLS`.
- Toàn bộ service path bị ép `MTU = 1400`.
- TCP liên chi nhánh đang chịu thêm encapsulation `Ethernet -> GRE -> IP -> MPLS`, cộng qdisc của Mininet/OVS trong VM.
- Log `iperf3 TCP` cho thấy hiện tượng chủ đạo là `retransmission`, không phải mất reachability.
- Vì vậy chart throughput đang phản ánh "TCP efficiency của stack VPLS/GRE/MPLS trong lab VM hiện tại", chứ không phản ánh trần băng thông thuần của các link backbone.

Nếu thầy hỏi "vậy vì sao UDP lại còn lên được vài chục Mbps":

- Vì UDP không có cơ chế congestion control và retransmission như TCP.
- TCP nhạy với queue, retransmission, cửa sổ congestion và hiệu ứng path MTU.
- Do đó cùng một service path, UDP sweep vẫn có thể bắn ở tải cao, còn TCP effective throughput có thể rơi rất sâu.

Nếu thầy hỏi "vậy số liệu này có sai không":

- Không sai vì log là thật và chart được vẽ trực tiếp từ log thật.
- Nhưng cần nói đúng bản chất: đây là hiệu năng thực nghiệm của cách đóng gói dịch vụ hiện tại trong lab, không phải chỉ số tối ưu của MPLS nói chung.

Nếu thầy hỏi "nên cải thiện thế nào nếu muốn throughput đẹp hơn":

- Tách chart nội bộ và liên chi nhánh riêng để tránh hiểu nhầm.
- Đo thêm `mode ip` làm baseline đối chiếu.
- Tối ưu service MTU/offload/qdisc.
- Thử thêm `iperf3 -P` nhiều stream hoặc kiểm tra lại data-plane VPLS/GRETAP.

## 12. Cách nói ngắn gọn khi trình bày throughput chart

Có thể nói nguyên văn ngắn như sau:

> Biểu đồ throughput đang đo throughput TCP phía nhận của từng phiên iperf3 5 giây. Nội bộ chi nhánh lên khoảng 94 Mbps vì đi trên LAN 100 Mbps. Ba cặp liên chi nhánh chỉ còn khoảng 0.208 Mbps là bất thường, và log iperf3 cho thấy nguyên nhân trực tiếp là TCP retransmission rất cao trên service path VPLS over GRE over MPLS trong môi trường Mininet/OVS/VM. Vì vậy biểu đồ này là số liệu thật, nhưng nó phản ánh hiệu quả TCP của lab hiện tại chứ không phải trần băng thông danh định của backbone MPLS.

## 13. Kiểm tra nhanh các bằng chứng sau khi chạy full benchmark

```bash
ls -lh results
ls -lh images/*_chart.png
ls -lh report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
column -s, -t < results/results.csv | less -S
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
grep -n "retransmits" results/iperf_results.txt | head -n 20
```

## 14. Kết luận để chốt buổi demo

Nên chốt bằng 3 ý:

1. Topology, OSPF, LDP, kernel MPLS và tcpdump đều chứng minh MPLS/VPLS đang chạy thật.
2. Delay, jitter, UDP loss và bảng CSV/chart đều sinh từ đo kiểm thật, không phải nhập tay.
3. Throughput nội bộ đẹp, throughput TCP liên chi nhánh đang bất thường do hiệu quả TCP trên service path VPLS/GRE/MPLS của lab hiện tại, và log `iperf3` đã chỉ ra rõ triệu chứng `retransmission`.
