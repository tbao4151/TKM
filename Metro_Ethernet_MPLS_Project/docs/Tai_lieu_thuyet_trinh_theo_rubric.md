# Tai lieu thuyet trinh theo rubric

De tai: Thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep  
Sinh vien: Nguyen Van Thien Bao - 52300179

Tai lieu nay dung de cam noi khi thuyet trinh. Thu tu ben duoi bam sat rubric cham diem: mo dau bang so do tong quan, sau do di lan luot 1/ Hinh thuc, 2/ Noi dung ly thuyet, 4/ Demo & trien khai, 5/ Kha nang bien luan.

## 0. Chuan bi truoc khi vao phong

Chay trong thu muc project:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo -v
sudo mn -c
```

Neu can tao lai toan bo ket qua:

```bash
sudo bash code/run_all.sh
```

Neu can mo GUI demo:

```bash
sudo -v
python3 code/gui_monitor.py
```

Neu can mo slide:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/latex_report
xdg-open slides.pdf
```

Neu can build lai slide:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/latex_report
pdflatex slides.tex
```

## 1. Thu tu thuyet trinh nhanh 7-10 phut

1. Mo dau bang so do tong quan: noi bai co 3 chi nhanh, 3 kien truc LAN khac nhau, ket noi qua CE-PE-P backbone MPLS.
2. Rubric 1 - Hinh thuc: chi ra bao cao Word, LaTeX, muc luc, hinh anh, tai lieu tham khao.
3. Rubric 2 - Ly thuyet: giai thich Metro Ethernet, CE/PE/P, MPLS push/swap/pop, OSPF/LDP, VPLS/L2VPN.
4. Rubric 4 - Demo & trien khai: day la phan diem lon nhat; mo terminal/GUI va chung minh topology, MPLS, tcpdump, performance, log.
5. Rubric 5 - Bien luan: noi ro cac lenh co the show tai cho va cac file co the sua nhanh.
6. Ket luan: nhan manh so lieu that, khong dung du lieu gia, co raw log va co pipeline tu dong.

## 2. Slide 1 sau bia - Tong quan so do mang

Slide: `Tong quan so do mang Metro Ethernet MPLS`

File/hinh can mo:

```text
latex_report/image/topology_overview.png
Metro_Ethernet_MPLS_Project/images/topology_overview.png
Metro_Ethernet_MPLS_Project/code/topology_mininet.py
```

Noi khi thuyet trinh:

```text
Day la mo hinh tong the cua de tai. Em chia doanh nghiep thanh 3 chi nhanh:
Branch 1 dung Flat Network, Branch 2 dung Three-tier, Branch 3 dung Leaf-Spine.
Moi chi nhanh noi vao router CE, sau do di qua mang nha cung cap gom PE va P router.
Luu luong lien chi nhanh khong di truc tiep giua cac LAN, ma di theo duong CE -> PE -> P -> PE -> CE qua backbone MPLS.
```

Lenh demo neu thay yeu cau chay topology:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo mn -c
sudo python3 code/topology_mininet.py --mode mpls --test-mode --stp-wait 20
```

## 3. Rubric 1 - Hinh thuc (1.5 diem)

### 1.1 Bo cuc bao cao

File minh chung:

```text
Metro_Ethernet_MPLS_Project/report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
latex_report/main.tex
latex_report/main.pdf
```

Lenh mo:

```bash
xdg-open report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx
xdg-open ../latex_report/main.pdf
```

Noi khi thuyet trinh:

```text
Bao cao duoc trinh bay theo cau truc 5 chuong: gioi thieu, co so ly thuyet, thiet ke, trien khai-danh gia, ket luan.
Ngoai ban Word, em co them ban LaTeX theo mau bao cao, co phu luc va tai lieu tham khao.
```

### 1.2 Hinh anh va so do

File minh chung:

```text
images/topology_overview.png
images/branch1_flat.png
images/branch2_three_tier.png
images/branch3_leaf_spine.png
images/mpls_backbone.png
```

Lenh xem nhanh:

```bash
ls -lh images/topology_overview.png images/branch1_flat.png images/branch2_three_tier.png images/branch3_leaf_spine.png images/mpls_backbone.png
xdg-open images/topology_overview.png
```

