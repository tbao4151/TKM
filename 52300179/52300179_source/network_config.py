#!/usr/bin/env python3
"""Cau hinh IP va Linux kernel MPLS cho topology Metro Ethernet trong Mininet."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


PROJECT_NOTE = (
    "Mode mpls dung Linux kernel MPLS va FRRouting OSPF/LDP/VPLS: "
    "CE lien chi nhanh di qua VPLS/L2VPN data-plane tren backbone MPLS; khong tao du lieu gia."
)

FRR_DIR = Path("/tmp/metro_ethernet_mpls_frr")
FRR_DAEMON_DIR = Path("/usr/lib/frr")
VPLS_SERVICE_MTU = 1400

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

VPLS_CE_WAN: Dict[str, Tuple[str, str]] = {
    "b1_ce": ("b1_ce-eth1", "172.16.100.1/24"),
    "b2_ce": ("b2_ce-eth1", "172.16.100.2/24"),
    "b3_ce": ("b3_ce-eth1", "172.16.100.3/24"),
}

VPLS_CE_ROUTES: Dict[str, List[Tuple[str, str]]] = {
    "b1_ce": [("10.2.0.0/24", "172.16.100.2"), ("10.3.0.0/24", "172.16.100.3")],
    "b2_ce": [("10.1.0.0/24", "172.16.100.1"), ("10.3.0.0/24", "172.16.100.3")],
    "b3_ce": [("10.1.0.0/24", "172.16.100.1"), ("10.2.0.0/24", "172.16.100.2")],
}

FRR_VPLS_ACCESS_INTERFACES: Dict[str, str] = {
    "pe1": "pe1-eth0",
    "pe2": "pe2-eth0",
    "pe3": "pe3-eth0",
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

FRR_ROUTER_IDS: Dict[str, str] = {
    "pe1": "1.1.1.1",
    "pe2": "2.2.2.2",
    "pe3": "3.3.3.3",
    "p1": "11.11.11.11",
    "p2": "22.22.22.22",
    "p3": "33.33.33.33",
    "p4": "44.44.44.44",
}

FRR_LDP_INTERFACES: Dict[str, List[str]] = {
    "pe1": ["pe1-eth1", "pe1-eth2"],
    "pe2": ["pe2-eth1", "pe2-eth2"],
    "pe3": ["pe3-eth1", "pe3-eth2"],
    "p1": ["p1-eth0", "p1-eth1"],
    "p2": ["p2-eth0", "p2-eth1"],
    "p3": ["p3-eth0", "p3-eth1"],
    "p4": ["p4-eth0", "p4-eth1"],
}

FRR_VPLS_NEIGHBORS: Dict[str, List[Tuple[str, str]]] = {
    "pe1": [("mpw-pe2", FRR_ROUTER_IDS["pe2"]), ("mpw-pe3", FRR_ROUTER_IDS["pe3"])],
    "pe2": [("mpw-pe1", FRR_ROUTER_IDS["pe1"]), ("mpw-pe3", FRR_ROUTER_IDS["pe3"])],
    "pe3": [("mpw-pe1", FRR_ROUTER_IDS["pe1"]), ("mpw-pe2", FRR_ROUTER_IDS["pe2"])],
}

LINUX_VPLS_PSEUDOWIRES: Dict[str, List[Tuple[str, str]]] = {
    "pe1": [("pe2", FRR_ROUTER_IDS["pe2"]), ("pe3", FRR_ROUTER_IDS["pe3"])],
    "pe2": [("pe1", FRR_ROUTER_IDS["pe1"]), ("pe3", FRR_ROUTER_IDS["pe3"])],
    "pe3": [("pe1", FRR_ROUTER_IDS["pe1"]), ("pe2", FRR_ROUTER_IDS["pe2"])],
}


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
        run(host, f"ip link set {intf} mtu {VPLS_SERVICE_MTU}")
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
    for module in ("mpls_router", "mpls_iptunnel", "mpls_gso", "ip_gre"):
        result = subprocess.run(["modprobe", module], text=True, capture_output=True)
        if result.returncode != 0 and module not in {"mpls_gso", "ip_gre"}:
            message = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"Khong load duoc kernel module {module}: {message}")


def configure_mpls_sysctl(net) -> None:
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        run(router, "sysctl -w net.mpls.platform_labels=100000")
        for intf in ROUTER_INTERFACES[router_name]:
            run(router, f"sysctl -w net.mpls.conf.{intf}.input=1")


def configure_vpls_customer_edges(net) -> None:
    for ce_name, (intf, ip_addr) in VPLS_CE_WAN.items():
        ce = net.get(ce_name)
        run(ce, f"ip addr flush dev {intf}")
        run(ce, f"ip addr add {ip_addr} dev {intf}")
        run(ce, f"ip link set {intf} mtu {VPLS_SERVICE_MTU}")
        run(ce, f"ip link set {intf} up")
        for network, gateway in VPLS_CE_ROUTES[ce_name]:
            run(ce, f"ip route replace {network} via {gateway} dev {intf}")

    for pe_name, access_intf in FRR_VPLS_ACCESS_INTERFACES.items():
        pe = net.get(pe_name)
        run(pe, f"ip addr flush dev {access_intf}")
        run(pe, f"ip link set {access_intf} mtu {VPLS_SERVICE_MTU}")
        run(pe, f"ip link set {access_intf} up")
        run(pe, f"ip link set {access_intf} promisc on")


def ensure_frr_support() -> None:
    required = ["zebra", "ospfd", "ldpd"]
    missing = [name for name in required if not (FRR_DAEMON_DIR / name).exists()]
    if missing:
        raise RuntimeError(
            "Thieu FRRouting daemon: "
            + ", ".join(missing)
            + ". Hay cai goi frr truoc khi chay mode MPLS voi OSPF/LDP."
        )


def frr_paths(router_name: str) -> Dict[str, Path]:
    base = FRR_DIR / router_name
    return {
        "base": base,
        "vty": base / "vty",
        "conf": base / "frr.conf",
        "zebra_sock": base / "zebra.sock",
        "ldp_ctl": base / "ldpctl",
        "zebra_pid": base / "zebra.pid",
        "ospfd_pid": base / "ospfd.pid",
        "ldpd_pid": base / "ldpd.pid",
        "zebra_log": base / "zebra.log",
        "ospfd_log": base / "ospfd.log",
        "ldpd_log": base / "ldpd.log",
    }


def provider_network_config(router_name: str) -> str:
    router_id = FRR_ROUTER_IDS[router_name]
    lines = [
        "frr version 8.4",
        "frr defaults traditional",
        f"hostname {router_name}",
        "password zebra",
        "service integrated-vtysh-config",
        f"ip router-id {router_id}",
        "!",
    ]
    for intf in FRR_LDP_INTERFACES[router_name]:
        lines.extend(
            [
                f"interface {intf}",
                " ip ospf network point-to-point",
                " ip ospf hello-interval 1",
                " ip ospf dead-interval 4",
                " mpls enable",
                "!",
            ]
        )

    lines.extend(
        [
        "router ospf",
        f" ospf router-id {router_id}",
        f" network {router_id}/32 area 0",
        " network 172.20.0.0/16 area 0",
        " mpls ldp-sync",
        "!",
        "mpls ldp",
        f" router-id {router_id}",
        " !",
        " address-family ipv4",
        f"  discovery transport-address {router_id}",
        ]
    )
    for intf in FRR_LDP_INTERFACES[router_name]:
        lines.extend([f"  interface {intf}", "  !"])
    lines.extend([" exit-address-family", "!", "line vty", "!"])

    if router_name in FRR_VPLS_NEIGHBORS:
        access_intf = FRR_VPLS_ACCESS_INTERFACES[router_name]
        lines.extend(
            [
                "l2vpn BRANCH-MAN type vpls",
                f" bridge br-{router_name}",
                f" member interface {access_intf}",
                " !",
            ]
        )
        for pseudowire, neighbor_id in FRR_VPLS_NEIGHBORS[router_name]:
            lines.extend(
                [
                    f" member pseudowire {pseudowire}",
                    f"  neighbor lsr-id {neighbor_id}",
                    "  pw-id 100",
                    " !",
                ]
            )
        lines.append("!")
    return "\n".join(lines) + "\n"


def prepare_frr_files(net) -> None:
    FRR_DIR.mkdir(parents=True, exist_ok=True)
    FRR_DIR.chmod(0o777)
    for router_name in PROVIDER_ROUTERS:
        paths = frr_paths(router_name)
        paths["base"].mkdir(parents=True, exist_ok=True)
        paths["vty"].mkdir(parents=True, exist_ok=True)
        paths["ldp_ctl"].mkdir(parents=True, exist_ok=True)
        paths["base"].chmod(0o777)
        paths["vty"].chmod(0o777)
        paths["ldp_ctl"].chmod(0o777)
        paths["conf"].write_text(provider_network_config(router_name), encoding="utf-8")
        paths["conf"].chmod(0o644)

        router = net.get(router_name)
        router_id = FRR_ROUTER_IDS[router_name]
        run(router, f"ip addr replace {router_id}/32 dev lo")
        run(router, "ip link set lo up")

        if router_name in FRR_VPLS_NEIGHBORS:
            access_intf = FRR_VPLS_ACCESS_INTERFACES[router_name]
            run(router, f"ip link add br-{router_name} type bridge 2>/dev/null || true")
            run(router, f"ip addr flush dev {access_intf}")
            run(router, f"ip link set {access_intf} master br-{router_name} 2>/dev/null || true")
            run(router, f"ip link set br-{router_name} up")
            run(router, f"ip link set {access_intf} mtu {VPLS_SERVICE_MTU}")
            run(router, f"ip link set {access_intf} up")
            run(router, f"ip link set {access_intf} promisc on")


def configure_linux_vpls_pseudowires(net) -> None:
    for router_name, peers in LINUX_VPLS_PSEUDOWIRES.items():
        router = net.get(router_name)
        bridge = f"br-{router_name}"
        local_id = FRR_ROUTER_IDS[router_name]
        for peer_name, neighbor_id in peers:
            tunnel = f"gt-{peer_name}"
            run(router, f"ip link del {tunnel} 2>/dev/null || true")
            run(
                router,
                f"ip link add {tunnel} type gretap local {local_id} remote {neighbor_id} key 100 ttl 64",
            )
            run(router, f"ip link set {tunnel} mtu {VPLS_SERVICE_MTU}")
            run(router, f"ip link set {tunnel} master {bridge}")
            run(router, f"bridge link set dev {tunnel} isolated on 2>/dev/null || true")
            run(router, f"ip link set {tunnel} up")
            run(router, f"ip link set {tunnel} promisc on")


def start_frr_daemons(net) -> None:
    ensure_frr_support()
    prepare_frr_files(net)
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        paths = frr_paths(router_name)
        run(router, f"pkill -f '/usr/lib/frr/(zebra|ospfd|ldpd).*metro_ethernet_mpls_frr/{router_name}' 2>/dev/null || true")
        common = f"-f {paths['conf']} --vty_socket {paths['vty']} -A 127.0.0.1"
        run(
            router,
            f"{FRR_DAEMON_DIR / 'zebra'} -d {common} "
            f"-i {paths['zebra_pid']} -z {paths['zebra_sock']} "
            f"--log file:{paths['zebra_log']}",
        )
        run(
            router,
            f"{FRR_DAEMON_DIR / 'ospfd'} -d {common} "
            f"-i {paths['ospfd_pid']} -z {paths['zebra_sock']} "
            f"--log file:{paths['ospfd_log']}",
        )
        run(
            router,
            f"{FRR_DAEMON_DIR / 'ldpd'} -d {common} "
            f"-i {paths['ldpd_pid']} -z {paths['zebra_sock']} "
            f"--ctl_socket {paths['ldp_ctl']} --log file:{paths['ldpd_log']}",
        )
    configure_linux_vpls_pseudowires(net)


def stop_frr_daemons(net) -> None:
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        for daemon in ("zebra", "ospfd", "ldpd"):
            run(router, f"pkill -f '/usr/lib/frr/{daemon}.*metro_ethernet_mpls_frr/{router_name}' 2>/dev/null || true")


def vtysh(router, router_name: str, command: str) -> str:
    paths = frr_paths(router_name)
    return run(router, f"vtysh --vty_socket {paths['vty']} -c \"{command}\" 2>&1")


def collect_frr_state(net) -> str:
    sections = []
    for router_name in PROVIDER_ROUTERS:
        router = net.get(router_name)
        sections.append(f"===== {router_name}: show ip ospf neighbor =====\n{vtysh(router, router_name, 'show ip ospf neighbor')}")
        sections.append(f"===== {router_name}: show ip route ospf =====\n{vtysh(router, router_name, 'show ip route ospf')}")
        sections.append(f"===== {router_name}: show mpls ldp neighbor =====\n{vtysh(router, router_name, 'show mpls ldp neighbor')}")
        sections.append(f"===== {router_name}: show mpls ldp ipv4 binding =====\n{vtysh(router, router_name, 'show mpls ldp ipv4 binding')}")
        sections.append(f"===== {router_name}: show mpls table =====\n{vtysh(router, router_name, 'show mpls table')}")
        if router_name in FRR_VPLS_NEIGHBORS:
            sections.append(f"===== {router_name}: show running-config l2vpn =====\n{vtysh(router, router_name, 'show running-config')}")
            bridge_output = run(router, f"bridge link show master br-{router_name}")
            gretap_output = run(router, "ip -d link show type gretap")
            sections.append(f"===== {router_name}: linux bridge vpls data-plane =====\n{bridge_output}")
            sections.append(f"===== {router_name}: linux gretap pseudowires =====\n{gretap_output}")
    return "\n".join(sections)


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
        configure_vpls_customer_edges(net)
        start_frr_daemons(net)
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
