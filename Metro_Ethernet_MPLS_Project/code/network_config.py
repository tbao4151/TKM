#!/usr/bin/env python3
"""Cau hinh IP/routing cho topology Metro Ethernet MPLS-like trong Mininet.

Project nay uu tien du lieu do that. Phan forwarding duoc trien khai bang
Linux static routing qua cac node CE/PE/P that trong Mininet. Neu moi truong
khong ho tro MPLS native, day la co che chuyen tiep tuong duong ve logic:
luu luong van di theo duong CE -> PE -> P -> PE -> CE va co the kiem chung
bang ping/iperf/traceroute.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


PROJECT_NOTE = (
    "Forwarding MPLS-like bang static route that qua CE/PE/P trong Mininet; "
    "khong tao du lieu gia."
)

BRANCH_HOSTS: Dict[str, Dict[str, str]] = {
    "host1": {"ip": "10.1.0.11/24", "gw": "10.1.0.1", "branch": "Branch1"},
    "host2": {"ip": "10.1.0.12/24", "gw": "10.1.0.1", "branch": "Branch1"},
    "host3": {"ip": "10.1.0.13/24", "gw": "10.1.0.1", "branch": "Branch1"},
    "host4": {"ip": "10.1.0.14/24", "gw": "10.1.0.1", "branch": "Branch1"},
    "admin1": {"ip": "10.2.0.11/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "admin2": {"ip": "10.2.0.12/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "user1": {"ip": "10.2.0.21/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "user2": {"ip": "10.2.0.22/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "guest1": {"ip": "10.2.0.31/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "guest2": {"ip": "10.2.0.32/24", "gw": "10.2.0.1", "branch": "Branch2"},
    "svr1": {"ip": "10.3.0.11/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "svr2": {"ip": "10.3.0.12/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "svr3a": {"ip": "10.3.0.13/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "svr3b": {"ip": "10.3.0.14/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "svr4": {"ip": "10.3.0.15/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "os1": {"ip": "10.3.0.21/24", "gw": "10.3.0.1", "branch": "Branch3"},
    "os2": {"ip": "10.3.0.22/24", "gw": "10.3.0.1", "branch": "Branch3"},
}

HOST_IP = {name: cfg["ip"].split("/")[0] for name, cfg in BRANCH_HOSTS.items()}

ROUTER_INTERFACES: Dict[str, Dict[str, str]] = {
    "b1_ce": {"b1_ce-eth0": "10.1.0.1/24", "b1_ce-eth1": "172.16.1.2/30"},
    "b2_ce": {"b2_ce-eth0": "10.2.0.1/24", "b2_ce-eth1": "172.16.2.2/30"},
    "b3_ce": {"b3_ce-eth0": "10.3.0.1/24", "b3_ce-eth1": "172.16.3.2/30"},
    "pe1": {
        "pe1-eth0": "172.16.1.1/30",
        "pe1-eth1": "172.20.11.1/30",
        "pe1-eth2": "172.20.13.1/30",
    },
    "pe2": {
        "pe2-eth0": "172.16.2.1/30",
        "pe2-eth1": "172.20.23.1/30",
        "pe2-eth2": "172.20.24.1/30",
    },
    "pe3": {
        "pe3-eth0": "172.16.3.1/30",
        "pe3-eth1": "172.20.32.1/30",
        "pe3-eth2": "172.20.34.1/30",
    },
    "p1": {
        "p1-eth0": "172.20.11.2/30",
        "p1-eth1": "172.20.12.1/30",
        "p1-eth2": "172.20.113.1/30",
        "p1-eth3": "172.20.14.1/30",
    },
    "p2": {
        "p2-eth0": "172.20.32.2/30",
        "p2-eth1": "172.20.12.2/30",
        "p2-eth2": "172.20.124.1/30",
        "p2-eth3": "172.20.123.1/30",
    },
    "p3": {
        "p3-eth0": "172.20.13.2/30",
        "p3-eth1": "172.20.23.2/30",
        "p3-eth2": "172.20.113.2/30",
        "p3-eth3": "172.20.134.1/30",
        "p3-eth4": "172.20.123.2/30",
    },
    "p4": {
        "p4-eth0": "172.20.24.2/30",
        "p4-eth1": "172.20.34.2/30",
        "p4-eth2": "172.20.124.2/30",
        "p4-eth3": "172.20.134.2/30",
        "p4-eth4": "172.20.14.2/30",
    },
}

STATIC_ROUTES: Dict[str, List[Tuple[str, str]]] = {
    "b1_ce": [("10.2.0.0/24", "172.16.1.1"), ("10.3.0.0/24", "172.16.1.1")],
    "b2_ce": [("10.1.0.0/24", "172.16.2.1"), ("10.3.0.0/24", "172.16.2.1")],
    "b3_ce": [("10.1.0.0/24", "172.16.3.1"), ("10.2.0.0/24", "172.16.3.1")],
    "pe1": [
        ("10.1.0.0/24", "172.16.1.2"),
        ("10.2.0.0/24", "172.20.13.2"),
        ("10.3.0.0/24", "172.20.11.2"),
    ],
    "pe2": [
        ("10.2.0.0/24", "172.16.2.2"),
        ("10.1.0.0/24", "172.20.23.2"),
        ("10.3.0.0/24", "172.20.24.2"),
    ],
    "pe3": [
        ("10.3.0.0/24", "172.16.3.2"),
        ("10.1.0.0/24", "172.20.32.2"),
        ("10.2.0.0/24", "172.20.34.2"),
    ],
    "p1": [
        ("10.1.0.0/24", "172.20.11.1"),
        ("10.2.0.0/24", "172.20.113.2"),
        ("10.3.0.0/24", "172.20.12.2"),
    ],
    "p2": [
        ("10.1.0.0/24", "172.20.12.1"),
        ("10.2.0.0/24", "172.20.124.2"),
        ("10.3.0.0/24", "172.20.32.1"),
    ],
    "p3": [
        ("10.1.0.0/24", "172.20.13.1"),
        ("10.2.0.0/24", "172.20.23.1"),
        ("10.3.0.0/24", "172.20.134.2"),
    ],
    "p4": [
        ("10.1.0.0/24", "172.20.14.1"),
        ("10.2.0.0/24", "172.20.24.1"),
        ("10.3.0.0/24", "172.20.34.1"),
    ],
}

SWITCHES = [
    "b1_sw1",
    "b1_sw2",
    "b2_core1",
    "b2_core2",
    "b2_dist1",
    "b2_dist2",
    "b2_acc1",
    "b2_acc2",
    "b2_acc3",
    "b3_leaf1",
    "b3_leaf2",
    "b3_leaf3",
    "b3_leaf4",
    "b3_spine1",
    "b3_spine2",
]

ROUTERS = ["b1_ce", "b2_ce", "b3_ce", "pe1", "pe2", "pe3", "p1", "p2", "p3", "p4"]


@dataclass(frozen=True)
class TestPair:
    source_branch: str
    destination_branch: str
    source_host: str
    destination_host: str


TEST_PAIRS: List[TestPair] = [
    TestPair("Branch1", "Branch2", "host1", "user1"),
    TestPair("Branch1", "Branch3", "host2", "svr1"),
    TestPair("Branch2", "Branch3", "user1", "svr2"),
]


def run(node, command: str) -> str:
    """Chay lenh trong namespace cua node Mininet va tra output that."""
    return node.cmd(command)


def configure_hosts(net) -> None:
    for host_name, cfg in BRANCH_HOSTS.items():
        host = net.get(host_name)
        intf = f"{host_name}-eth0"
        run(host, f"ip addr flush dev {intf}")
        run(host, "ip route flush table main")
        run(host, f"ip addr add {cfg['ip']} dev {intf}")
        run(host, f"ip link set {intf} up")
        run(host, f"ip route add default via {cfg['gw']}")


def configure_router_interfaces(net) -> None:
    for router_name, interfaces in ROUTER_INTERFACES.items():
        router = net.get(router_name)
        run(router, "sysctl -w net.ipv4.ip_forward=1")
        run(router, "sysctl -w net.ipv4.conf.all.rp_filter=0")
        run(router, "sysctl -w net.ipv4.conf.default.rp_filter=0")
        for intf, ip_addr in interfaces.items():
            run(router, f"ip addr flush dev {intf}")
            run(router, f"ip addr add {ip_addr} dev {intf}")
            run(router, f"ip link set {intf} up")
            run(router, f"sysctl -w net.ipv4.conf.{intf}.rp_filter=0")


def configure_static_routes(net) -> None:
    for router_name, routes in STATIC_ROUTES.items():
        router = net.get(router_name)
        for network, gateway in routes:
            run(router, f"ip route replace {network} via {gateway}")


def configure_switching(net) -> None:
    for switch_name in SWITCHES:
        switch = net.get(switch_name)
        run(switch, f"ovs-vsctl set-fail-mode {switch_name} standalone")
        # So do moi co nhieu link du phong L2; bat STP de tranh loop broadcast.
        run(switch, f"ovs-vsctl set bridge {switch_name} stp_enable=true")


def configure_network(net) -> None:
    configure_switching(net)
    configure_hosts(net)
    configure_router_interfaces(net)
    configure_static_routes(net)


def connectivity_checks(net, pairs: Iterable[TestPair] = TEST_PAIRS) -> List[Tuple[str, str, bool, str]]:
    checks = []
    for pair in pairs:
        src = net.get(pair.source_host)
        dst_ip = HOST_IP[pair.destination_host]
        output = run(src, f"ping -c 2 -W 2 {dst_ip}")
        checks.append((pair.source_host, pair.destination_host, " 0% packet loss" in output, output))
    return checks
