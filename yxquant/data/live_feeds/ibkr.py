# -*- coding: utf-8 -*-
"""
    IBKR live data feed (https://www.interactivebrokers.com/).
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class IBLiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
