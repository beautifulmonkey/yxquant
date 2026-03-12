from yxquant.data import CSVData
from yxquant.utils import start_static_server
from yxquant.engine import OPTEngine
from yxquant.profiles import DataFeed, BacktestMode, OptimizeProfile, Broker, OHLCV
from yxquant.trading import CTAStrategyBase
import backtrader as bt

class EMA9Strategy(CTAStrategyBase):
    name = 'EMA9'
    params = dict(
        period=9,  # EMA 计算周期
        tp=10,  # 止盈点数
        sl=7  # 止损点数
    )

    def __init__(self):
        super().__init__()
        self.ema9 = bt.indicators.EMA(self.datas[0], period=self.p.period)

    def on_data(self):
        o, h, l, c = self.data.open[0], self.data.high[0], self.data.low[0], self.data.close[0]

        if self.ema9[0] > l >= self.ema9[-1]:
            self.long(tp_price=c + self.p.tp, sl_price=c - self.p.sl)


if __name__ == '__main__':
    BACKTEST_CTA_PROFILE = OptimizeProfile(
        mode=BacktestMode.CTA,
        data=[DataFeed(name="ES", feed=CSVData, params=dict(path="ES_5min.csv"), schema=OHLCV)],
        broker=Broker(cash=10000)
    )
    engine = OPTEngine({}, batch_size=512, max_cpus=None)
    # 对止盈和止损参数做网格搜索，批量评估不同参数组合的表现。
    engine.opt_strategy(EMA9Strategy, **dict(
        tp=range(5, 20),
        sl=range(5, 20),
    ))
    engine.attach(BACKTEST_CTA_PROFILE)
    engine.run()
    # 启动静态页面，用于查看参数优化结果。
    start_static_server()

