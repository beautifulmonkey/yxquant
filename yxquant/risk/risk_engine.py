"""
风控引擎 - 管理多个风控监控器
"""
from typing import List, Optional, Type, Dict, Any
import backtrader as bt
from yxquant.utils.logger import get_logger
from yxquant.profiles.common import RunningMode
from .base import BaseRiskMonitor

logger = get_logger('live')


class RiskEngine:
    """
    风控引擎，管理多个风控监控器
    用户可以注册多个监控器，每个监控器都有自己的params配置
    """
    def __init__(self, cerebro: bt.Cerebro, alert=None):
        self.cerebro = cerebro
        self.broker = cerebro.broker
        self.alert = alert
        
        self.monitors: List[BaseRiskMonitor] = []
        self.is_live = getattr(cerebro.p, 'running_mode', None) == RunningMode.LIVE
        logger.info(f"风控引擎初始化 ({'实盘' if self.is_live else '回测/优化'}模式)")
    
    def add_monitor(self, monitor_cls: Type[BaseRiskMonitor], **kwargs):
        try:
            monitor = monitor_cls(**kwargs)
            self.monitors.append(monitor)
            
            logger.info(
                f"风控引擎: 已添加监控器 {monitor_cls.__name__} "
                f"(参数: {kwargs})"
            )
            
        except Exception as e:
            logger.error(f"风控引擎: 添加监控器 {monitor_cls.__name__} 失败: {e}", exc_info=True)
    
    def set_strategy(self, strategy):
        for monitor in self.monitors:
            monitor.setenvironment(self.cerebro, strategy)
            monitor.on_start()
    
    def on_data(self):
        for monitor in self.monitors:
            try:
                monitor.on_data()
            except Exception as e:
                logger.error(
                    f"风控引擎: 监控器 {monitor.__class__.__name__} on_data 出错: {e}",
                    exc_info=True
                )
    
    def on_order(self, order):
        for monitor in self.monitors:
            try:
                monitor.on_order(order)
            except Exception as e:
                logger.error(
                    f"风控引擎: 监控器 {monitor.__class__.__name__} on_order 出错: {e}",
                    exc_info=True
                )
    
    def on_trade(self, trade):
        for monitor in self.monitors:
            try:
                monitor.on_trade(trade)
            except Exception as e:
                logger.error(
                    f"风控引擎: 监控器 {monitor.__class__.__name__} on_trade 出错: {e}",
                    exc_info=True
                )
    
    def on_stop(self):
        for monitor in self.monitors:
            try:
                monitor.on_stop()
            except Exception as e:
                logger.error(
                    f"风控引擎: 监控器 {monitor.__class__.__name__} on_stop 出错: {e}",
                    exc_info=True
                )
    
    def is_trading_allowed(self) -> bool:
        """
        检查是否允许交易
        
        Returns:
            bool: 如果所有监控器都允许交易返回True，否则返回False
        """
        for monitor in self.monitors:
            if monitor.is_trading_forbidden():
                return False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'monitors': [monitor.get_status() for monitor in self.monitors],
            'trading_allowed': self.is_trading_allowed(),
            'is_live': self.is_live
        }

