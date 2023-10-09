import backtrader as bt
from collections import defaultdict


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

