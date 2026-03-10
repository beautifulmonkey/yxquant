# -*- coding: utf-8 -*-
# Author: Chris Yang
import backtrader as bt
from yxquant.exceptions import LicenseError

class SierraChart(bt.BrokerBase):
    params = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
