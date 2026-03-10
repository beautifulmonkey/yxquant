# -*- coding: utf-8 -*-
"""Redis Pub/Sub 实时数据源。"""
import backtrader as bt
from yxquant.exceptions import LicenseError


class RedisPubSubLiveFeed(bt.feed.DataBase):
    """Backtrader live data feed driven by Redis Pub/Sub."""
    lines = ()
    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")