# yx_quant/run_profiles/backtest.py
from typing import Dict, Any
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union, Type
from .common import DataFeed, Broker
# 可继续扩展 ParquetFeed / DBFeed 等


@dataclass
class BacktestProfile:
    data: Sequence[DataFeed]
    broker: Optional[Broker] = None

    def attach(self, engine):
        for d in self.data:
            engine.add_data(d.feed, name=d.name, params=d.params)

        b = engine.cerebro.getbroker()
        if self.broker:
            if self.broker.commission is not None:
                b.setcommission(commission=self.broker.commission)
            if self.broker.cash is not None:
                b.setcash(self.broker.cash)
            if self.broker.slip_perc:
                # 仅示例：简单滑点；复杂滑点请自定义 Slippage 模型
                engine.cerebro.broker.set_slippage_perc(perc=self.broker.slip_perc)

        # 分析器
        # engine.add_analyzers()
