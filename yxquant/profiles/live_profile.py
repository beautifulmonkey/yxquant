from dataclasses import dataclass, field
from typing import Sequence, Union, Any
import backtrader as bt
from .common import DataFeed, BacktestMode, RunningMode
from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase
from yxquant.utils.alerts import DiscordAlert, DingTalkAlert
from yxquant.exceptions import LicenseError


@dataclass
class LiveProfile:
    """实盘配置：数据、券商、数据库、报警与风控，需专业版许可证。"""
    mode: BacktestMode
    data: Sequence[DataFeed]
    broker: bt.BrokerBase
    db: Union[MySQLDatabase, PostgresqlDatabase, SqliteDatabase]
    stake: float = 1
    alert: Union[DiscordAlert, DingTalkAlert] = None
    risk_monitors: list = field(default_factory=list)

    def attach(self, engine):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
