# -*- coding: utf-8 -*-
"""
    Databento live data feed (https://databento.com/).
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class DatabentoLiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")
