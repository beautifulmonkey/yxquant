# -*- coding: utf-8 -*-
# Author: Chris Yang
import backtrader as bt
from yxquant.exceptions import LicenseError

class BinanceBroker(bt.BrokerBase):
    params = ()
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")
