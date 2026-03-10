import copy
import json
from typing import Dict, List
from .base import BaseExporter
import numpy as np


class OptExporter(BaseExporter):
    """参数优化结果导出"""
    lines: List[Dict] = []
    table: List[Dict] = []

    # 各个指标的排行榜
    top_sharpe = []
    top_calmar = []
    top_sortino = []
    top_drawdown = []
    top_total_net_profit = []
    top_total_of_trades = []
    top_percent_profitable = []
    top_avg_trade = []
    top_ratio_win_loss = []

    top_n = 5

    def add_batch(self, opt_params, back_result):
        _idx_start = len(self.table) + 1
        batch_results = []
        for idx, _b in enumerate(back_result, start=_idx_start):
            performance = _b[0].analyzers.pnl_analysis.get_analysis()
            summary = dict(
                id=idx,
                **performance
            )
            batch_results.append(copy.deepcopy(summary))
            summary.pop("Pnl_list", None)
            for _param in opt_params.keys():
                summary[_param] = getattr(_b[0].params, _param)
            self.table.append(summary)

        # 本批更新top排行榜
        if batch_results:
            # todo: refine this shit

            # Sharpe最大
            combined = OptExporter.top_sharpe + batch_results
            combined = sorted(combined, key=lambda x: (x['Sharperatio'] is not None, x['Sharperatio']), reverse=True)
            OptExporter.top_sharpe = combined[:OptExporter.top_n]

            # Calmar最大
            combined = OptExporter.top_calmar + batch_results
            combined = sorted(combined, key=lambda x: (x['Calmar'] is not None, x['Calmar']), reverse=True)
            OptExporter.top_calmar = combined[:OptExporter.top_n]

            # Sortino最大
            combined = OptExporter.top_sortino + batch_results
            combined = sorted(combined, key=lambda x: (x['Sortino'] is not None, x['Sortino']), reverse=True)
            OptExporter.top_sortino = combined[:OptExporter.top_n]

            # Drawdown最小
            combined = OptExporter.top_drawdown + batch_results
            combined = sorted(combined, key=lambda x: (x['Drawdown'] is not None, x['Drawdown']), reverse=False)
            OptExporter.top_drawdown = combined[:OptExporter.top_n]

            # Total_net_profit最大
            combined = OptExporter.top_total_net_profit + batch_results
            combined = sorted(combined, key=lambda x: (x['Total_net_profit'] is not None, x['Total_net_profit']), reverse=True)
            OptExporter.top_total_net_profit = combined[:OptExporter.top_n]

            # Total_of_trades最大
            combined = OptExporter.top_total_of_trades + batch_results
            combined = sorted(combined, key=lambda x: (x['Total_of_trades'] is not None, x['Total_of_trades']), reverse=True)
            OptExporter.top_total_of_trades = combined[:OptExporter.top_n]

            # Percent_profitable最大
            combined = OptExporter.top_percent_profitable + batch_results
            combined = sorted(combined, key=lambda x: (x['Percent_profitable'] is not None, x['Percent_profitable']), reverse=True)
            OptExporter.top_percent_profitable = combined[:OptExporter.top_n]

            # Avg_trade最大
            combined = OptExporter.top_avg_trade + batch_results
            combined = sorted(combined, key=lambda x: (x['Avg_trade'] is not None, x['Avg_trade']), reverse=True)
            OptExporter.top_avg_trade = combined[:OptExporter.top_n]

            # Ratio_win_loss最大
            combined = OptExporter.top_ratio_win_loss + batch_results
            combined = sorted(combined, key=lambda x: (x['Ratio_win_loss'] is not None, x['Ratio_win_loss']), reverse=True)
            OptExporter.top_ratio_win_loss = combined[:OptExporter.top_n]


    def export(self):
        # 融合所有榜单、参数组根据id去重
        candidates = OptExporter.top_sharpe + OptExporter.top_calmar + OptExporter.top_sortino + OptExporter.top_drawdown + OptExporter.top_total_net_profit + OptExporter.top_total_of_trades + OptExporter.top_percent_profitable + OptExporter.top_avg_trade + OptExporter.top_ratio_win_loss
        uniq = {}
        for item in candidates:
            key = item['id']
            if key not in uniq:
                uniq[key] = item
        final_results = list(uniq.values())
        self.lines = []
        for result in final_results:
            x_list = list(range(len(result["Pnl_list"])))
            y_list = np.cumsum(result["Pnl_list"]).tolist()
            self.lines.append({
                'x': x_list,
                'y': y_list,
                'name': result['id']
            })
        if not self.lines or not self.table:
            raise NotImplementedError

        with open(f"{self.output_path}/dist/opt_report.json", "w") as outfile:
            json.dump({"lines": self.lines, "table": self.table}, outfile)

