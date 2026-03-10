import backtrader as bt
from collections import defaultdict
import pandas as pd


class PnlAnalyzer(bt.Analyzer):
    def __init__(self):
        self.pnl_list = []
        self.pnl_days = defaultdict(float)
        self.id_pnl_map = defaultdict(float)
        self.id_balance_map = {}
        self.trade_records_dict = {}

    def get_analysis(self, rf=0.02, periods=252):
        # 将字典转换为列表返回
        trade_records = list(self.trade_records_dict.values())
        pnl_list = [i["pnl"] for i in trade_records]
        _win_trades = [i for i in pnl_list if i > 0]
        _loss_trades = [i for i in pnl_list if i <= 0]
        if not pnl_list:
            return {"Pnl_list": [], "Total_net_profit": 0, "Total_of_trades": 0, "Percent_profitable": 0,
                    "Avg_trade": 0, "Ratio_win_loss": 0, "Sharperatio": 0, "Drawdown": 0, "Sortino": 0, "Calmar": 0,
                    "CAGR": 0, }

        df = pd.DataFrame(trade_records)
        df.set_index(df["close_time"], inplace=True)

        df['_day'] = df.index.date
        daily_netvalue = df.groupby("_day")["balance"].last()
        daily_netvalue.index = pd.to_datetime(daily_netvalue.index, format='%Y-%m-%d')
        daily_netvalue = daily_netvalue.resample('D').ffill()
        daily_returns = daily_netvalue.pct_change().dropna()

        import quantstats as qs
        if daily_netvalue.size <= 1:
            sharpe, max_drawdown, sortino, calmar, cagr = [0, 0, 0, 0, 0]
        else:
            sharpe = qs.stats.sharpe(daily_returns, rf=rf, periods=periods, annualize=True)
            max_drawdown = qs.stats.max_drawdown(daily_returns) * 100
            sortino = qs.stats.sortino(daily_returns, rf=rf, periods=periods, annualize=True)
            calmar = qs.stats.calmar(daily_returns) if max_drawdown else 999
            cagr = qs.stats.cagr(daily_returns, periods=periods)

        return {
            "Pnl_list": pnl_list,
            "Total_net_profit": int(sum(pnl_list)),
            "Total_of_trades": len(pnl_list),
            "Percent_profitable": round(len(_win_trades) / len(pnl_list) * 100 if _win_trades else 0, 1),
            "Avg_trade": round(sum(pnl_list) / len(pnl_list), 2) if pnl_list else 0,
            "Ratio_win_loss": round(
                float(sum(_win_trades) / len(_win_trades)) / abs(float(sum(_loss_trades) / len(_loss_trades))),
                2) if _win_trades and _loss_trades else 0,
            "Sharperatio": round(sharpe, 2),
            "Drawdown": round(max_drawdown, 2),
            "Sortino": round(sortino, 2),
            "Calmar": round(calmar, 2),
            "CAGR": round(cagr, 2)
        }

    def notify_trade(self, trade):
        tradeid = trade.tradeid
        current_time = trade.data.datetime.datetime() if hasattr(trade, 'data') else None

        if not trade.isclosed:
            if tradeid not in self.trade_records_dict:
                self.trade_records_dict[tradeid] = {
                    "tradeid": tradeid,
                    "open_time": current_time,
                    "close_time": None,
                    "pnl": 0.0,
                    "balance": None
                }
        else:
            pnl, pnlcomm = trade.pnl, trade.pnlcomm
            balance = self.strategy.broker.getcash()

            self.pnl_list.append(pnlcomm)
            self.pnl_days[str(trade.data.datetime.datetime().date())] += pnlcomm
            self.id_pnl_map[tradeid] += pnlcomm
            self.id_balance_map[tradeid] = balance

            if tradeid in self.trade_records_dict:
                self.trade_records_dict[tradeid]["pnl"] += pnlcomm
                self.trade_records_dict[tradeid]["pnl"] = round(self.trade_records_dict[tradeid]["pnl"], 3)
                self.trade_records_dict[tradeid]["close_time"] = current_time
                self.trade_records_dict[tradeid]["balance"] = balance

            else:
                raise Exception(f"No trade record for {tradeid}")



