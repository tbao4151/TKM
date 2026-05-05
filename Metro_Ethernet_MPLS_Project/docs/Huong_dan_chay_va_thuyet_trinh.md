# Huong dan chay va thuyet trinh

## 1. Project nay lam gi?

Project thiet ke va trien khai mo hinh Metro Ethernet ket noi 3 chi nhanh doanh nghiep qua provider backbone. Topology chay that tren Mininet, dung Open vSwitch cho cac switch LAN va Linux router namespace cho CE/PE/P.

## 2. Mo hinh tong the hoat dong nhu the nao?

Host trong tung chi nhanh gui traffic den CE. CE day traffic sang PE cua provider. Trong backbone, PE dau vao push MPLS label, P router swap label, PE dau ra pop label, sau do goi ve CE va LAN dich.

## 3. Giai thich Host, Switch, CE, PE, P

- Host: may tram tao luu luong ping/iperf/traceroute.
- Switch: thiet bi Layer 2 ket noi cac host trong LAN.
- CE: Customer Edge, router phia khach hang.
- PE: Provider Edge, router bien cua nha cung cap, noi voi CE.
- P: Provider router, router loi trong backbone.

## 4. Flat Network

Flat Network la mang phang, cac host gan vao cung mot switch access va cung subnet. Uu diem la don gian, de cau hinh; han che la kho mo rong va kho phan doan khi quy mo lon.

## 5. Three-tier Network

Three-tier chia LAN thanh Access, Distribution va Core. Access noi host, Distribution tap trung chinh sach/phan phoi, Core lam truc xuong song toc do cao.

## 6. Leaf-Spine Network

Leaf-Spine la kien truc hay dung trong data center. Host noi vao leaf, leaf noi len spine. Muc tieu la giam nghen va tao duong di dong deu. Trong lab nay topology duoc giu khong tao loop L2 de chay on dinh trong Mininet.

## 7. Metro Ethernet

Metro Ethernet la dich vu Ethernet trong pham vi do thi/khu vuc MAN, giup ket noi nhieu chi nhanh nhu dang mo rong LAN qua ha tang nha cung cap.

## 8. MPLS de hieu

MPLS co the hieu la gan "nhan duong di" cho goi tin. Router trong backbone khong can doc day du bang dinh tuyen IP moi lan ma chuyen tiep dua tren label.

## 9. Label switching la gi?

Label switching la co che router nhin label dau goi de quyet dinh chuyen tiep. Label co y nghia cuc bo giua cac router lien ke trong backbone.

## 10. Push, swap, pop label

- Push label: PE dau vao gan label cho goi tin.
- Swap label: P router doi label cu thanh label moi.
- Pop label: PE dau ra bo label truoc khi dua goi ve mang khach hang.

## 11. Duong di Branch 1 sang Branch 2

`host1 -> b1_sw1 -> b1_ce -> pe1 -> p3 -> pe2 -> b2_ce -> b2_core1 -> b2_dist1/b2_dist2 -> b2_acc2 -> user1`.

## 12. Duong di Branch 1 sang Branch 3

`host2 -> b1_sw1 -> b1_ce -> pe1 -> p1 -> p2 -> pe3 -> b3_ce -> b3_spine1 -> b3_leaf1 -> svr1`.

## 13. Duong di Branch 2 sang Branch 3

`user1 -> b2_acc2 -> b2_dist1/b2_dist2 -> b2_core1 -> b2_ce -> pe2 -> p4 -> pe3 -> b3_ce -> b3_spine1 -> b3_leaf2 -> svr2`.

## 14. Cach cai moi truong

```bash
cd Metro_Ethernet_MPLS_Project
chmod +x code/install_environment.sh
sudo bash code/install_environment.sh
```

Khi he thong yeu cau, nhap mat khau sudo cua may ao.

## 15. Cach chay tu dau den cuoi

```bash
cd Metro_Ethernet_MPLS_Project
chmod +x code/install_environment.sh
sudo bash code/install_environment.sh
sudo mn -c
python3 code/draw_topology.py
sudo python3 code/topology_mininet.py --mode mpls
sudo python3 code/performance_test.py --mode mpls
python3 code/plot_results.py
python3 code/generate_report.py
python3 code/gui_monitor.py
```

Trong thuc te, de tu dong hoa dung:

```bash
cd Metro_Ethernet_MPLS_Project
chmod +x code/run_all.sh
sudo bash code/run_all.sh
```

`performance_test.py` tu tao topology Mininet, chay test that, luu bang chung MPLS kernel trong `results/mpls_routes.txt` va `results/tcpdump_mpls.txt`, sau do stop topology. Neu muon demo thu cong, chay `sudo python3 code/topology_mininet.py --mode mpls` de vao Mininet CLI.

## 16. Cach cleanup Mininet

```bash
sudo mn -c
```

## 17. Cach doc results.csv

File `results/results.csv` co cac cot: timestamp, mode, source_branch, destination_branch, source_host, destination_host, throughput_mbps, avg_delay_ms, packet_loss_percent, jitter_ms, udp_packet_loss_percent, test_tool, note.

## 18. Cach doc bieu do throughput

Cot cang cao thi bang thong TCP iperf3 giua cap chi nhanh cang lon. Don vi la Mbps.

## 19. Cach doc bieu do delay

Delay la RTT trung binh tu ping. Cot cang thap thi thoi gian phan hoi cang tot.

## 20. Cach doc packet loss

Packet loss la ti le goi ping bi mat. 0% la tot nhat; gia tri cao cho thay loi ket noi hoac qua tai.

