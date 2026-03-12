# -*- coding: utf-8 -*-
"""逐笔成交 schema。"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """单笔成交：价格、数量、方向、时间。"""
    price: float
    size: float
    side: str  # "buy" / "sell" 或 "B" / "S"
    ts: datetime


@dataclass
class TBBO(Trade):
    """带成交时刻一档盘口的成交：在 Trade 基础上增加当时最优买卖价与量。"""

    bid_price: float   # 成交时刻买一价
    bid_size: float    # 成交时刻买一量
    ask_price: float   # 成交时刻卖一价
    ask_size: float    # 成交时刻卖一量
