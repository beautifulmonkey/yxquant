# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant.exceptions import LicenseError


class ExecutionMonitor(BaseRiskMonitor):
    """监控成交质量：滑点过大、成交价偏离信号价等，需专业版许可证。"""

    def __init__(
        self,
        max_slippage_pct: Optional[float] = None,           # 单笔最大滑点比例（成交价相对信号价）
        max_slippage_ticks: Optional[float] = None,           # 单笔最大滑点（tick 数，相对信号价）
        max_avg_slippage_pct: Optional[float] = None,         # 一段时间内平均滑点上限（如当日）
        consecutive_bad_fills: Optional[int] = None,        # 连续 N 笔劣质成交则触发
        warn_only: bool = False,                            # 仅告警不禁止交易（用于观察期）
        close_all_on_trigger: bool = True,                   # 触发时是否平掉全部持仓
        shutdown_on_trigger: bool = False,                  # 触发时是否退出进程
        **kwargs,
    ):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
