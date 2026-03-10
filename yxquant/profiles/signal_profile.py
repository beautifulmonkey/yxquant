from dataclasses import dataclass, field
from typing import Sequence, Union, Optional
import backtrader as bt
from .common import DataFeed, BacktestMode, RunningMode, Broker
from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase
from yxquant.risk import setup_exception_handler, RiskEngine, BaseRiskMonitor
from yxquant.utils.alerts import DiscordAlert, DingTalkAlert


@dataclass
class SignalProfile:
    """信号模式配置：只发信号不实盘下单，数据与风控同实盘，结果落库。"""
    mode: BacktestMode
    stake: float
    data: Sequence[DataFeed]
    db: Union[MySQLDatabase, PostgresqlDatabase, SqliteDatabase]
    broker: Broker
    alert: Union[DiscordAlert, DingTalkAlert] = None
    risk_monitors: list = field(default_factory=list)

    def attach(self, engine):
        engine.cerebro.p.running_mode = RunningMode.LIVE
        engine.add_sizer(bt.sizers.SizerFix, stake=self.stake)

        for d in self.data:
            engine.add_data(d.feed, name=d.name, params=d.params, need_load=d.need_load)

        b = engine.cerebro.getbroker()
        b.setcash(self.broker.cash)

        setup_exception_handler(engine.cerebro, self.alert)

        # 初始化风控引擎
        risk_engine = RiskEngine(cerebro=engine.cerebro, alert=self.alert)

        # 注册风控监控器
        if self.risk_monitors:
            for monitor_config in self.risk_monitors:
                monitor_cls, params = monitor_config
                risk_engine.add_monitor(monitor_cls, **params)

        # 将风控引擎存储到cerebro中，供策略访问
        engine.cerebro.p.risk_engine = risk_engine
