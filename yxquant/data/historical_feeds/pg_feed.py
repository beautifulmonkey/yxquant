# -*- coding: utf-8 -*-
import pandas as pd
import backtrader as bt
from peewee import PostgresqlDatabase
from typing import Optional

from ..resampler import resample_ohlcv


class PGDBData:
    """
    PostgreSQL data loader using peewee.
    Table format required: date, open, close, high, low, volume.
    """

    @staticmethod
    def load(
        database: str,
        table: str,
        password: str,
        host: str = 'localhost',
        port: int = 5432,
        user: str = 'postgres',
        datetime_column: str = 'date',
        start: Optional[str] = None,
        end: Optional[str] = None,
        timedelta: Optional[pd.Timedelta] = None,
        resample_timeframe: Optional[str] = None,
        **kwargs,
    ):
        db = PostgresqlDatabase(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
            **kwargs,
        )
        db.connect()

        query = f'SELECT * FROM "{table}"'
        params = []
        conditions = []

        if start:
            start_dt = pd.to_datetime(start)
            conditions.append(f'"{datetime_column}" >= %s')
            params.append(start_dt)

        if end:
            end_dt = pd.to_datetime(end)
            conditions.append(f'"{datetime_column}" <= %s')
            params.append(end_dt)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += f' ORDER BY "{datetime_column}"'

        if params:
            df = pd.read_sql(
                query, db.connection(), params=params,
                parse_dates=[datetime_column], index_col=datetime_column,
            )
        else:
            df = pd.read_sql(
                query, db.connection(),
                parse_dates=[datetime_column], index_col=datetime_column,
            )

        db.close()

        if timedelta:
            df.index = df.index + timedelta

        if resample_timeframe:
            df = resample_ohlcv(df, resample_timeframe)

        return bt.feeds.PandasData(dataname=df)