## 21. Cach doc jitter

Jitter la dao dong do tre cua luu luong UDP iperf3. Jitter thap tot cho voice/video.

## 22. Cach mo bao cao Word

Mo file `report/Bao_cao_Metro_Ethernet_MPLS_Mininet.docx` bang LibreOffice Writer hoac Microsoft Word.

## 23. Cach demo GUI

```bash
python3 code/gui_monitor.py
```

GUI co cac nut Ping, Traceroute, Throughput, Delay, Packet Loss va Jitter. Cac nut nay goi `sudo python3 code/performance_test.py`, vi vay do la test that trong Mininet, khong phai du lieu mau.

## 24. Checklist truoc khi thuyet trinh

- Da chay `sudo bash code/run_all.sh`.
- `results/results.csv` co du lieu va timestamp moi.
- `results/ping_results.txt`, `iperf_results.txt`, `traceroute_results.txt` co log that.
- `results/mpls_routes.txt` co `ip -f mpls route show` that tren PE/P.
- `results/tcpdump_mpls.txt` co goi MPLS bat duoc tren core link.
- Cac anh trong `images/` da tao.
- Bao cao Word da tao.
- Chay `grep -R` de dam bao khong co mat khau trong project.
- Chuan bi lenh demo: `sudo python3 code/topology_mininet.py`.

## 25. Cau hoi van dap va tra loi mau

1. Metro Ethernet la gi?  
Tra loi: La mang/dich vu Ethernet pham vi do thi dung de ket noi cac diem cua doanh nghiep qua ha tang nha cung cap.

2. MPLS khac IP routing o diem nao?  
Tra loi: MPLS chuyen tiep theo label, IP routing chuyen tiep theo dia chi IP dich va bang dinh tuyen.

3. CE la gi?  
Tra loi: CE la router bien phia khach hang, noi LAN chi nhanh voi provider.

4. PE la gi?  
Tra loi: PE la router bien phia nha cung cap, noi CE vao backbone.

5. P router la gi?  
Tra loi: P router nam trong loi provider, chuyen tiep luu luong giua cac PE.

6. Vi sao Branch 1 goi la Flat Network?  
Tra loi: Vi host nam cung subnet va noi qua mot switch access don gian.

7. Uu diem Three-tier la gi?  
Tra loi: De mo rong, de quan tri va tach ro access, distribution, core.

8. Leaf-Spine phu hop o dau?  
Tra loi: Phu hop data center, noi nhieu server voi duong di dong deu.

9. Push label la gi?  
Tra loi: Gan label vao goi khi vao mien MPLS.

10. Swap label la gi?  
Tra loi: Thay label cu bang label moi tren router trung gian.

11. Pop label la gi?  
Tra loi: Bo label truoc khi goi ra khoi mien MPLS.

12. Project co dung du lieu gia khong?  
Tra loi: Khong. `results.csv` duoc tao tu ping, iperf3 va traceroute that trong Mininet.

13. Neu iperf fail thi sao?  
Tra loi: Script ghi fail vao log va note, khong tu dien so lieu dep.

14. Throughput do bang gi?  
Tra loi: iperf3 TCP.

15. Jitter do bang gi?  
Tra loi: iperf3 UDP.

16. Delay do bang gi?  
Tra loi: ping RTT trung binh.

17. Packet loss do bang gi?  
Tra loi: ping packet loss.

18. Traceroute dung de lam gi?  
Tra loi: Kiem tra duong di goi tin qua CE/PE/P.

19. Vi sao can `sudo`?  
Tra loi: Mininet tao namespace, interface ao va OVS bridge nen can quyen root.

20. MPLS native co chay khong?  
Tra loi: Co. Lab load `mpls_router`, `mpls_iptunnel`, cau hinh `ip route encap mpls` tren PE, `ip -f mpls route` tren P/PE, va dung tcpdump bat goi MPLS that tren link core.

21. MPLS-like nghia la gi?  
Tra loi: La cach mo phong logic neu may khong ho tro kernel MPLS. Ban hien tai uu tien mode `mpls` native; chi dung `--mode ip` lam baseline so sanh.

22. File cau hinh route nam dau?  
Tra loi: `code/network_config.py`.

23. File topology nam dau?  
Tra loi: `code/topology_mininet.py`.

24. Lam sao tao lai bieu do?  
Tra loi: Chay `python3 code/plot_results.py` sau khi co `results/results.csv`.

25. Lam sao tao lai bao cao?  
Tra loi: Chay `python3 code/generate_report.py` sau khi da co CSV va chart.

26. Neu ping lien chi nhanh fail thi kiem tra gi?  
Tra loi: Kiem tra IP host, default gateway, IP forwarding tren CE/PE/P, `net.mpls.platform_labels`, `net.mpls.conf.<interface>.input`, `ip route show` tren PE va `ip -f mpls route show` tren P/PE.

27. Vi sao packet loss co the khac 0?  
Tra loi: Do tai may ao, OVS, CPU scheduler hoac loi ket noi trong topology.

28. Vi sao throughput khong dat dung bw link?  
Tra loi: Do overhead TCP, tai CPU, gioi han Mininet/TCLink va thoi gian test.

29. Co the mo rong len 4 chi nhanh khong?  
Tra loi: Co, them CE/PE, subnet LAN, static route va cap test moi.

30. Loi ich chinh cua project la gi?  
Tra loi: Vua co thiet ke ly thuyet, vua co topology chay that va so lieu do thuc te.
