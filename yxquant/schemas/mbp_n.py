# -*- coding: utf-8 -*-
"""
MBP-N：多档盘口（L2 深度）。
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import datetime


@dataclass
class MBPN:
    """
    Market By Price, N levels（L2 深度）：多档买卖盘。
    """

    bids: List[Tuple[float, float]]   # (price, size) per level
    asks: List[Tuple[float, float]]
    ts: datetime
    symbol: Optional[str] = None
