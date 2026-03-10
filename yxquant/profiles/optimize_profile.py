import backtrader as bt
from dataclasses import dataclass, field
from .common import DataFeed, Broker, BacktestMode, RunningMode
from typing import Optional, Sequence
from yxquant.analyzer import PnlAnalyzer
from yxquant.exporter import DistExporter
from yxquant.risk import RiskEngine, BaseRiskMonitor

@dataclass
class OptimizeProfile:
    """参数优化配置：在回测配置基础上用于多组参数批量回测，输出到指定路径。"""
    mode: BacktestMode
    stake: float
    data: Sequence[DataFeed]
    output_path: str
    broker: Optional[Broker] = None
    enable_cache: bool = True
    risk_monitors: list = field(default_factory=list)

    def attach(self, engine):
        engine.cerebro.p.running_mode = RunningMode.OPT
        engine.cerebro.p.enable_cache = self.enable_cache

        engine.add_sizer(bt.sizers.SizerFix, stake=self.stake)
        for d in self.data:
            engine.add_data(d.feed, name=d.name, need_load=d.need_load, params=d.params)

        b = engine.cerebro.getbroker()
        if self.broker:
            for comm in self.broker.commissions:
                b.setcommission(**comm.__dict__)
            if self.broker.cash is not None:
                b.setcash(self.broker.cash)
            if self.broker.slip_perc:
                engine.cerebro.broker.set_slippage_perc(perc=self.broker.slip_perc)
            if self.broker.coc:
                b.set_coc(self.broker.coc)

        # 初始化风控引擎
        risk_engine = RiskEngine(cerebro=engine.cerebro, alert=None)
        
        # 注册风控监控器
        if self.risk_monitors:
            for monitor_config in self.risk_monitors:
                monitor_cls, params = monitor_config
                risk_engine.add_monitor(monitor_cls, **params)
        
        # 将风控引擎存储到cerebro中，供策略访问
        engine.cerebro.p.risk_engine = risk_engine

        engine.add_analyzer(PnlAnalyzer, name='pnl_analysis')
        engine.add_exporter(DistExporter(output_path=self.output_path))

