# yx_quant/engine.py
from __future__ import annotations
import backtrader as bt
from pathlib import Path
from typing import Dict, Any, Type, Union, Callable, Optional, List

class RunContext:
    """记录一次运行的输出路径、统计、对象引用等"""
    def __init__(self, out_dir: Path):
        self.paths = {"root": str(out_dir)}
        self.stats: Dict[str, Any] = {}
        self.objects: Dict[str, Any] = {}  # analyzers/feeds 等句柄

class CoreEngine:
    """
    单次运行引擎：不关心“回测/实盘”，只提供挂数据/券商/分析器/策略并 run 的能力。
    具体如何挂数据与 broker 由 run_profile 决定。
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cerebro = bt.Cerebro()
        self.ctx = RunContext(out_dir=Path(self.config.get("out_dir", "runs/_dev")))

    # —— 可选便捷：给“用法 C”直接加数据 —— #
    def add_data(self, feed_cls: Type, name: str, params: Dict[str, Any]):
        feed = feed_cls.load(**params)
        self.cerebro.adddata(feed)
        return feed

    def add_analyzers(self):
        for acfg in self.config.get("analyzers", []):
            cls = load_object(acfg["cls"]) if isinstance(acfg["cls"], str) else acfg["cls"]
            a = self.cerebro.addanalyzer(cls, **acfg.get("params", {}))
            self.ctx.objects.setdefault("analyzers", []).append(a)

    # def configure_broker(self):
    #     broker = self.cerebro.getbroker()
    #     bc = self.config.get("broker", {})
    #     if "commission" in bc:
    #         broker.setcommission(commission=bc["commission"])
    #     # 这里也可设置滑点、保证金、成交撮合规则等
    #     return broker

    def add_strategy(self, strategy, **kwargs):
        self.cerebro.addstrategy(strategy, **kwargs)

    def attach(self, profile_or_type, **kwargs):
        # 允许传类或实例
        profile = profile_or_type(**kwargs) if isinstance(profile_or_type, type) else profile_or_type
        profile.attach(self)
        self._profile = profile
        return self

    def run(self):
        results = self.cerebro.run()
        return results, self.ctx
