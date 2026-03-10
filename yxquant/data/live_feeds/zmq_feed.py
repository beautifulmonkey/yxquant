# -*- coding: utf-8 -*-
import backtrader as bt
from yxquant.exceptions import LicenseError


class ZeroMQLiveFeed(bt.feed.DataBase):
    """Backtrader live data feed driven by ZeroMQ"""
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")