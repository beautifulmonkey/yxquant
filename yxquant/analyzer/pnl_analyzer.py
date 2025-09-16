import backtrader as bt
from collections import defaultdict


class PnlAnalyzer(bt.Analyzer):
    def __init__(self):
        self.pnl_list = []
        self.pnl_days = defaultdict(float)
        self.id_pnl_map = {}
        self.id_balance_map = {}

    def get_analysis(self):
        _win_trades = [i for i in self.pnl_list if i > 0]
        _loss_trades = [i for i in self.pnl_list if i <= 0]

        return {
            "Pnl_list": self.pnl_list,
            "Total_net_profit": int(sum(self.pnl_list)),
            "Total_of_trades": len(self.pnl_list),
            "Percent_profitable": round(len(_win_trades) / len(self.pnl_list) * 100 if _win_trades else 0, 1),
            "Avg_trade": sum(self.pnl_list) / len(self.pnl_list) if self.pnl_list else 0,
            "Ratio_win_loss": round(
                float(sum(_win_trades) / len(_win_trades)) / abs(float(sum(_loss_trades) / len(_loss_trades))),
                2) if _win_trades and _loss_trades else 0,
        }

    def notify_trade(self, trade):
        if trade.isclosed:
            self.pnl_list.append(trade.pnl)
            self.pnl_days[str(trade.data.datetime.datetime().date())] += trade.pnl
            self.id_pnl_map[trade.tradeid] = trade.pnl
            self.id_balance_map[trade.tradeid] = self.strategy.broker.getcash()



