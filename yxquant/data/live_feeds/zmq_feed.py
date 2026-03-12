# -*- coding: utf-8 -*-
import backtrader as bt
from yxquant.exceptions import LicenseError


class ZeroMQLiveFeed(bt.feed.DataBase):
    """Backtrader live data feed driven by ZeroMQ"""
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("当前开源版本暂不提供该功能")