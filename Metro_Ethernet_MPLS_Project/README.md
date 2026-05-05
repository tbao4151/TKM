# Metro Ethernet MPLS Project

Project mon hoc: **Thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep**.

## Muc tieu

- Mo phong 3 chi nhanh doanh nghiep tren Mininet.
- Ket noi cac chi nhanh qua provider backbone gom CE, PE va P router.
- Kiem thu that bang ping, iperf3 va traceroute.
- Tao `results/results.csv`, bieu do, bao cao Word va tai lieu van dap.

## Yeu cau he thong

- Ubuntu/Linux.
- Quyen sudo.
- Mininet, Open vSwitch, iperf/iperf3, traceroute, Python 3.

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
sudo python3 code/topology_mininet.py
```

Trong Mininet CLI co the demo:

```text
host1 ping -c 3 10.2.0.11
host2 traceroute -n 10.3.0.11
```

De chay do kiem tu dong:

```bash
sudo python3 code/performance_test.py
python3 code/plot_results.py
python3 code/generate_report.py
```

## Mo GUI

```bash
python3 code/gui_monitor.py
```

GUI goi script test that. Neu he thong yeu cau sudo, nhap mat khau trong terminal/GUI prompt cua he thong.

## Tao bao cao

Bao cao duoc tao tai:

```text
report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
```

`generate_report.py` chi tao bao cao khi da co `results/results.csv` co du lieu.

## Cleanup Mininet

```bash
sudo mn -c
```

## Ghi chu ve MPLS

Project uu tien MPLS native neu moi truong ho tro. Trong moi truong Mininet/Open vSwitch thong dung, label switching native co the khong kha dung, nen project dung static route that qua CE/PE/P de mo phong co che forwarding tuong duong MPLS ve logic. Du lieu do hieu nang van la du lieu that trong topology Mininet, khong phai du lieu mau.

## Kiem tra ket qua that

**Du lieu trong results/results.csv duoc tao tu kiem thu thuc te bang ping/iperf/traceroute trong Mininet. Neu file nay chua ton tai, can chay performance_test.py hoac run_all.sh.**

Kiem tra log:

```bash
cat results/ping_results.txt
cat results/iperf_results.txt
cat results/traceroute_results.txt
cat results/command_history.txt
```

Kiem tra khong luu mat khau:

```bash
grep -R "mat_khau_can_kiem_tra" . || echo "OK: password not found in project files"
```
