import backtrader as bt
from datetime import time as dtime
from collections import defaultdict
from yxquant.utils.logger import get_logger
from yxquant.profiles.common import RunningMode


class BaseStrategy(bt.Strategy):
    params = dict(
        exported_indicators=[],
        forbidden_entry_date=[],  # 'YYYY-MM-DD'
        forbidden_entry_time=[],  # datetime.time
        forbidden_exit_date=[],  # 'YYYY-MM-DD'
        forbidden_exit_time=[],  # datetime.time
        position_close=[],  # 'HH:MM:SS'
        max_spread=9999,  # 实盘最大点差(Ask-Bid), Line必须要有spread字段
    )

    def __init__(self):
        super().__init__()

        self._mark_lines = []
        self._mark_points = []
        self._mark_areas = []

        self._strat_position = defaultdict(bt.Position)
        self._bt_last_dt: float = 0
        self.logger = get_logger('live') if self.is_live else None

        # 获取风控引擎（如果已注册）
        self.risk_engine = getattr(self.cerebro.p, 'risk_engine', None)
        if self.risk_engine:
            self.risk_engine.set_strategy(self)

    def on_order(self, order):
        # 订单事件
        pass

    def on_trade(self, trade):
        # 交易事件
        pass

    def on_data(self):
        # 数据事件
        pass

    def on_start(self):
        # 策略开始事件
        pass

    def on_stop(self):
        # 策略结束事件
        pass

    def on_buy(self, **kwargs):
        # 买入事件
        pass

    def on_sell(self, **kwargs):
        # 卖出事件
        pass

    def close_all(self):
        raise NotImplementedError

    @property
    def is_backtest(self):
        return self.cerebro.params.running_mode == RunningMode.BACKTEST

    @property
    def is_opt(self):
        return self.cerebro.params.running_mode == RunningMode.OPT

    @property
    def is_live(self):
        return self.cerebro.params.running_mode == RunningMode.LIVE

    @property
    def _time(self):
        return self.data.datetime.datetime()

    @property
    def _stime(self):
        return str(self._time)

    def f2t(self, t):
        return str(bt.num2date(t))

    def _in_time_range(self, check: dtime, start: dtime, end: dtime) -> bool:
        if start <= end:
            return start <= check <= end
        else:
            return check >= start or check <= end

    @property
    def _entry_time_available(self):
        now = self.data.datetime.time()
        for start, end in self.p.forbidden_entry_time:
            if self._in_time_range(now, start, end):
                return False
        return True

    @property
    def _exit_time_available(self):
        now = self.data.datetime.time()
        for start, end in self.p.forbidden_exit_time:
            if self._in_time_range(now, start, end):
                return False
        return True

    @property
    def _entry_date_available(self):
        _d = str(self._time.date())
        return _d not in self.p.forbidden_entry_date

    @property
    def _exit_date_available(self):
        _d = str(self._time.date())
        return _d not in self.p.forbidden_exit_date

    @property
    def _risk_control_allowed(self):
        """
        风控检查：检查是否允许交易
        如果任何监控器禁止交易，则不允许交易
        """
        if self.risk_engine:
            return self.risk_engine.is_trading_allowed()
        return True

    @property
    def _liquidity_risk(self):
        """
            流动性风险检查
            任何一方点差大于max_spread就不入场
        """
        for _line in self.datas:
            if not hasattr(_line, 'spread'):
                continue
            _spread = _line.spread[0]
            if _spread >= self.p.max_spread:
                if self.logger:
                    self.logger.error(f"Liquidity Risk !!! -> {self.name} {self._stime} Spread:{_spread}")
                return True
        return False

    @staticmethod
    def entry_guard(func):
        """
            Decorator to guard entry functions with time/date/... conditions.
        """

        def _wrapped(self, *args, **kwargs):
            if not self._entry_time_available:
                return
            if not self._entry_date_available:
                return
            # 风控检查：如果任何监控器禁止交易，则不允许交易
            if not self._risk_control_allowed:
                if self.logger:
                    self.logger.warning(
                        f"风控禁止交易 -> {self.name} {self._stime} "
                        f"(风控监控器已禁止交易)"
                    )
                return

            return func(self, *args, **kwargs)

        return _wrapped

    @staticmethod
    def exit_guard(func):
        """
            Decorator to guard exit functions with time/date/... conditions.
        """

        def _wrapped(self, *args, **kwargs):
            if not self._exit_time_available:
                return
            if not self._exit_date_available:
                return

            return func(self, *args, **kwargs)

        return _wrapped

    @staticmethod
    def liquidity_risk_guard(func):
        """
            Decorator to guard entry functions with liquidity risk conditions.
        """

        def _wrapped(self, *args, **kwargs):
            if self._liquidity_risk:
                return
            return func(self, *args, **kwargs)

        return _wrapped

    def getstrategyposition(self, data=None, broker=None):
        data = data if data is not None else self.datas[0]
        broker = broker or self.broker
        if callable(getattr(broker, 'getstrategyposition', None)):
            return broker.getstrategyposition(data, strategy_name=self.name)
        elif hasattr(self, '_strat_position'):
            return self._strat_position[data]
        else:
            raise NotImplementedError

    def buy(self, data=None,
            size=None, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0, oco=None,
            trailamount=None, trailpercent=None,
            parent=None, transmit=True,
            **kwargs):
        order_params = dict(
            data=data, size=size, price=price, plimit=plimit,
            exectype=exectype, valid=valid, tradeid=tradeid, oco=oco,
            trailamount=trailamount, trailpercent=trailpercent,
            parent=parent, transmit=transmit, **kwargs
        )
        self.on_buy(**order_params)
        return super().buy(**order_params)

    def sell(self, data=None,
             size=None, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0, oco=None,
             trailamount=None, trailpercent=None,
             parent=None, transmit=True,
             **kwargs):
        order_params = dict(
            data=data, size=size, price=price, plimit=plimit,
            exectype=exectype, valid=valid, tradeid=tradeid, oco=oco,
            trailamount=trailamount, trailpercent=trailpercent,
            parent=parent, transmit=transmit, **kwargs
        )
        self.on_sell(**order_params)
        return super().sell(**order_params)

    def close(self, data=None, size=None, **kwargs):
        if data is None:
            data = self.data

        possize = self.getstrategyposition(data=data).size

        size = abs(size if size is not None else possize)

        if possize > 0:
            return self.sell(data=data, size=size, yx_from="close", **kwargs)
        elif possize < 0:
            return self.buy(data=data, size=size, yx_from="close", **kwargs)
        return None

    def notify_order(self, order):
        self.on_order(order)
        # 通知风控引擎
        if self.risk_engine:
            self.risk_engine.on_order(order)

    def notify_trade(self, trade):
        self._strat_position[trade.data] = bt.Position(size=trade.size, price=trade.price)
        self.on_trade(trade)
        # 通知风控引擎
        if self.risk_engine:
            self.risk_engine.on_trade(trade)

    def next(self):
        if self.cerebro.tqdm:
            self.cerebro.tqdm.update(1)

        all_data_times = []
        for data in self.datas:
            if getattr(data, 'is_warmup', False):
                return
            all_data_times.append(str(data.datetime.datetime()))

        if len(set(all_data_times)) > 1:
            self.logger.error(
                f"Strategy -> Inconsistency of data time  -> {self.name} {self._stime} {str(all_data_times)}")
            return

        if self.is_live:
            if hasattr(self.broker, 'ib') and not self.broker.ib.conn.isConnected():
                self.logger.error(f"Strategy -> No IB connection -> {self.name} {self._stime}")
                return

        # 检查风控（所有模式）
        if self.risk_engine:
            try:
                self.risk_engine.on_data()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"风控检查出错: {e}", exc_info=True)

        if str(self._time.time()) in getattr(self.p, 'position_close', []):
            return self.close_all()

        if (self.is_backtest or self.is_opt) and self.data.datetime[0] >= self._bt_last_dt:
            return self.close_all()

        self.on_data()

    def start(self):
        if self.is_backtest or self.is_opt:
            if len(self.data.datetime.array):
                self._bt_last_dt = self.data.datetime[-1]
            else:
                self._bt_last_dt = bt.date2num(self.data.p.dataname.index[-2])

        self.on_start()

    def stop(self):
        self.on_stop()
        # 通知风控引擎停止
        if self.risk_engine:
            self.risk_engine.on_stop()

    def add_mark_point(self, x=None, y=None, color=None):
        self._mark_points.append({
            "coord": [x, y],
            "itemStyle": {
                "color": color,
            }
        })

    def add_mark_line(self):
        # todo
        pass

    def add_mark_area(self, x1=None, y1=None, x2=None, y2=None, label='', color='#fff', border_color='', border_width=1,
                      border_type='solid'):
        self._mark_areas.append([{
            "coord": [x1, y1],
            "name": label,
            "itemStyle": {
                "color": color,
                "borderColor": border_color,
                "borderWidth": border_width,
                "borderType": border_type, }},
            {"coord": [x2, y2]}
        ])