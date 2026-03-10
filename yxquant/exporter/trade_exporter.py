from yxquant.profiles.common import BacktestMode

from collections import defaultdict
from typing import Dict, List

import backtrader as bt
import pandas as pd
import json

from .base import BaseExporter


class TradeRecordExporter(BaseExporter):
    trade_record_df: pd.DataFrame
    trade_record_list: List[Dict]

    def _to_cta_trade_record(self, back_result, grouped_order):
        # todo: 摆脱analyzer计算收益
        pnl_map = {k: v for st in back_result for k, v in st.analyzers.pnl_analysis.id_pnl_map.items()}
        balance_map = {k: v for st in back_result for k, v in st.analyzers.pnl_analysis.id_balance_map.items()}

        trade_records = []
        for entry_order, out_order in grouped_order:
            open_time = bt.num2date(entry_order.executed.dt)
            close_time = bt.num2date(out_order.executed.dt)
            pnl = round(pnl_map[entry_order.tradeid], 3)
            action = "long" if entry_order.isbuy() else "short"
            strategy = entry_order.p.owner.name
            balance = balance_map[entry_order.tradeid]
            duration = (close_time - open_time).seconds
            tradeid = entry_order.tradeid

            trade_records.append({
                "strategy": strategy,
                "tradeid": tradeid,
                "open_time": open_time,
                "open_price": entry_order.executed.price,
                "action": action,
                "close_time": close_time,
                "close_price": out_order.executed.price,
                "duration_sec": duration,
                "pnl": pnl,
                "balance": balance,
            })

        return trade_records


    def _to_arb_trade_record(self, back_result, grouped_order):
        pass

    def _order_grouper(self, engine):
        all_trades_map = defaultdict(list)
        for order in engine.cerebro.broker.orders:
            if order.status in [order.Completed]:
                all_trades_map[order.tradeid].append(order)

        grouped_order = list(all_trades_map.values())
        grouped_order.sort(key=lambda x: x[0].executed.dt)
        return grouped_order

    def trade_record_to_list(self):
        _record = self.trade_record_df.copy()
        if not _record.size: return []
        _record = _record.drop(columns=["tradeid"])
        _record["open_time"] = _record["open_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        _record["close_time"] = _record["close_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        return _record.to_dict(orient="records")

    def export(self, engine, back_result):
        grouped_order = self._order_grouper(engine)
        if self.kwargs["mode"] == BacktestMode.ARB:
            record = self._to_arb_trade_record(back_result, grouped_order)
        elif self.kwargs["mode"] == BacktestMode.CTA:
            record = self._to_cta_trade_record(back_result, grouped_order)
        else:
            raise NotImplementedError

        self.trade_record_df = pd.DataFrame(record)
        self.trade_record_list = self.trade_record_to_list()

        self.trade_record_df.to_csv(f"{self.output_path}/trade_records.csv")
