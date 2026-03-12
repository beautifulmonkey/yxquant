# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant.exceptions import LicenseError


class MarginMonitor(BaseRiskMonitor):
    """监控保证金占用与强平风控监控"""

    def __init__(
        self,
        margin_usage_warning_pct: Optional[float] = None,   # 保证金使用率告警线（如 0.8 表示 80%）
        margin_usage_critical_pct: Optional[float] = None, # 保证金使用率危险线，超则平仓/禁止开仓
        min_available_balance: Optional[float] = None,      # 可用资金下限，低于则触发风控
        close_all_on_trigger: bool = True,                 # 触发时是否平掉全部持仓
        forbid_on_warning: bool = False,                   # 仅达告警线时是否也禁止新开仓
        shutdown_on_trigger: bool = False,                 # 触发时是否紧急Shutdown
        **kwargs,
    ):
        raise LicenseError("当前开源版本暂不提供该功能")
