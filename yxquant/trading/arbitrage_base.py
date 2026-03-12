"""
    套利交易类
"""
from .base import BaseStrategy
from yxquant.exceptions import LicenseError

class ArbStrategyBase(BaseStrategy):
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")
