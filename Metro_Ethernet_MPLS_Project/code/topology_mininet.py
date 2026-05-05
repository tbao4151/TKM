#!/usr/bin/env python3
"""Topology Mininet cho Metro Ethernet ket noi 3 chi nhanh qua provider."""

from __future__ import annotations

import argparse
import os
import sys
import time

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.topo import Topo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from network_config import collect_mpls_state, configure_network, connectivity_checks


class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class MetroEthernetTopo(Topo):
    def build(self):
        # Branch 1: Flat Network - 2 access switch, 4 host.
        for host in ("host1", "host2", "host3", "host4"):
            self.addHost(host)
        self.addSwitch("b1_sw1", failMode="standalone")
        self.addSwitch("b1_sw2", failMode="standalone")
        self.addHost("b1_ce", cls=LinuxRouter)
        self.addLink("host1", "b1_sw1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("host2", "b1_sw1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("host3", "b1_sw2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("host4", "b1_sw2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b1_sw1", "b1_sw2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b1_sw1", "b1_ce", cls=TCLink, bw=100, delay="1ms")

        # Branch 2: Three-tier Network - Core/Distribution/Access.
        for host in ("admin1", "admin2", "user1", "user2", "guest1", "guest2"):
            self.addHost(host)
        for switch in ("b2_core1", "b2_core2", "b2_dist1", "b2_dist2", "b2_acc1", "b2_acc2", "b2_acc3"):
            self.addSwitch(switch, failMode="standalone")
        self.addHost("b2_ce", cls=LinuxRouter)
        self.addLink("admin1", "b2_acc1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("admin2", "b2_acc1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("user1", "b2_acc2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("user2", "b2_acc2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("guest1", "b2_acc3", cls=TCLink, bw=100, delay="1ms")
        self.addLink("guest2", "b2_acc3", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_acc1", "b2_dist1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_acc2", "b2_dist1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_acc3", "b2_dist2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_dist1", "b2_core1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_dist2", "b2_core1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_core1", "b2_core2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b2_core1", "b2_ce", cls=TCLink, bw=100, delay="1ms")

        # Branch 3: Leaf-Spine Network - loop-free lab variant for stable OVS startup.
        for host in ("svr1", "svr2", "svr3a", "svr3b", "svr4", "os1", "os2"):
            self.addHost(host)
        self.addSwitch("b3_leaf1", failMode="standalone")
        self.addSwitch("b3_leaf2", failMode="standalone")
        self.addSwitch("b3_leaf3", failMode="standalone")
        self.addSwitch("b3_leaf4", failMode="standalone")
        self.addSwitch("b3_spine1", failMode="standalone")
        self.addSwitch("b3_spine2", failMode="standalone")
        self.addHost("b3_ce", cls=LinuxRouter)
        self.addLink("svr1", "b3_leaf1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("svr2", "b3_leaf2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("svr3a", "b3_leaf2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("svr3b", "b3_leaf3", cls=TCLink, bw=100, delay="1ms")
        self.addLink("svr4", "b3_leaf3", cls=TCLink, bw=100, delay="1ms")
        self.addLink("os1", "b3_leaf4", cls=TCLink, bw=100, delay="1ms")
        self.addLink("os2", "b3_leaf4", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_leaf1", "b3_spine1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_leaf2", "b3_spine1", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_leaf3", "b3_spine2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_leaf4", "b3_spine2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_spine1", "b3_spine2", cls=TCLink, bw=100, delay="1ms")
        self.addLink("b3_spine1", "b3_ce", cls=TCLink, bw=100, delay="1ms")

        # Provider Backbone: 3 PE va 4 P router mesh theo so do mau.
        for router in ("pe1", "pe2", "pe3", "p1", "p2", "p3", "p4"):
            self.addHost(router, cls=LinuxRouter)
        self.addLink("b1_ce", "pe1", cls=TCLink, bw=80, delay="2ms")
        self.addLink("b2_ce", "pe2", cls=TCLink, bw=80, delay="2ms")
        self.addLink("b3_ce", "pe3", cls=TCLink, bw=80, delay="2ms")
        self.addLink("pe1", "p1", cls=TCLink, bw=60, delay="3ms")
        self.addLink("pe1", "p3", cls=TCLink, bw=60, delay="3ms")
        self.addLink("pe2", "p3", cls=TCLink, bw=60, delay="3ms")
        self.addLink("pe2", "p4", cls=TCLink, bw=60, delay="3ms")
        self.addLink("pe3", "p2", cls=TCLink, bw=60, delay="3ms")
        self.addLink("pe3", "p4", cls=TCLink, bw=60, delay="3ms")
        self.addLink("p1", "p2", cls=TCLink, bw=50, delay="4ms")


def build_network(auto_set_macs: bool = True) -> Mininet:
    topo = MetroEthernetTopo()
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=None,
        link=TCLink,
        autoSetMacs=auto_set_macs,
        waitConnected=False,
    )
    return net


def start_configured_network(mode: str = "mpls", stp_wait: int = 2) -> Mininet:
    net = build_network()
    net.start()
    configure_network(net, mode=mode)
    # Cho OVS STP hoi tu vi topology moi co cac link du phong L2.
    time.sleep(stp_wait)
    return net


def main() -> int:
    parser = argparse.ArgumentParser(description="Metro Ethernet native MPLS Mininet topology")
    parser.add_argument("--mode", choices=("ip", "mpls"), default="mpls", help="forwarding mode")
    parser.add_argument("--stp-wait", type=int, default=2, help="seconds to wait after OVS startup")
    parser.add_argument("--test-mode", action="store_true", help="start topology, run connectivity checks, stop")
    args = parser.parse_args()

    setLogLevel("info")
    net = None
    try:
        net = start_configured_network(mode=args.mode, stp_wait=args.stp_wait)
        if args.test_mode:
            info("*** Connectivity checks\n")
            failed = False
            for src, dst, ok, output in connectivity_checks(net):
                status = "OK" if ok else "FAIL"
                info(f"{src} -> {dst}: {status}\n")
                if not ok:
                    info(output + "\n")
                    failed = True
            if args.mode == "mpls":
                info("*** MPLS kernel routes\n")
                info(collect_mpls_state(net) + "\n")
            return 1 if failed else 0

        info(f"*** Topology ready in {args.mode} mode. Use Mininet CLI for demo.\n")
        info("*** Example: host1 ping -c 3 10.2.0.11\n")
        CLI(net)
        return 0
    finally:
        if net is not None:
            net.stop()


if __name__ == "__main__":
    raise SystemExit(main())
