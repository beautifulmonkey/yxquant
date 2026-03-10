"""
日志配置模块
支持回测和实盘不同的日志配置
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class TradingLogger:
    """交易日志管理器"""
    
    def __init__(self, mode='live', log_level=logging.INFO):
        self.mode = mode
        self.log_level = log_level
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志器"""
        logger = logging.getLogger(f'trading_{self.mode}')
        logger.setLevel(self.log_level)
        
        # 避免重复添加handler
        if logger.handlers:
            return logger
        
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        _date = datetime.now().strftime('%Y%m%d')
        
        # 格式化器
        if self.mode == 'backtest':
            formatter = logging.Formatter(
                '%(asctime)s [BACKTEST] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # live
            formatter = logging.Formatter(
                '%(asctime)s [LIVE] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # 为不同级别创建不同的文件处理器
        level_handlers = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        for level_name, level_value in level_handlers.items():
            if self.log_level <= level_value:  # 只创建需要的级别处理器
                log_file = log_dir / f'{self.mode}_{level_name.lower()}_{_date}.log'
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(level_value)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        # 控制台处理器（显示所有级别）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger

    def debug(self, message, exc_info=None):
        """调试日志"""
        self.logger.debug(message, exc_info=exc_info)
    
    def info(self, message, exc_info=None):
        """信息日志"""
        self.logger.info(message, exc_info=exc_info)
    
    def warning(self, message, exc_info=None):
        """警告日志"""
        self.logger.warning(message, exc_info=exc_info)
    
    def error(self, message, exc_info=None):
        """错误日志"""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=None):
        """夺命日志"""
        self.logger.critical(message, exc_info=exc_info)
    
    def liquidity_risk(self, spread_info):
        """流动性风险日志 - WARNING级别"""
        self.warning(f"流动性风险检测 - {spread_info}")
    
    def strategy_execution(self, spread, spot_price, future_price, bb_info):
        """策略执行日志 - DEBUG级别（高频信息）"""
        self.debug(f"策略执行 - 价差: {spread:.4f}, 现货价格: {spot_price:.4f}, 期货价格: {future_price:.4f}, 布林线: {bb_info}")
    
    def entry_signal(self, entry_type, spread, spot_price, future_price, bb_info, reason):
        """入场信号日志 - INFO级别"""
        self.info(f"入场信号 [{entry_type}] - 价差: {spread:.4f}, 现货: {spot_price:.4f}, 期货: {future_price:.4f}, 布林线: {bb_info}, 原因: {reason}")
    
    def exit_signal(self, exit_type, spread, spot_price, future_price, entry_spread, pnl):
        """出场信号日志 - INFO级别"""
        self.info(f"出场信号 [{exit_type}] - 当前价差: {spread:.4f}, 入场价差: {entry_spread:.4f}, 现货: {spot_price:.4f}, 期货: {future_price:.4f}, 盈亏: {pnl:.4f}")
    
    def trade_execution(self, action, symbol, price, size, trade_id):
        """交易执行日志 - INFO级别"""
        self.info(f"交易执行 - {action} {symbol} 价格: {price:.4f} 数量: {size} 交易ID: {trade_id}")
    
    def position_update(self, spot_size, future_size, total_value):
        """持仓更新日志 - INFO级别"""
        self.info(f"持仓更新 - 现货: {spot_size}, 期货: {future_size}, 总价值: {total_value:.2f}")
    
    def system_error(self, error_msg, exception=None, exc_info=None):
        """系统错误日志 - ERROR级别"""
        if exception:
            self.error(f"系统错误 - {error_msg}: {str(exception)}", exc_info=exc_info or exception)
        else:
            self.error(f"系统错误 - {error_msg}", exc_info=exc_info)
    
    def critical_error(self, error_msg, exception=None, exc_info=None):
        """严重错误日志 - CRITICAL级别"""
        if exception:
            self.critical(f"严重错误 - {error_msg}: {str(exception)}", exc_info=exc_info or exception)
        else:
            self.critical(f"严重错误 - {error_msg}", exc_info=exc_info)
    
    def performance_info(self, metric_name, value, unit=""):
        """性能指标日志 - INFO级别"""
        self.info(f"性能指标 - {metric_name}: {value} {unit}")
    
    def market_data(self, symbol, price, volume, timestamp=None):
        """市场数据日志 - DEBUG级别"""
        ts_str = f"时间: {timestamp}, " if timestamp else ""
        self.debug(f"市场数据 - {symbol} 价格: {price}, 成交量: {volume}, {ts_str}")


def get_logger(mode='live', log_level=logging.INFO):
    """获取日志器实例"""
    return TradingLogger(mode, log_level)