# -*- coding: utf-8 -*-
from typing import Optional
from .base import BaseRiskMonitor
from yxquant_os.exceptions import LicenseError


class HeartbeatMonitor(BaseRiskMonitor):
    """监控进程/连接心跳监控"""

    def __init__(
        self,
        timeout_seconds: float = 60.0,              # 心跳超时秒数，超时则执行 action_on_timeout
        check_interval_seconds: float = 5.0,       # 检查心跳的间隔秒数
        action_on_timeout: str = "forbid",         # 超时动作：forbid 仅禁止交易，close 平仓
        close_all_on_timeout: bool = False,       # 超时时是否平掉全部持仓
        shutdown_on_timeout: bool = False,        # 超时时是否退出进程
        heartbeat_key: Optional[str] = None,      # 外部心跳来源标识（如 Redis key）
        **kwargs,
    ):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
