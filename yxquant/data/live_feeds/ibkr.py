# -*- coding: utf-8 -*-
"""
    IBKR live data feed (https://www.interactivebrokers.com/).
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class IBLiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")