Noi khi thuyet trinh:

```text
Phan hinh anh tach ro LAN tung chi nhanh va backbone nha cung cap. Tren so do co phan biet CE, PE, P va cac nhom Flat, Three-tier, Leaf-Spine.
```

### 1.3 Muc luc va danh muc

File minh chung:

```text
latex_report/main.tex
latex_report/main.pdf
```

Noi khi thuyet trinh:

```text
Ban LaTeX dung tableofcontents, listoffigures va listoftables tu dong, nen muc luc va danh muc hinh/bang duoc cap nhat theo noi dung that.
```

### 1.4 Trich dan va tai lieu

File minh chung:

```text
latex_report/tailieuthamkhao.bib
latex_report/main.pdf
```

Noi khi thuyet trinh:

```text
Tai lieu tham khao gom Metro Ethernet Forum, RFC 3031 ve MPLS, RFC 5036 ve LDP, tai lieu Mininet, Open vSwitch, Linux MPLS, FRRouting va iperf3.
```

### 1.5 Loi chinh ta

Noi khi thuyet trinh:

```text
Noi dung da duoc viet lai theo dung de tai Metro Ethernet MPLS, thong nhat thuat ngu CE, PE, P, MPLS, LDP, VPLS va cac chi so hieu nang.
```

## 4. Rubric 2 - Noi dung ly thuyet (1.5 diem)

### 2.1 Cach hanh van

File minh chung:

```text
latex_report/chuongs/chuong2.tex
Metro_Ethernet_MPLS_Project/docs/Kich_ban_thuyet_trinh.md
```

Noi khi thuyet trinh:

```text
Trong phan ly thuyet, em khong chi neu dinh nghia ma gan truc tiep voi mo hinh bai lam:
CE la router phia khach hang, PE la bien nha cung cap, P la router loi.
Metro Ethernet dong vai tro ha tang MAN, con MPLS giup chuyen tiep bang nhan tren backbone.
```

### 2.2 Tinh dung dan

File code/minh chung:

```text
code/network_config.py
results/mpls_routes.txt
results/frr_control_plane.txt
results/tcpdump_mpls.txt
```

Lenh xem:

```bash
cat results/mpls_routes.txt
cat results/frr_control_plane.txt
cat results/tcpdump_mpls.txt
```

Noi khi thuyet trinh:

```text
MPLS hoat dong theo ba buoc: ingress PE push label, P router swap label, egress PE pop label.
OSPF tao underlay de cac router PE/P biet duong di den loopback nhau.
LDP phan phoi label dong. Bang chung nam o frr_control_plane.txt voi OSPF Full va LDP OPERATIONAL.
Voi VPLS/L2VPN, cac CE lien chi nhanh duoc noi qua bridge va pseudowire GRETAP full-mesh co split-horizon.
```

## 5. Rubric 4 - Demo & trien khai (5.0 diem)

Day la phan can noi ky nhat vi chiem 5 diem.

### 4.1 Topology & Kien truc (0.75 diem)

File code:

```text
code/topology_mininet.py
code/draw_topology.py
draw_network_topology.py
```

