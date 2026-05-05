# Linux kernel MPLS setup

Project chay native MPLS trong Mininet namespace.

## Kiem tra module

```bash
sudo modprobe mpls_router
sudo modprobe mpls_iptunnel
sudo modprobe mpls_gso || true
lsmod | grep mpls
sysctl net.mpls.platform_labels
```

## Chay benchmark MPLS

```bash
cd Metro_Ethernet_MPLS_Project
sudo mn -c
sudo python3 code/performance_test.py --mode mpls
```

## Bang chung can nop

- `results/mpls_routes.txt`: co `ip route show` va `ip -f mpls route show` tren PE/P.
- `results/tcpdump_mpls.txt`: co goi MPLS that bat tren link `p3-eth0`.
- `results/results.csv`: co cot `mode=mpls` va cac chi so throughput, delay, packet loss, jitter.

## Co che label

- PE ingress push label bang `ip route replace <prefix> encap mpls <label> via <next-hop> dev <interface>`.
- P router swap label bang `ip -f mpls route add <in-label> as <out-label> via inet <next-hop> dev <interface>`.
- PE egress pop label bang `ip -f mpls route add <label> via inet <CE-next-hop> dev <CE-interface>`.
