# -*- coding: utf-8 -*-
"""
    Databento live data feed (https://databento.com/).
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class DatabentoLiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
