"""
数据库模块 - 简洁版本
基于DatabaseProxy的简单实现
"""

from .models import database_proxy, Trade
from .connection import init_db, init_sqlite, init_postgresql
from .service import TradingDataService

__all__ = [
    'database_proxy', 'Trade', 'init_db', 'init_sqlite', 'init_postgresql',
    'TradingDataService'
]
