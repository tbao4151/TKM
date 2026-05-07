# Huong dan su dung gui_monitor

Tai lieu nay chi huong dan dung giao dien `code/gui_monitor.py`. GUI giup demo truc quan cac phep do that trong Mininet, nhung khong thay the hoan toan cac thao tac thu cong trong tai lieu demo Ubuntu.

## 1. GUI lam duoc gi

`gui_monitor.py` la giao dien Tkinter de:

- Chon source host va destination host.
- Chay Ping.
- Chay Traceroute.
- Do Throughput bang iperf3 TCP.
- Do Delay bang ping.
- Do Packet Loss bang iperf3 UDP load sweep.
- Do Jitter bang iperf3 UDP.
- Chay Full Benchmark.
- Doc va hien thi bang `results/results.csv`.
- Mo thu muc `images` de xem chart.
- Xem log lenh trong cua so rieng.

Tat ca nut test cua GUI goi lai `code/performance_test.py`, nen ket qua van la lenh that chay trong namespace Mininet, khong phai so lieu gia.

## 2. GUI co thay the hoan toan demo thu cong khong?

Khong. GUI khong thay the hoan toan cac thao tac thu cong trong `Huong_dan_demo_thu_cong_Ubuntu.md`.

GUI co the thay the phan chay nhanh cac phep do:

- Ping.
- Traceroute.
- Throughput.
- Delay.
- Packet loss.
- Jitter.
- Full benchmark tao `results/results.csv`.

GUI khong nen thay the cac phan sau khi thuyet trinh rubric:

- Kiem tra/cai moi truong Ubuntu bang `install_environment.sh`.
- Cleanup Mininet bang `sudo mn -c`.
- Mo Mininet CLI de chi ro `nodes`, `links`, `net`.
- Giai thich truc tiep topology CE/PE/P, 3 chi nhanh va 3 kien truc LAN.
- Xem thu cong `ip -f mpls route show` tren PE/P.
- Xem thu cong FRRouting `show ip ospf neighbor`, `show mpls ldp neighbor`.
- Bat tcpdump truc tiep tren core link de chung minh goi MPLS.
- Troubleshooting khi kernel MPLS, OVS, FRRouting hoac sudo gap loi.

Ket luan khi demo: dung GUI de trinh bay ket qua do cho dep va nhanh; van nen dung terminal thu cong de chung minh topology va MPLS label switching.

## 3. Chuan bi truoc khi mo GUI

