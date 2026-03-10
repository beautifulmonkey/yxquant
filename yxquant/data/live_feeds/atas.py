# -*- coding: utf-8 -*-
"""
    ATAS live data feed (https://atas.net/).
    Based on https://github.com/huangchiyuan/ATAS-market-data-storage.
"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class AtasLiveFeed(bt.feed.DataBase):
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
