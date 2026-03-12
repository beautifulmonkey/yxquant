# -*- coding: utf-8 -*-
"""
MBP-1：一档盘口（最优买卖价）。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MBP1:
    """Market By Price, 1 level：仅最优买一/卖一价与量。"""

    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
    ts: datetime
