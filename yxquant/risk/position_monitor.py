# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant.exceptions import LicenseError


class PositionMonitor(BaseRiskMonitor):
    """仓位风控监控。"""

    def __init__(
        self,
        max_position_size: Optional[float] = None,       # 总持仓数量上限（多+空合计）
        max_position_value: Optional[float] = None,     # 总持仓市值上限
        max_position_per_symbol: Optional[float] = None,  # 单品种持仓数量上限（不分多空）
        max_long_per_symbol: Optional[float] = None,     # 单品种多头持仓上限
        max_short_per_symbol: Optional[float] = None,    # 单品种空头持仓上限
        max_total_long: Optional[float] = None,          # 全品种多头总持仓上限
        max_total_short: Optional[float] = None,        # 全品种空头总持仓上限
        close_all_on_trigger: bool = True,              # 触发时是否平掉全部持仓
        shutdown_on_trigger: bool = False,              # 触发时是否紧急Shutdown
        **kwargs,
    ):
        raise LicenseError("当前开源版本暂不提供该功能")
