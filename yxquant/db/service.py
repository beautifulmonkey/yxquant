"""
数据服务类
提供交易记录和订单的CRUD操作
"""


from yxquant.exceptions import LicenseError

class OrderDataService:
    """订单数据服务类"""
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")


class TradingDataService:
    """交易数据服务类"""
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")

