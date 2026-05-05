# Bao cao LaTeX Metro Ethernet MPLS

Thu muc nay la ban bao cao LaTeX theo mau ban da them. Noi dung da duoc viet lai cho de tai:

```text
Thiet ke va trien khai mang Metro Ethernet su dung MPLS cho ket noi da chi nhanh doanh nghiep
```

## Build PDF

Neu may chua co LaTeX:

```bash
sudo apt update
sudo apt install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-lang-other texlive-fonts-recommended
```

Build:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

File dau ra:

```text
main.pdf
```

## Noi dung chinh

- `main.tex`: file dieu phoi bao cao.
- `preamble.tex`: cau hinh font, mau, ten de tai, sinh vien, GVHD.
- `chuongs/chuong1.tex`: gioi thieu.
- `chuongs/chuong2.tex`: co so ly thuyet Metro Ethernet/MPLS.
- `chuongs/chuong3.tex`: thiet ke topology.
- `chuongs/chuong4.tex`: trien khai, ket qua, doi chieu rubric.
- `chuongs/chuong5.tex`: ket luan, diem can noi ro khi bao ve va huong phat trien.
- `appendix.tex`: phu luc lenh demo va ma nguon chinh.
- `image/`: so do va bieu do copy tu project Mininet.

## Luu y doi chieu rubric

- Ban LaTeX nay da tach thanh 5 chuong lon de khop rubric cham diem.
- Phu luc da co lenh demo thu cong, lenh kiem tra MPLS va cleanup Mininet.
- Khi bao ve nen noi chinh xac: MPLS native that tren underlay, con data-plane VPLS/L2VPN trong Mininet dung GRETAP pseudowire tren underlay MPLS.
