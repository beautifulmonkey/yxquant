import json
import pandas as pd
import backtrader as bt
from typing import Dict, Any
from yxquant.analyzer import get_performance
from .base import BaseExporter
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


class WebViewExporter(BaseExporter):
    """Web可视化结果导出"""
    performance: Dict[str, Any] = {}
    mark_lines = []
    mark_points = []
    mark_areas = []

    def mark(self, back_result):
        for st in back_result:
            if getattr(st, '_mark_lines', None):
                self.mark_lines += st._mark_lines
            if getattr(st, '_mark_points', None):
                self.mark_points += st._mark_points
            if getattr(st, '_mark_areas', None):
                self.mark_areas += st._mark_areas

    def to_qs_report(self, trade_record_df, rf=0.02, periods=252, filename="qs_report.html"):
        df = trade_record_df.copy()
        df.set_index(pd.to_datetime(df["close_time"], errors="coerce"), inplace=True)

        # 按日聚合净值：取每日最后一个交易的balance
        df['_day'] = df.index.date
        daily_netvalue = df.groupby("_day")["balance"].last()
        daily_netvalue.index = pd.to_datetime(daily_netvalue.index, format='%Y-%m-%d')
        # 填充缺失的交易日（使用前值填充）
        daily_netvalue = daily_netvalue.resample('D').ffill()
        daily_returns = daily_netvalue.pct_change().dropna()
        import quantstats as qs
        qs.reports.html(
            daily_returns,
            output=f"{self.output_path}/dist/{filename}",
            title="Report",
            rf=rf,
            periods_per_year=periods
        )

    def export(self, engine, back_result):
        trade_record_df = engine.ctx.exporters["TradeRecordExporter"].trade_record_df
        trade_record_list = engine.ctx.exporters["TradeRecordExporter"].trade_record_list

        date_list = [bt.num2date(i).date() for i in engine.cerebro.datas[0].datetime.array]
        self.mark(back_result)
        self.performance = get_performance(trade_record_df, date_list)

        data_json = {
            "trade_record": trade_record_list,
            "performance": self.performance,
            "correlation": {},
            # "strategy_params": [{'name': st.name, **st.params.__dict__} for st in back_result],
            "strategy_params": [], # todo: time format
            "mark_lines": self.mark_lines,
            "mark_points": self.mark_points,
            "mark_areas": self.mark_areas
        }
        if trade_record_list:
            self.to_qs_report(trade_record_df)

        with open(f"{self.output_path}/dist/trade_data.json", "w") as outfile:
            json.dump(data_json, outfile)

