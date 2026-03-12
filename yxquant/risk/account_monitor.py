# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant.exceptions import LicenseError


class AccountMonitor(BaseRiskMonitor):
    """账户风控监控"""

    def __init__(
        self,
        loss_threshold: float = 0.02,           # 当日亏损比例阈值，如 0.02 表示 2%
        loss_threshold_amount: Optional[float] = None,  # 当日亏损绝对金额阈值（与比例二选一或同时生效）
        daily_reset_hour: int = 0,               # 每日重置的小时（0-23）
        daily_reset_minute: int = 0,             # 每日重置的分钟
        close_all_on_trigger: bool = True,      # 触发时是否平掉全部持仓
        forbid_until_next_day: bool = True,      # 触发后是否禁止交易直至下一交易日
        shutdown_on_trigger: bool = False,       # 触发时是否紧急Shutdown
        **kwargs,
    ):
        raise LicenseError("当前开源版本暂不提供该功能")
