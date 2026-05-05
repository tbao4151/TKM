#!/usr/bin/env python3
"""Cau hinh IP va Linux kernel MPLS cho topology Metro Ethernet trong Mininet."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


PROJECT_NOTE = (
    "Mode mpls dung Linux kernel MPLS that: PE push label, P swap label, "
    "egress PE pop label ve CE; khong tao du lieu gia."
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
    },
    "p2": {
        "p2-eth0": "172.20.32.2/30",
        "p2-eth1": "172.20.12.2/30",
    },
    "p3": {
        "p3-eth0": "172.20.13.2/30",
        "p3-eth1": "172.20.23.2/30",
    },
    "p4": {
        "p4-eth0": "172.20.24.2/30",
        "p4-eth1": "172.20.34.2/30",
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
        ("10.2.0.0/24", "172.20.11.1"),
        ("10.3.0.0/24", "172.20.12.2"),
    ],
    "p2": [
        ("10.1.0.0/24", "172.20.12.1"),
        ("10.2.0.0/24", "172.20.32.1"),
        ("10.3.0.0/24", "172.20.32.1"),
    ],
    "p3": [
        ("10.1.0.0/24", "172.20.13.1"),
        ("10.2.0.0/24", "172.20.23.1"),
        ("10.3.0.0/24", "172.20.23.1"),
    ],
    "p4": [
        ("10.1.0.0/24", "172.20.24.1"),
        ("10.2.0.0/24", "172.20.24.1"),
        ("10.3.0.0/24", "172.20.34.1"),
    ],
}

CE_ROUTES: Dict[str, List[Tuple[str, str]]] = {
    router: routes for router, routes in STATIC_ROUTES.items() if router.endswith("_ce")
}

PE_LOCAL_ROUTES: Dict[str, List[Tuple[str, str]]] = {
    "pe1": [("10.1.0.0/24", "172.16.1.2")],
    "pe2": [("10.2.0.0/24", "172.16.2.2")],
    "pe3": [("10.3.0.0/24", "172.16.3.2")],
}

# Ingress PE IP routes that push MPLS labels for remote branch LANs.
MPLS_PUSH_ROUTES: Dict[str, List[Tuple[str, int, str, str]]] = {
    "pe1": [
        ("10.2.0.0/24", 120, "172.20.13.2", "pe1-eth2"),
        ("10.3.0.0/24", 130, "172.20.11.2", "pe1-eth1"),
    ],
    "pe2": [
        ("10.1.0.0/24", 210, "172.20.23.2", "pe2-eth1"),
        ("10.3.0.0/24", 230, "172.20.24.2", "pe2-eth2"),
    ],
    "pe3": [
        ("10.1.0.0/24", 310, "172.20.32.2", "pe3-eth1"),
        ("10.2.0.0/24", 320, "172.20.34.2", "pe3-eth2"),
    ],
}

# MPLS label forwarding entries. Entries with out_label=None pop at egress PE.
MPLS_LABEL_ROUTES: Dict[str, List[Tuple[int, int | None, str, str]]] = {
    "p3": [
        (120, 121, "172.20.23.1", "p3-eth1"),  # Branch1 -> Branch2
        (210, 211, "172.20.13.1", "p3-eth0"),  # Branch2 -> Branch1
    ],
    "p1": [
        (130, 131, "172.20.12.2", "p1-eth1"),  # Branch1 -> Branch3
        (311, 312, "172.20.11.1", "p1-eth0"),  # Branch3 -> Branch1
    ],
    "p2": [
        (131, 132, "172.20.32.1", "p2-eth0"),  # Branch1 -> Branch3
        (310, 311, "172.20.12.1", "p2-eth1"),  # Branch3 -> Branch1
    ],
    "p4": [
        (230, 231, "172.20.34.1", "p4-eth1"),  # Branch2 -> Branch3
        (320, 321, "172.20.24.1", "p4-eth0"),  # Branch3 -> Branch2
    ],
    "pe1": [(211, None, "172.16.1.2", "pe1-eth0"), (312, None, "172.16.1.2", "pe1-eth0")],
    "pe2": [(121, None, "172.16.2.2", "pe2-eth0"), (321, None, "172.16.2.2", "pe2-eth0")],
    "pe3": [(132, None, "172.16.3.2", "pe3-eth0"), (231, None, "172.16.3.2", "pe3-eth0")],
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
PROVIDER_ROUTERS = ["pe1", "pe2", "pe3", "p1", "p2", "p3", "p4"]


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
    TestPair("Branch1", "Branch1", "host1", "host4"),
    TestPair("Branch2", "Branch2", "admin1", "guest1"),
    TestPair("Branch3", "Branch3", "svr1", "os1"),
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


def ensure_kernel_mpls_support() -> None:
    for module in ("mpls_router", "mpls_iptunnel", "mpls_gso"):
        result = subprocess.run(["modprobe", module], text=True, capture_output=True)
        if result.returncode != 0 and module != "mpls_gso":
            message = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"Khong load duoc kernel module {module}: {message}")


def configure_mpls_sysctl(net) -> None:
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        run(router, "sysctl -w net.mpls.platform_labels=100000")
        for intf in ROUTER_INTERFACES[router_name]:
            run(router, f"sysctl -w net.mpls.conf.{intf}.input=1")


def configure_mpls_routes(net) -> None:
    for router_name, routes in CE_ROUTES.items():
        router = net.get(router_name)
        for network, gateway in routes:
            run(router, f"ip route replace {network} via {gateway}")

    for router_name, routes in PE_LOCAL_ROUTES.items():
        router = net.get(router_name)
        for network, gateway in routes:
            run(router, f"ip route replace {network} via {gateway}")

    for router_name, routes in MPLS_PUSH_ROUTES.items():
        router = net.get(router_name)
        for network, label, gateway, dev in routes:
            run(router, f"ip route replace {network} encap mpls {label} via {gateway} dev {dev}")

    for router_name, routes in MPLS_LABEL_ROUTES.items():
        router = net.get(router_name)
        for in_label, out_label, gateway, dev in routes:
            run(router, f"ip -f mpls route del {in_label} 2>/dev/null || true")
            if out_label is None:
                run(router, f"ip -f mpls route add {in_label} via inet {gateway} dev {dev}")
            else:
                run(router, f"ip -f mpls route add {in_label} as {out_label} via inet {gateway} dev {dev}")


def configure_switching(net) -> None:
    for switch_name in SWITCHES:
        switch = net.get(switch_name)
        run(switch, f"ovs-vsctl set-fail-mode {switch_name} standalone")
        # Topology lab da duoc giu loop-free de Mininet/OVS khoi dong nhanh tren VM nho.
        run(switch, f"ovs-vsctl set bridge {switch_name} stp_enable=false")


def configure_network(net, mode: str = "mpls") -> None:
    configure_switching(net)
    configure_hosts(net)
    configure_router_interfaces(net)
    if mode == "ip":
        configure_static_routes(net)
    elif mode == "mpls":
        ensure_kernel_mpls_support()
        configure_mpls_sysctl(net)
        configure_mpls_routes(net)
    else:
        raise ValueError(f"Unknown network mode: {mode}")


def collect_mpls_state(net) -> str:
    sections = []
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        sections.append(f"===== {router_name}: ip route show =====\n{run(router, 'ip route show')}")
        sections.append(f"===== {router_name}: ip -f mpls route show =====\n{run(router, 'ip -f mpls route show')}")
        sections.append(f"===== {router_name}: sysctl net.mpls.platform_labels =====\n{run(router, 'sysctl net.mpls.platform_labels')}")
    return "\n".join(sections)


def capture_mpls_packets(net, source_host: str = "host1", destination_host: str = "user1") -> str:
    capture_router = net.get("p3")
    source = net.get(source_host)
    destination_ip = HOST_IP[destination_host]
    capture_router.cmd("rm -f /tmp/mpls_capture.log")
    capture_router.cmd("timeout 12s tcpdump -vvv -eni p3-eth0 -XX -c 6 'ether proto 0x8847' >/tmp/mpls_capture.log 2>&1 &")
    capture_router.cmd("sleep 1")
    source.cmd(f"ping -c 12 -i 0.2 -W 2 {destination_ip}")
    capture_router.cmd("sleep 3")
    return capture_router.cmd("cat /tmp/mpls_capture.log 2>/dev/null")


def connectivity_checks(net, pairs: Iterable[TestPair] = TEST_PAIRS) -> List[Tuple[str, str, bool, str]]:
    checks = []
    for pair in pairs:
        src = net.get(pair.source_host)
        dst_ip = HOST_IP[pair.destination_host]
        output = run(src, f"ping -c 2 -W 2 {dst_ip}")
        checks.append((pair.source_host, pair.destination_host, " 0% packet loss" in output, output))
    return checks
