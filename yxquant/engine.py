from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Type, List
from .utils import FusionCerebro
from .exporter import OptExporter
import itertools
import gc
import copy
import math


class RunContext:
    """记录一次运行的输出路径、统计、对象引用等"""
    def __init__(self):
        self.stats: Dict[str, Any] = {}
        self.feeds: List[Any] = []
        self.strategies: List[Any] = []
        self.exporters: Dict[str, Any] = {}
        self.analyzers: List[Any] = []

        self.profile = None

class CoreEngine:
    """
        挂载数据与 broker 由 profile 决定
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cerebro = FusionCerebro()
        self.ctx = RunContext()

    def add_data(self, feed_cls: Type, name: str, params: Dict[str, Any], need_load: bool=False):
        feed = feed_cls.load(**params) if need_load else feed_cls(**params)
        self.cerebro.adddata(feed, name=name)
        self.ctx.feeds.append(feed)

    def add_analyzer(self, analyzer, name: str=None):
        self.cerebro.addanalyzer(analyzer, _name=name)
        self.ctx.analyzers.append(analyzer)

    def add_strategy(self, strategy, **kwargs):
        self.cerebro.addstrategy(strategy, **kwargs)
        self.ctx.strategies.append(strategy)

    def add_exporter(self, exporter):
        self.ctx.exporters[exporter.name] = exporter

    def add_sizer(self, sizer, stake=1):
        self.cerebro.addsizer(sizer, stake=stake)

    def attach(self, profile_or_type, **kwargs):
        profile = profile_or_type(**kwargs) if isinstance(profile_or_type, type) else profile_or_type
        profile.attach(self)
        self.ctx.profile = profile
        return self

    def run(self, **kwargs):
        results = self.cerebro.run(**kwargs)

        for name, exporter in self.ctx.exporters.items():
            exporter.export(self, results)

        return results, self.ctx


class OPTEngine:
    def __init__(self, config: Dict[str, Any], batch_size=512, max_cpus=None):
        self.config = config
        self.batch_size = batch_size
        self.max_cpus = max_cpus

        self.opt_params = None
        self.ctx = RunContext()


    def opt_strategy(self, strategy, **opt_params):
        self.ctx.strategies.append(strategy)
        self.opt_params = opt_params

    def attach(self, profile):
        self.ctx.profile = profile

    @staticmethod
    def chunked(iterable, size):
        it = iter(iterable)
        while True:
            batch = list(itertools.islice(it, size))
            if not batch:
                break
            yield batch

    @property
    def count_combos(self):
        return math.prod(len(v) for v in self.opt_params.values())

    def run(self):
        optkeys = list(self.opt_params)
        vals = self.opt_params.values()
        optvals = itertools.product(*vals)

        okwargs_dicts = map(lambda vs: dict(zip(optkeys, vs)), optvals)

        total_batch = math.ceil(self.count_combos / self.batch_size)

        opt_exp = OptExporter(output_path=self.ctx.profile.output_path)

        for idx, batch in enumerate(self.chunked(okwargs_dicts, self.batch_size), start=1):
            print(f"Total batch: {total_batch}, Current batch: {idx}")
            _pf_cp = copy.deepcopy(self.ctx.profile)
            _st_cp = copy.deepcopy(self.ctx.strategies[0])

            c_engine = CoreEngine({})
            c_engine.cerebro.optstrategy_combos(_st_cp, kwcombos=batch)
            c_engine.attach(_pf_cp)
            results, _ = c_engine.run(maxcpus=self.max_cpus)

            opt_exp.add_batch(self.opt_params, results)

            del c_engine, _pf_cp, _st_cp, results
            gc.collect()

        opt_exp.export()

