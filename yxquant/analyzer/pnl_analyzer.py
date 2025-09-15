import backtrader as bt
from collections import defaultdict
import numpy as np


class PnlAnalysis(bt.Analyzer):
    def __init__(self):
        self.pnl_list = []
        self.pnl_daily = defaultdict(float)
        self.id_pnl_map = {}

    def get_analysis(self):
        _win_trades = [i for i in self.pnl_list if i > 0]
        _loss_trades = [i for i in self.pnl_list if i <= 0]

        return {
            "Pnl_list": self.pnl_list,  # 盈亏列表
            "Total_net_profit": sum(self.pnl_list),  # 总盈亏
            "Total_of_trades": len(self.pnl_list),  # 交易笔数
            "Percent_profitable": int(len(_win_trades) / len(self.pnl_list) * 100) if _win_trades else 0,  # 胜率
            "Avg_trade": sum(self.pnl_list) / len(self.pnl_list) if self.pnl_list else 0,  # 平均单笔盈亏
            "Ratio_win_loss": round(
                float(sum(_win_trades) / len(_win_trades)) / abs(float(sum(_loss_trades) / len(_loss_trades))),
                2) if _win_trades and _loss_trades else 0  # 盈亏比
        }

    def notify_trade(self, trade):
        if trade.isclosed:
            self.pnl_list.append(trade.pnl)
            self.pnl_daily[str(trade.data.datetime.datetime().date())] += trade.pnl
            self.id_pnl_map[trade.tradeid] = trade.pnl


class ParamsOpt:
    def __init__(self, back, params):
        self.back = back
        self.params = params

    def params_pnl_curve(self):
        """每个参数组合的盈利曲线"""
        export_data = []
        for idx, _b in enumerate(self.back, start=1):
            if len(self.params) == 1:
                idx = getattr(_b[0].p, next(iter(self.params)))
            pnl_list = _b[0].analyzers.pnl_analysis.get_analysis()["Pnl_list"]
            if not pnl_list: continue
            x_list = list(range(len(pnl_list)))
            y_list = np.cumsum(pnl_list).tolist()
            export_data.append({
                'x': x_list,
                'y': y_list,
                'name': idx
            })
        return export_data

    def params_performance(self):
        items = []
        for idx, _b in enumerate(self.back, start=1):
            performance = _b[0].analyzers.pnl_analysis.get_analysis()
            sharperatio = _b[0].analyzers.sharpe.get_analysis()['sharperatio']
            returns = _b[0].analyzers.returns.get_analysis()['rnorm100']
            drawdown = _b[0].analyzers.drawdown.get_analysis()['max']['drawdown']
            summary = dict(
                Sharperatio=sharperatio,
                Drawdown=drawdown,
                Returns=returns,
                **performance
            )
            summary.pop("Pnl_list")
            for _param in self.params.keys():
                summary[_param] = getattr(_b[0].params, _param)
            items.append(summary)

        return items

