# -*- coding: utf-8 -*-
import pandas as pd
import backtrader as bt
from typing import Optional

from ..resampler import resample_ohlcv


class CSVData:
    """
    CSV data loader.
    CSV format required: date, open, close, high, low, volume.
    """

    @staticmethod
    def load(
        path: str,
        timedelta: pd.Timedelta = None,
        start: str = None,
        end: str = None,
        resample_timeframe: Optional[str] = None,
    ):
        df = pd.read_csv(path, parse_dates=[0], index_col=0)

        if timedelta:
            df.index = df.index + timedelta

        if start:
            start = pd.to_datetime(start)
            df = df[df.index >= start]

        if end:
            end = pd.to_datetime(end)
            df = df[df.index <= end]

        if resample_timeframe:
            df = resample_ohlcv(df, resample_timeframe)

        return bt.feeds.PandasData(dataname=df)
