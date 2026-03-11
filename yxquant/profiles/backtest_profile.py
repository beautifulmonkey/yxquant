import backtrader as bt
from dataclasses import dataclass, field
from typing import Optional, Sequence
from .common import DataFeed, Broker, BacktestMode, RunningMode
from yxquant.analyzer import PnlAnalyzer
from yxquant.exporter import TradeRecordExporter, WebViewExporter, DataFeedsExporter, ArbSpreadDataFeedsExporter, IndicatorDataExporter, DistExporter
from yxquant.risk import RiskEngine, BaseRiskMonitor


@dataclass
class BacktestProfile:
    """回测配置：数据、资金、手续费、输出路径、分析器与导出器，挂载到引擎后用于纯回测运行。"""
    mode: BacktestMode
    data: Sequence[DataFeed]
    stake: float = 1
    output_path: str = "runs"
    broker: Optional[Broker] = None
    enable_cache: bool = True
    risk_monitors: list = field(default_factory=list)

    def attach(self, engine):
        engine.cerebro.p.running_mode = RunningMode.BACKTEST
        engine.cerebro.p.enable_cache = self.enable_cache
        engine.cerebro.p.output_path = self.output_path

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

        # 分析器
        engine.add_analyzer(PnlAnalyzer, name='pnl_analysis')

        # 导出器
        engine.add_exporter(DistExporter(output_path=self.output_path))
        engine.add_exporter(TradeRecordExporter(output_path=self.output_path, mode=self.mode))
        engine.add_exporter(WebViewExporter(output_path=self.output_path))
        engine.add_exporter(IndicatorDataExporter(output_path=self.output_path))

        if self.mode == BacktestMode.CTA:
            engine.add_exporter(DataFeedsExporter(output_path=self.output_path))
        elif self.mode == BacktestMode.ARB:
            engine.add_exporter(ArbSpreadDataFeedsExporter(output_path=self.output_path))


