# -*- coding: utf-8 -*-
"""
OHLCV 行情 schema。
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class OHLCV:
    """K 线 / 聚合 bar：开高低收量。"""

    open: float
    high: float
    low: float
    close: float
    volume: float
    ts: datetime
