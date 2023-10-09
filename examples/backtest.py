import pandas as pd
import backtrader as bt

from yxquant.yxquant.trading import Trading
from yxquant.yxquant.cerebro import Cerebro


class EMA9Strategy(Trading):
    name = 'EMA9'
    params = dict(
        RTH_stop=10,
        RTH_target=20,
        forbidden_hour=[*Trading.ETH1, *Trading.ETH2],
    )

    def __init__(self):
        super().__init__()
        self.ema9 = bt.indicators.EMA(self.datas[0], period=9)

    @Trading.position_management
    def next(self):
        if self.data.high[0] > self.ema9[0] and self.data.high[-1] <= self.ema9[-1]:
            self.trade_by_signal(-1)  # 做空
        elif self.data.low[0] < self.ema9[0] and self.data.low[-1] >= self.ema9[-1]:
            self.trade_by_signal(1)  # 做多


if __name__ == '__main__':

    df = pd.read_csv("ES_5min.csv", parse_dates=[0], index_col=0)

    cerebro = Cerebro()

    cerebro.adddata(df)
    cerebro.addstrategy(EMA9Strategy)
    cerebro.broker.setcash(100000.0)
    cerebro.run()
    cerebro.plot()
    print(f"最终资金: {cerebro.broker.getvalue()}")
