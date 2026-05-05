#!/usr/bin/env python3
"""Wrapper ve so do moi. Giu ten file cu de run_all.sh khong doi."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from draw_network_topology import main


if __name__ == "__main__":
    main()
