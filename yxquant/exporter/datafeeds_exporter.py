import json
import backtrader as bt
from typing import List, Union
from .base import BaseExporter

class DataFeedsExporter(BaseExporter):
    feeds: List[List] = []

    def export(self, engine, back_result):
        for feed in engine.cerebro.datas:
            _datetime = feed.p.dataname.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
            _open = feed.p.dataname.open.to_numpy().tolist()
            _close = feed.p.dataname.close.to_numpy().tolist()
            _high = feed.p.dataname.high.to_numpy().tolist()
            _low = feed.p.dataname.low.to_numpy().tolist()
            _volume = feed.p.dataname.volume.to_numpy().tolist()

            self.feeds.append(list(map(list, zip(_datetime, _open, _high, _low, _close, _volume))))

        with open(f"{self.output_path}/dist/datafeeds.json", "w") as outfile:
            json.dump({
                "datafeeds": self.feeds
            }, outfile)


class ArbSpreadDataFeedsExporter(BaseExporter):
    dataset: List[List[Union[float, str]]] = []

    def export(self, engine, back_result):
        assert len(engine.cerebro.datas) == 2

        date_list = [str(bt.num2date(i)) for i in engine.cerebro.datas[0].datetime.array]
        spot_close = engine.cerebro.datas[0].close.array.tolist()
        future_close = engine.cerebro.datas[1].close.array.tolist()
        spread = [round(f - s, 4) for f, s in zip(future_close, spot_close)]

        result = [list(x) for x in zip(date_list, spot_close, future_close, spread)]

        with open(f"{self.output_path}/dist/arb_datafeeds.json", "w") as outfile:
            json.dump({
                "datasource": result
            }, outfile)

