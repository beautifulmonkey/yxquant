# -*- coding: utf-8 -*-
"""
    MT4/MT5 live data feed
    based on https://github.com/dingmaotu/mql-zmq.
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class MT5LiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