Lenh chay:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo mn -c
sudo python3 code/topology_mininet.py --mode mpls --test-mode --stp-wait 20
```

Neu muon vao Mininet CLI:

```bash
sudo python3 code/topology_mininet.py --mode mpls
```

Lenh trong Mininet CLI:

```text
nodes
links
host1 ping -c 3 10.2.0.21
host2 traceroute -n 10.3.0.11
exit
```

Noi khi thuyet trinh:

```text
File topology_mininet.py tao toan bo he thong tren Mininet: host, switch LAN, CE, PE va P router.
Branch 1 la Flat Network, Branch 2 la Three-tier, Branch 3 la Leaf-Spine.
Khi chay test-mode, script tu khoi tao topology, cau hinh mang va chay precheck ket noi.
```

### 4.2 MPLS & VPLS Core (1.0 diem)

File code:

```text
code/network_config.py
code/topology_mininet.py
results/frr_control_plane.txt
results/mpls_routes.txt
```

Lenh xem minh chung:

```bash
cat results/frr_control_plane.txt
cat results/mpls_routes.txt
```

Noi khi thuyet trinh:

```text
network_config.py bat Linux kernel MPLS, cau hinh interface, route, bridge L2VPN va khoi chay FRRouting trong namespace PE/P.
OSPF giup mang loi hoi tu, LDP cap label dong, con VPLS/L2VPN noi cac CE lien chi nhanh.
Trong frr_control_plane.txt co OSPF Full, LDP OPERATIONAL, label binding va running-config L2VPN.
```

### 4.3 Xac minh chuyen nhan (0.75 diem)

File minh chung:

```text
results/tcpdump_mpls.txt
results/mpls_routes.txt
```

Lenh xem:

```bash
cat results/tcpdump_mpls.txt
cat results/mpls_routes.txt
```

Tu khoa can chi vao:

```text
ethertype MPLS unicast (0x8847)
MPLS (label ...)
encap mpls
proto ldp
as to
```

Noi khi thuyet trinh:

```text
Day la phan chung minh quan trong nhat cua MPLS.
tcpdump bat duoc ethertype 0x8847, nghia la goi tin that su co MPLS shim header, khong phai chi la IP routing.
Trong bang route, encap mpls the hien push label; as to the hien swap label tren router loi; egress PE pop label va dua goi ve CE dich.
```

### 4.4 Phan tich hieu nang (1.0 diem)

File code:

```text
code/performance_test.py
code/plot_results.py
results/results.csv
images/throughput_chart.png
images/delay_chart.png
images/packet_loss_chart.png
images/jitter_chart.png
```

Lenh chay full benchmark:

```bash
sudo python3 code/performance_test.py --mode mpls
python3 code/plot_results.py
```

Lenh chay tung phep do:

```bash
sudo python3 code/performance_test.py --action throughput --source-host host1 --destination-host user1 --mode mpls
sudo python3 code/performance_test.py --action delay --source-host host1 --destination-host user1 --mode mpls
sudo python3 code/performance_test.py --action jitter --source-host host1 --destination-host user1 --mode mpls
sudo python3 code/performance_test.py --action packet-loss --source-host host1 --destination-host user1 --mode mpls
```

Noi khi thuyet trinh:

```text
performance_test.py chay ping, traceroute va iperf3 that trong namespace Mininet.
Ket qua duoc ghi vao results.csv, sau do plot_results.py ve bieu do throughput, delay, jitter va packet loss.
Packet loss duoc do bang UDP load sweep voi cac muc 5M, 20M, 50M, 80M va 120M.
Khi tai vuot nang luc backbone, loss tang ro, nen ket qua phan anh hanh vi mang that.
```

### 4.5 Minh chung ket qua (0.75 diem)

File minh chung:

```text
results/ping_results.txt
results/iperf_results.txt
results/traceroute_results.txt
results/mpls_routes.txt
results/frr_control_plane.txt
results/tcpdump_mpls.txt
results/command_history.txt
```

Lenh xem nhanh:

```bash
tail -n 40 results/command_history.txt
tail -n 60 results/ping_results.txt
tail -n 80 results/iperf_results.txt
cat results/traceroute_results.txt
```

Noi khi thuyet trinh:

```text
Tat ca so lieu tren slide va bao cao deu co raw log di kem.
Ping log chung minh connectivity va delay, iperf log chung minh throughput/jitter/loss, traceroute log chung minh duong di, tcpdump va mpls_routes chung minh MPLS label.
```

### 4.6 Trien khai nghien cuu (0.75 diem)

File code:

```text
code/run_all.sh
code/gui_monitor.py
code/generate_report.py
code/plot_results.py
```

Lenh demo GUI:

```bash
sudo -v
python3 code/gui_monitor.py
```

Trong GUI:

```text
Chon source host1, destination user1.
Bam Ping, Throughput, Packet Loss hoac Jitter.
Bam Open Log Window de xem log phong to/thu nho.
Bam Open Charts de mo thu muc bieu do.
```

Noi khi thuyet trinh:

```text
Ngoai viec chay lenh rieng le, em co tu dong hoa bang run_all.sh.
Script nay cleanup Mininet, ve so do, chay benchmark, ve chart va tao bao cao Word.
GUI Tkinter giup thay/nguoi nghe chon cap host va chay tung test truc quan, log duoc hien trong cua so rieng de theo doi.
```

## 6. Rubric 5 - Kha nang bien luan (2.0 diem)

### 5.1 Tra loi cau hoi (1.5 diem)

Lenh can nho:

```bash
cat results/frr_control_plane.txt
cat results/mpls_routes.txt
cat results/tcpdump_mpls.txt
cat results/results.csv
```

Lenh neu dang trong Mininet CLI:

```text
host1 ping -c 3 10.2.0.21
host2 traceroute -n 10.3.0.11
```

Cau tra loi mau:

```text
MPLS khac IP routing o cho router loi khong can quyet dinh dua tren IP prefix tung goi, ma chuyen tiep dua tren label.
Ingress PE push label, P router swap label, egress PE pop label.
Trong bai nay, OSPF tao underlay va LDP cap label dong, nen label khong phai cau hinh tinh bang tay.
```

Neu bi hoi "co phai du lieu gia khong?":

```text
Khong. results.csv duoc tao tu performance_test.py khi topology Mininet dang chay.
Raw output nam trong ping_results.txt, iperf_results.txt, traceroute_results.txt va tcpdump_mpls.txt.
```

Neu bi hoi ve VPLS:

```text
Trong Mininet, data-plane L2VPN duoc hien thuc bang full-mesh Linux GRETAP pseudowire co port-isolation/split-horizon.
Underlay cua pseudowire chay qua MPLS/OSPF/LDP. FRR running-config van co block L2VPN/VPLS de the hien control-plane theo rubric.
```

### 5.2 Chinh sua cau hinh tai cho (0.5 diem)

File can biet de sua nhanh:

```text
code/topology_mininet.py      # them/bot node, link, bandwidth, delay
code/network_config.py        # IP, route, MPLS, FRR, L2VPN
code/performance_test.py      # cap host test, loai test, UDP load sweep
code/gui_monitor.py           # giao dien demo
```

Lenh tim nhanh trong code:

```bash
rg -n "HOST_IP|TEST_PAIRS|UDP_LOAD_LEVELS|addLink|iperf|mpls|ldp|ospf" code
```

Noi khi thuyet trinh:

```text
Neu can thay doi cap host test, em sua TEST_PAIRS trong network_config.py.
Neu can thay tai UDP, em sua UDP_LOAD_LEVELS trong performance_test.py.
Neu can thay bandwidth/delay link, em sua addLink trong topology_mininet.py.
```

## 7. Kich ban demo truc tiep neu chi co 3-5 phut

Chay nhanh:

```bash
cd /home/bao/ThietKeMang/Project_Cuoi_Ky/Metro_Ethernet_MPLS_Project
sudo -v
python3 code/gui_monitor.py
```

Trong GUI:

```text
1. Chon host1 -> user1.
2. Bam Ping de chung minh ket noi lien chi nhanh.
3. Bam Throughput de cho thay iperf3 TCP.
4. Bam Packet Loss de cho thay UDP load sweep.
5. Bam Open Log Window de phong to log.
6. Bam Open Charts de mo bieu do.
```

Neu khong dung GUI:

```bash
sudo python3 code/performance_test.py --action ping --source-host host1 --destination-host user1 --mode mpls
sudo python3 code/performance_test.py --action throughput --source-host host1 --destination-host user1 --mode mpls
sudo python3 code/performance_test.py --action packet-loss --source-host host1 --destination-host user1 --mode mpls
cat results/tcpdump_mpls.txt
```

## 8. Cau ket luan de noi cuoi bai

```text
Tong ket lai, bai lam da dung duoc topology Metro Ethernet MPLS da chi nhanh tren Mininet,
co 3 kien truc LAN khac nhau, co MPLS label switching that, co OSPF/LDP, co service L2VPN/VPLS,
co benchmark throughput, delay, jitter, packet loss va co bieu do/bao cao sinh tu so lieu that.
Phan quan trong nhat la moi ket qua deu co raw log de doi chieu, nen co the demo va kiem chung lai truc tiep.
```