Vao thu muc project:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
```

Kiem tra moi truong:

```bash
sudo bash code/install_environment.sh
sudo mn -c
```

Lay quyen sudo truoc khi bam nut trong GUI:

```bash
sudo -v
```

Ly do: GUI goi `sudo -n python3 ...`. Tuy chay tu giao dien, cac phep do van can quyen root de tao Mininet namespace. `sudo -v` giup GUI khong bi dung vi hoi mat khau trong nen.

## 4. Mo GUI

Chay:

```bash
python3 code/gui_monitor.py
```

Neu he thong khong co desktop/display, khong dung GUI. Khi do chay cac lenh terminal trong `Huong_dan_demo_thu_cong_Ubuntu.md`.

## 5. Cac thanh phan tren GUI

Khu vuc ben trai:

- `Source host`: chon host nguon.
- `Destination host`: chon host dich.
- `Ping`: chay ping that.
- `Traceroute`: chay traceroute that.
- `Throughput`: chay iperf3 TCP.
- `Delay`: chay ping va lay delay trung binh.
- `Packet Loss`: chay UDP load sweep.
- `Jitter`: chay iperf3 UDP.
- `Run Full Benchmark`: chay day du pipeline benchmark MPLS.
- `Open Charts`: mo thu muc `images`.
- `Reload Results`: doc lai `results/results.csv`.

Khu vuc ben phai:

- `Baseline rows`: so dong test baseline trong CSV.
- `Load sweep rows`: so dong packet-loss sweep.
- `Success rows`: so dong thanh cong.
- `Last run`: moc thoi gian dong ket qua gan nhat.
- Bang ket qua: doc truc tiep tu `results/results.csv`.
- `Open Log Window`: mo cua so log lon de xem output lenh.

## 6. Demo nhanh bang GUI

Chay theo thu tu nay de tranh roi:

1. Mo GUI:

```bash
python3 code/gui_monitor.py
```

2. Chon:

```text
Source host: host1
Destination host: user1
```

3. Bam `Ping`.

Noi khi demo: "Day la ping lien chi nhanh Branch 1 sang Branch 2."

4. Bam `Traceroute`.

Noi khi demo: "Traceroute cho thay duong di qua gateway va backbone."

5. Bam `Throughput`.

Noi khi demo: "Throughput duoc do bang iperf3 TCP, server va client deu nam trong Mininet namespace."

6. Chon:

```text
Source host: user1
Destination host: svr2
```

7. Bam `Jitter`.

Noi khi demo: "Jitter duoc do bang iperf3 UDP."

8. Bam `Packet Loss`.

Noi khi demo: "Packet loss duoc do khi tang offered load UDP 5M, 20M, 50M, 80M, 120M."

9. Bam `Run Full Benchmark` neu muon tao lai day du CSV.

10. Bam `Reload Results` de cap nhat bang.

11. Bam `Open Charts` sau khi da chay:

```bash
python3 code/plot_results.py
```

Hoac sau khi full pipeline `sudo bash code/run_all.sh` da hoan tat.

## 7. Full benchmark tu GUI

Nut `Run Full Benchmark` tuong duong lenh:

```bash
sudo -n python3 code/performance_test.py --mode mpls
```

Ket qua sinh ra:

```text
results/results.csv
results/ping_results.txt
results/iperf_results.txt
results/traceroute_results.txt
results/mpls_routes.txt
results/frr_control_plane.txt
results/tcpdump_mpls.txt
results/command_history.txt
```

Sau do neu can chart va report, chay them trong terminal:

```bash
python3 code/plot_results.py
python3 code/generate_report.py
```

Hoac dung pipeline day du:

```bash
sudo bash code/run_all.sh
```

## 8. Giai thich tung nut cho phan van dap

`Ping`:

- Goi `performance_test.py --action ping`.
- Dung de chung minh reachability va packet loss co ban.

`Traceroute`:

- Goi `performance_test.py --action traceroute`.
- Dung de chung minh duong di lien chi nhanh.

`Throughput`:

- Goi `performance_test.py --action throughput`.
- Dung iperf3 TCP.
- Ket qua chinh la Mbps.

`Delay`:

- Goi `performance_test.py --action delay`.
- Dung ping va lay RTT trung binh.
- Ket qua chinh la ms.

`Packet Loss`:

- Goi `performance_test.py --action packet-loss`.
- Dung iperf3 UDP voi nhieu muc tai.
- Ket qua chinh la `udp_packet_loss_percent`.

`Jitter`:

- Goi `performance_test.py --action jitter`.
- Dung iperf3 UDP.
- Ket qua chinh la ms.

`Run Full Benchmark`:

- Chay toan bo tap test trong `network_config.TEST_PAIRS`.
- Luu CSV va cac log bang chung.

## 9. Xu ly loi GUI

Neu bam nut va thay loi sudo:

```bash
sudo -v
python3 code/gui_monitor.py
```

Neu GUI khong mo duoc do thieu Tkinter:

```bash
sudo apt install -y python3-tk
python3 code/gui_monitor.py
```

Neu bang ket qua bao chua co CSV:

```bash
sudo python3 code/performance_test.py --mode mpls
python3 code/gui_monitor.py
```

Neu chart chua co:

```bash
python3 code/plot_results.py
```

Neu Mininet bi treo do lan demo truoc:

```bash
sudo pkill -f iperf3 || true
sudo pkill -f tcpdump || true
sudo mn -c
python3 code/gui_monitor.py
```

## 10. Loi khuyen khi thuyet trinh

Trinh bay dep nhat:

1. Dung terminal thu cong de chung minh topology, route MPLS va tcpdump MPLS.
2. Dung GUI de chon host va bam test cho nguoi xem thay thao tac truc quan.
3. Quay lai terminal de mo CSV/log/chart/report neu can bang chung chi tiet.
