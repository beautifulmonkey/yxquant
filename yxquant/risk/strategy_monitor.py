# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant.exceptions import LicenseError


class StrategyMonitor(BaseRiskMonitor):
    """策略维度风控监控"""

    def __init__(
        self,
        max_drawdown_pct: Optional[float] = None,     # 最大回撤比例，超则禁止开仓或平仓
        max_consecutive_losses: Optional[int] = None, # 连续亏损笔数上限，超则暂停开仓
        max_open_trades: Optional[int] = None,       # 最大同时持仓笔数（或敞口数）
        max_daily_trades: Optional[int] = None,     # 单日最大成交笔数
        max_daily_loss_pct: Optional[float] = None,  # 单日亏损比例上限
        close_all_on_trigger: bool = True,          # 触发时是否平掉全部持仓
        shutdown_on_trigger: bool = False,          # 触发时是否紧急Shutdown
        **kwargs,
    ):
        raise LicenseError("当前开源版本暂不提供该功能")
