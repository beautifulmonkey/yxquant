"""
    套利交易类
"""
from .base import BaseStrategy
from yxquant.exceptions import LicenseError

class ArbStrategyBase(BaseStrategy):
    def __init__(self, **kwargs):
        raise LicenseError("套利组件需要专业版许可证，请联系获取授权。")
