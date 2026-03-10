"""
风控监控器基类
"""
from typing import Optional
from datetime import datetime
from yxquant.utils.logger import get_logger
from yxquant.profiles.common import RunningMode

logger = get_logger('live')


class BaseRiskMonitor:
    """
    风控监控器基类
    """
    
    def __init__(self):
        """初始化监控器"""
        self.cerebro = None
        self.strategy = None
        self.broker = None
        self._trading_forbidden = False
        self._forbidden_date: Optional[datetime] = None
        
    def setenvironment(self, cerebro, strategy):
        self.cerebro = cerebro
        self.strategy = strategy
        self.broker = cerebro.broker
        
    @property
    def is_live(self):
        """是否为实盘模式"""
        return getattr(self.cerebro.p, 'running_mode', None) == RunningMode.LIVE
    
    @property
    def is_backtest(self):
        """是否为回测模式"""
        return getattr(self.cerebro.p, 'running_mode', None) == RunningMode.BACKTEST
    
    @property
    def is_opt(self):
        """是否为优化模式"""
        return getattr(self.cerebro.p, 'running_mode', None) == RunningMode.OPT
    
    @property
    def _time(self):
        """获取当前时间"""
        if self.strategy is not None and hasattr(self.strategy, '_time'):
            return self.strategy._time
        elif self.strategy is not None and hasattr(self.strategy, 'data'):
            return self.strategy.data.datetime.datetime()
        else:
            raise "No time available"
    
    def on_start(self):
        """
        监控器启动时调用（类似于策略的start方法）
        子类可以重写此方法
        """
        pass
    
    def on_stop(self):
        """
        监控器停止时调用（类似于策略的stop方法）
        子类可以重写此方法
        """
        pass
    
    def on_data(self):
        """
        每次数据更新时调用（类似于策略的next方法）
        子类必须重写此方法来实现具体的风控逻辑
        """
        pass
    
    def on_order(self, order):
        """
        订单状态更新时调用
        
        Args:
            order: 订单对象
        """
        pass
    
    def on_trade(self, trade):
        """
        交易完成时调用
        
        Args:
            trade: 交易对象
        """
        pass
    
    def forbid_trading(self, reason: str = ""):
        """
        禁止交易
        
        Args:
            reason: 禁止交易的原因
        """
        current_date = self._time.date() if isinstance(self._time, datetime) else self._time.date()
        self._trading_forbidden = True
        self._forbidden_date = current_date
        logger.critical(f"🚨 {self.__class__.__name__}: 禁止交易 - {reason}")
    
    def allow_trading(self):
        """允许交易"""
        self._trading_forbidden = False
        self._forbidden_date = None
        logger.info(f"{self.__class__.__name__}: 允许交易")
    
    def is_trading_forbidden(self) -> bool:
        """
        检查当前是否禁止交易
        
        Returns:
            bool: 如果禁止交易返回True
        """
        # 如果是新的一天，重置禁止交易标志
        if self._forbidden_date is not None:
            current_date = self._time.date() if isinstance(self._time, datetime) else self._time.date()
            if isinstance(self._forbidden_date, datetime):
                forbidden_date = self._forbidden_date.date()
            else:
                forbidden_date = self._forbidden_date
                
            if forbidden_date != current_date:
                self._trading_forbidden = False
                self._forbidden_date = None
        
        return self._trading_forbidden
    
    def close_all_positions(self):
        """
        平仓所有持仓
        子类可以重写此方法来实现特定的平仓逻辑
        """
        if self.is_live:
            # 实盘模式：使用broker的close_all方法
            if hasattr(self.broker, 'close_all'):
                self.broker.close_all()
                logger.critical(f"{self.__class__.__name__}: 已通过broker平仓所有持仓")
            else:
                logger.critical(f"{self.__class__.__name__}: Broker没有close_all方法")
        else:
            # 回测/优化模式：通过策略的close_all方法
            if self.strategy and hasattr(self.strategy, 'close_all'):
                try:
                    self.strategy.close_all()
                    logger.critical(f"{self.__class__.__name__}: 已通过策略平仓所有持仓")
                except Exception as e:
                    logger.critical(f"{self.__class__.__name__}: 策略平仓失败: {e}", exc_info=True)
            else:
                logger.critical(f"{self.__class__.__name__}: 策略没有close_all方法")
    
    def get_status(self) -> dict:
        """
        获取监控器状态
        
        Returns:
            dict: 状态信息
        """
        return {
            'name': self.__class__.__name__,
            'trading_forbidden': self._trading_forbidden,
            'forbidden_date': str(self._forbidden_date) if self._forbidden_date else None,
        }

