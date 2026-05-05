#!/usr/bin/env python3
"""Ve so do Metro Ethernet/MPLS giong anh mau bang Matplotlib.

Chay:
    python3 draw_network_topology.py

Output chinh:
    output/so_do_tong_hop.png
    output/so_do_tong_hop.svg
    output/so_do_tong_hop.pdf
    output/chi_nhanh_1.png
    output/chi_nhanh_2.png
    output/chi_nhanh_3.png

Script chi dung Matplotlib va toa do thu cong de de chinh sua bo cuc.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
IMAGE_DIR = PROJECT_DIR / "images"
DPI = 300

BLUE = "#0874b8"
BLUE_DARK = "#0f4b76"
LINE = "#202427"
WAN = "#345773"
MPLS = "#ffe18a"
BRANCH1 = "#d8efff"
BRANCH2 = "#ffd8d8"
BRANCH3 = "#ddf2d7"

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["axes.unicode_minus"] = False


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def draw_link(ax, a: Tuple[float, float], b: Tuple[float, float], lw: float = 1.25, color: str = LINE, zorder: int = 3) -> None:
    """Ve cap noi giua hai thiet bi."""
    ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, solid_capstyle="round", zorder=zorder)


def draw_cloud(ax, x: float, y: float, w: float, h: float, label: str = "WAN / MPLS") -> None:
    """Ve vung cloud WAN bang cac ellipse ghep lai."""
    parts = [
        (x + 0.22 * w, y + 0.40 * h, 0.34 * w, 0.58 * h),
        (x + 0.42 * w, y + 0.62 * h, 0.42 * w, 0.70 * h),
        (x + 0.58 * w, y + 0.72 * h, 0.44 * w, 0.82 * h),
        (x + 0.78 * w, y + 0.42 * h, 0.34 * w, 0.55 * h),
        (x + 0.55 * w, y + 0.36 * h, 0.76 * w, 0.48 * h),
    ]
    for cx, cy, ew, eh in parts:
        ax.add_patch(Ellipse((cx, cy), ew, eh, facecolor=WAN, edgecolor="#1d2f42", lw=1.2, alpha=0.96, zorder=0))
    ax.text(x + 0.52 * w, y + 0.95 * h, label, color="white", fontsize=13, fontweight="bold", ha="center", zorder=1)


def draw_mpls_area(ax, x: float, y: float, w: float, h: float) -> None:
    """Ve vung MPLS mau vang nam trong cloud WAN."""
    ax.add_patch(Ellipse((x + w / 2, y + h / 2), w, h, facecolor=MPLS, edgecolor="#e5bd52", lw=1.1, alpha=0.95, zorder=1))
    ax.text(x + w / 2, y + h - 0.45, "VÙNG MPLS", fontsize=11, fontweight="bold", ha="center", zorder=2)


def draw_branch_box(ax, x: float, y: float, w: float, h: float, color: str, lines: Iterable[str]) -> None:
    """Ve khung nen cua tung chi nhanh."""
    ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#222", lw=1.0, alpha=0.88, zorder=0))
    for i, text in enumerate(lines):
        ax.text(x + 0.25, y + h - 0.35 - i * 0.45, text, fontsize=10.5, fontweight="bold" if i == 0 else "normal", va="top", zorder=8)


def draw_layer_line(ax, x1: float, x2: float, y: float, label: str) -> None:
    """Ve duong net dut phan lop trong chi nhanh."""
    ax.plot([x1, x2], [y, y], color="#333", lw=0.9, ls=(0, (2, 2)), zorder=2)
    ax.text(x1 + 0.05, y + 0.23, label, fontsize=9.5, va="bottom", zorder=8)


def draw_router(ax, x: float, y: float, label: str, r: float = 0.38) -> None:
    """Ve router kieu Cisco bang hinh tron xanh va mui ten trang."""
    ax.add_patch(Ellipse((x, y - 0.12), 1.45 * r, 0.34 * r, facecolor="#07558a", edgecolor="#053a5f", lw=0.8, zorder=6))
    ax.add_patch(Circle((x, y), r, facecolor=BLUE, edgecolor="white", lw=1.2, zorder=7))
    for dx, dy, sx, sy in [(-0.16, 0.08, -0.20, 0.10), (0.16, 0.08, 0.20, 0.10), (-0.14, -0.08, -0.20, -0.10), (0.14, -0.08, 0.20, -0.10)]:
        ax.arrow(x + dx, y + dy, sx, sy, head_width=0.07, head_length=0.08, fc="white", ec="white", lw=0.8, zorder=8, length_includes_head=True)
    ax.text(x, y - 0.64, label, ha="center", va="top", fontsize=9.2, zorder=9)


def draw_switch(ax, x: float, y: float, label: str, w: float = 1.15, h: float = 0.48) -> None:
    """Ve switch dang hop xanh co mat tren 3D nhe."""
    ax.add_patch(Polygon([(x - w / 2 + 0.16, y + h / 2), (x + w / 2 + 0.16, y + h / 2),
                          (x + w / 2, y + h / 2 + 0.22), (x - w / 2, y + h / 2 + 0.22)],
                         closed=True, facecolor="#1590d2", edgecolor="white", lw=0.8, zorder=6))
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, facecolor=BLUE, edgecolor="white", lw=1.0, zorder=7))
    for yy in (-0.10, 0.08):
        ax.arrow(x - 0.32, y + yy, 0.30, 0, head_width=0.05, head_length=0.08, fc="white", ec="white", lw=0.8, zorder=8)
        ax.arrow(x + 0.32, y + yy, -0.30, 0, head_width=0.05, head_length=0.08, fc="white", ec="white", lw=0.8, zorder=8)
    ax.text(x, y - 0.52, label, ha="center", va="top", fontsize=8.8, zorder=9)


def draw_pc(ax, x: float, y: float, label: str) -> None:
    """Ve icon may tinh/host."""
    ax.add_patch(Rectangle((x - 0.28, y), 0.56, 0.44, facecolor="#e7f6ff", edgecolor=BLUE, lw=1.4, zorder=7))
    ax.add_patch(Rectangle((x - 0.18, y + 0.08), 0.36, 0.26, facecolor="#248cc9", edgecolor="#095e95", lw=0.9, zorder=8))
    ax.add_patch(Rectangle((x - 0.07, y - 0.12), 0.14, 0.12, facecolor=BLUE, edgecolor=BLUE, zorder=7))
    ax.add_patch(Rectangle((x - 0.34, y - 0.22), 0.68, 0.10, facecolor=BLUE, edgecolor=BLUE, zorder=7))
    ax.text(x, y - 0.34, label, ha="center", va="top", fontsize=7.6, zorder=9)


def draw_server(ax, x: float, y: float, label: str) -> None:
    """Ve icon server dang tower."""
    ax.add_patch(FancyBboxPatch((x - 0.24, y - 0.02), 0.48, 0.88, boxstyle="round,pad=0.02,rounding_size=0.03",
                                facecolor="#eefbff", edgecolor=BLUE, lw=1.4, zorder=7))
    ax.add_patch(Circle((x, y + 0.48), 0.055, facecolor="#76c7ff", edgecolor=BLUE, lw=0.9, zorder=8))
    for yy in (0.14, 0.30, 0.68):
        ax.plot([x - 0.18, x + 0.18], [y + yy, y + yy], color=BLUE, lw=1.0, zorder=8)
    ax.text(x, y - 0.17, label, ha="center", va="top", fontsize=7.5, zorder=9)


P = {"P1": (13.2, 15.25), "P2": (17.15, 15.25), "P3": (13.2, 12.95), "P4": (17.15, 12.95)}
PE = {"PE1": (9.15, 12.85), "PE2": (14.6, 10.75), "PE3": (20.75, 12.85)}
CE = {"CE1": (5.75, 6.65), "CE2": (14.65, 6.65), "CE3": (23.0, 6.65)}


def draw_provider(ax) -> None:
    """Ve WAN/MPLS: cloud, vung MPLS, P router mesh va PE router."""
    draw_cloud(ax, 4.7, 9.25, 20.4, 8.15)
    draw_mpls_area(ax, 11.0, 11.45, 8.1, 5.15)
    for a, b in [("P1", "P2"), ("P1", "P3"), ("P2", "P4"), ("P3", "P4"), ("P1", "P4"), ("P2", "P3")]:
        draw_link(ax, P[a], P[b], lw=1.05)
    for a, b in [("PE1", "P1"), ("PE1", "P3"), ("PE2", "P3"), ("PE2", "P4"), ("PE3", "P2"), ("PE3", "P4")]:
        draw_link(ax, PE[a], P[b], lw=1.05)
    for name, pos in P.items():
        draw_router(ax, *pos, name, r=0.35)
    for name, pos in PE.items():
        ax.add_patch(Circle(pos, 1.52, facecolor="#fdeeff", edgecolor="none", alpha=0.78, zorder=1))
        draw_router(ax, *pos, name, r=0.35)


def draw_branch1(ax, include_uplink: bool = True) -> None:
    """Ve Chi nhanh 1 - mang phang."""
    draw_branch_box(ax, 0.25, 0.75, 8.05, 7.25, BRANCH1, ["CHI NHÁNH 1", "MẠNG PHẲNG"])
    sw1, sw2 = (4.65, 4.55), (6.95, 4.55)
    hosts = {"host1": (1.45, 2.20), "host2": (3.60, 2.20), "host3": (5.70, 2.20), "host4": (7.55, 2.20)}
    if include_uplink:
        draw_link(ax, CE["CE1"], PE["PE1"])
    draw_link(ax, CE["CE1"], sw1)
    draw_link(ax, sw1, sw2)
    for name in ("host1", "host2"):
        draw_link(ax, sw1, hosts[name])
    for name in ("host3", "host4"):
        draw_link(ax, sw2, hosts[name])
    draw_router(ax, *CE["CE1"], "CE1")
    draw_switch(ax, *sw1, "SW-1")
    draw_switch(ax, *sw2, "SW-2")
    for name, pos in hosts.items():
        draw_pc(ax, *pos, name)


def draw_branch2(ax, include_uplink: bool = True) -> None:
    """Ve Chi nhanh 2 - mang 3 lop Core/Distribution/Access."""
    draw_branch_box(ax, 8.55, 0.40, 11.80, 7.60, BRANCH2, ["CHI NHÁNH 2", "MẠNG 3 LỚP", "CORE-DISTRIBUTION-ACCESS"])
    draw_layer_line(ax, 8.65, 20.25, 5.28, "LỚP CORE")
    draw_layer_line(ax, 8.65, 20.25, 3.30, "LỚP\nDISTRIBUTION")
    draw_layer_line(ax, 8.65, 20.25, 1.82, "LỚP ACCESS")
    core = [(12.25, 5.55), (17.10, 5.55)]
    dist = [(12.25, 3.85), (17.10, 3.85)]
    acc = [(11.15, 2.40), (14.65, 2.40), (18.15, 2.40)]
    pcs = [("admin1", 9.85), ("admin2", 11.55), ("user1", 13.90), ("user2", 15.55), ("guest1", 17.25), ("guest2", 18.85)]
    if include_uplink:
        draw_link(ax, CE["CE2"], PE["PE2"])
    for c in core:
        draw_link(ax, CE["CE2"], c)
    for c in core:
        for d in dist:
            draw_link(ax, c, d)
    for d in dist:
        for a in acc:
            draw_link(ax, d, a)
    for idx, a in enumerate(acc):
        for name, x in pcs[idx * 2: idx * 2 + 2]:
            draw_link(ax, a, (x, 0.92))
    draw_router(ax, *CE["CE2"], "CE2")
    for i, pos in enumerate(core, 1):
        draw_switch(ax, *pos, f"Core{i}")
    for i, pos in enumerate(dist, 1):
        draw_switch(ax, *pos, f"Dist{i}")
    for i, pos in enumerate(acc, 1):
        draw_switch(ax, *pos, f"Access{i}")
    for name, x in pcs:
        draw_pc(ax, x, 0.92, name)


def draw_branch3(ax, include_uplink: bool = True) -> None:
    """Ve Chi nhanh 3 - mang Spine/Leaf."""
    draw_branch_box(ax, 20.60, 0.85, 9.05, 7.15, BRANCH3, ["CHI NHÁNH 3", "MẠNG 2 LỚP"])
    draw_layer_line(ax, 20.75, 29.50, 4.05, "SWITCH SPINE")
    draw_layer_line(ax, 20.75, 29.50, 2.92, "SWITCH LEAF")
    spines = [(24.45, 4.35), (27.55, 4.35)]
    leaves = [(23.10, 2.55), (25.00, 2.55), (27.05, 2.55), (29.00, 2.55)]
    endpoints = [("svr1", 22.75, leaves[0]), ("svr2", 24.15, leaves[1]), ("svr3", 25.30, leaves[1]),
                 ("svr3", 26.60, leaves[2]), ("svr4", 27.75, leaves[2]), ("os1", 28.70, leaves[3]), ("os2", 29.75, leaves[3])]
    if include_uplink:
        draw_link(ax, CE["CE3"], PE["PE3"])
    draw_link(ax, CE["CE3"], spines[0])
    for spine in spines:
        for leaf in leaves:
            draw_link(ax, spine, leaf)
    for _, x, leaf in endpoints:
        draw_link(ax, leaf, (x, 1.25))
    draw_router(ax, *CE["CE3"], "CE3")
    for i, pos in enumerate(spines, 1):
        draw_switch(ax, *pos, f"Spine{i}")
    for i, pos in enumerate(leaves, 1):
        draw_switch(ax, *pos, f"Leaf{i}")
    for name, x, _ in endpoints:
        draw_server(ax, x, 1.25, name)


def setup_canvas(ax, xlim=(0, 30), ylim=(0, 18)) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


def draw_full(ax) -> None:
    """Ve so do tong hop toan he thong."""
    setup_canvas(ax)
    draw_provider(ax)
    draw_branch1(ax)
    draw_branch2(ax)
    draw_branch3(ax)


def save_full() -> None:
    fig, ax = plt.subplots(figsize=(16, 9.6))
    draw_full(ax)
    fig.tight_layout(pad=0.2)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT_DIR / f"so_do_tong_hop.{ext}", dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_crop(filename: str, xlim, ylim) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    draw_full(ax)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    fig.savefig(OUTPUT_DIR / filename, dpi=DPI, facecolor="white")
    plt.close(fig)


def sync_for_existing_report() -> None:
    """Dong bo anh moi sang images/ de cac script bao cao cu dung duoc ngay."""
    mapping = {
        "so_do_tong_hop.png": "topology_overview.png",
        "chi_nhanh_1.png": "branch1_flat.png",
        "chi_nhanh_2.png": "branch2_three_tier.png",
        "chi_nhanh_3.png": "branch3_leaf_spine.png",
        "mpls_backbone.png": "mpls_backbone.png",
    }
    for src, dst in mapping.items():
        source = OUTPUT_DIR / src
        if source.exists():
            shutil.copy2(source, IMAGE_DIR / dst)


def main() -> None:
    ensure_dirs()
    save_full()
    save_crop("chi_nhanh_1.png", (0.1, 8.45), (0.55, 8.2))
    save_crop("chi_nhanh_2.png", (8.35, 20.55), (0.20, 8.25))
    save_crop("chi_nhanh_3.png", (20.35, 29.95), (0.65, 8.25))
    save_crop("mpls_backbone.png", (4.5, 25.3), (9.0, 17.7))
    sync_for_existing_report()
    print(f"Da xuat anh topology vao: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
