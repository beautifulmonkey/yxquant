import backtrader as bt
from datetime import datetime, time as dtime
from collections import defaultdict
import uuid
import time
import json
import logging
import requests
logger = logging.getLogger()


class Trading(bt.Strategy):
    TRADES_FORBIDDEN_TIME = [
            '08:30:00',  # 数据公布 如CPI/非农
            '14:00:00',  # 美联储事件
            '14:30:00',  # 美联储事件
            '16:55:00',  # 期货收盘
        ]

    ETH1 = [18, 19, 20, 21, 22, 23, 0, 1, 2]
    ETH2 = [3, 4, 5, 6, 7, 8]
    RTH = [9, 10, 11, 12, 13, 14, 15, 16, 17]

    LIVE = False
    SIGNAL_WEBHOOK_URL = None  # Discord信号通知
    TRADE_WEBHOOK_URL = None  # Discord交易通知

    TICK = 0.25

    def __init__(self):
        self.open_order = {}  # open的订单
        self.position_size = 0  # 当前仓位
        self.last_complete_order = None  # 最新成交订单
        self.daily_pnl = defaultdict(list)

        self._best_trail = None
        self._check_stoptrail = True

    @staticmethod
    def position_management(next_func):
        def wrapper(self):
            if getattr(self, 'tqdm', None):
                self.tqdm.update(1)
            self.before_exec_strategy(next_func)
        return wrapper

    def before_exec_strategy(self, callback):
        self._check_stoptrail = True
        # 收盘前平仓
        if str(self._time.time()) in ['16:55:00', *getattr(self.p, 'position_close', [])]:
            self.close_all_position()
            return

        # 执行策略
        callback(self)

        if getattr(self.p, 'trail_stop_percent', None) and self._check_stoptrail:
            self.check_stop_trail()

    def check_stop_trail(self):
        if not self.position_size:
            self._best_trail = None
            return
        unrealized_pnl = self.unrealized_pnl()
        if not self._best_trail:
            self._best_trail = (None, 0)

        if unrealized_pnl > self._best_trail[1]:
            add_profit = unrealized_pnl - self._best_trail[1]
            add_profit_trail = add_profit * self.p.trail_stop_percent
            if add_profit_trail <= self.TICK:
                return
            elif add_profit_trail % self.TICK != 0:
                add_profit_trail = self.round_to_nearest_multiple(add_profit_trail, self.TICK)
                assert add_profit_trail % self.TICK == 0

            open_orders = self.open_order.values()
            assert len(open_orders) == 2, f"订单个数: {len(open_orders)} 时间: {self._stime} 仓位: {self.position_size}"
            for order in open_orders:
                if order.exectype == bt.Order.Stop:
                    sl_order_params = dict(price=order.price, exectype=bt.Order.Stop, tradeid=order.tradeid)
                elif order.exectype == bt.Order.Limit:
                    tp_order_params = dict(price=order.price, exectype=bt.Order.Limit, tradeid=order.tradeid)
                self.cancel(order)
            assert sl_order_params['tradeid'] == tp_order_params['tradeid']
            tradeid = sl_order_params['tradeid']
            if self.position_size > 0:
                update_stop = sl_order_params["price"] + add_profit_trail
                sl_order_params['price'] = update_stop
                sl_order = self.sell(**sl_order_params)
                tp_order = self.sell(oco=sl_order, **tp_order_params)
                logger.debug(f'{self.name} move_stop@{update_stop} time@{self._stime} ref:{sl_order.ref}/{tp_order.ref} tradeid:{tradeid}')

            elif self.position_size < 0:
                update_stop = sl_order_params["price"] - add_profit_trail
                sl_order_params['price'] = update_stop
                sl_order = self.buy(**sl_order_params)
                tp_order = self.buy(oco=sl_order, **tp_order_params)
                logger.debug(f'{self.name} move_stop@{update_stop} time@{self._stime} ref:{sl_order.ref}/{tp_order.ref} tradeid:{tradeid}')

            self._best_trail = (None, unrealized_pnl)

    def notify_order(self, order):
        logger.debug(f'{self.name} notify_order -> Ref:{order.ref} Status:{order.Status[order.status]} ExecType:{order.ExecTypes[order.exectype]}')

        if order.status == order.Rejected:
            logger.error(f'{self.name} Order Rejected!!')
            return

        if order.status in [order.Completed]:
            self.last_complete_order = order

        if order.status in [order.Created, order.Submitted, order.Accepted]:
            self.open_order[order.ref] = order
        else:
            self.open_order.pop(order.ref)

    def notify_trade(self, trade):  # 记录交易收益情况
        self.position_size = trade.size
        logger.debug(f'{self.name} notify_trade -> size:{trade.size} pnl:{trade.pnl}')
        if trade.isclosed:
            self.daily_pnl[str(self._time.date())].append(trade.pnl)
            logger.debug(f'{self.name} out@{self.last_complete_order.executed.price} time@{self.f2t(trade.dtopen)} tradeid:{trade.tradeid}')
            logger.debug(f'{self.name} trade_close@{self.f2t(trade.dtopen)} pnl:{trade.pnl}')

    def notify_store(self, msg, *args, **kwargs):
        logger.debug("notify_store -> " + str(msg))

    def close_all_position(self):
        for order in self.open_order.values():
            self.cancel(order)
            logger.debug(f'{self.name} cancel time@{self._stime} tradeid:{order.tradeid}')

        if self.position_size == 0: return

        tid = self.last_complete_order.tradeid

        if self.position_size > 0:
            self.sell(tradeid=tid, exectype=bt.Order.Market)
            self._check_stoptrail = False
            logger.debug(f'{self.name} sell2close time@{self._stime} tradeid:{tid}')
        elif self.position_size < 0:
            self.buy(tradeid=tid, exectype=bt.Order.Market)
            self._check_stoptrail = False
            logger.debug(f'{self.name} buy2close time@{self._stime} tradeid:{tid}')

    def trade_by_signal(self, signal, price=None):
        """根据策略产生的信号进行交易, 包括一些仓位的控制"""
        current_close = price or self.data.close[0]
        exectype = bt.Order.Limit if price else bt.Order.Market
        _time = self._time

        if str(_time.time()) in [
            *self.TRADES_FORBIDDEN_TIME,
            *getattr(self.p, 'position_close', []),
            *getattr(self.p, 'forbidden_time', []),
        ]: return
        if _time.hour in self.params.forbidden_hour: return

        trade_id = str(uuid.uuid1())
        if self.position_size == 0:
            self.close_all_position()
            if signal == 1:
                # 做多
                stop_price = current_close-self.timeframe_sl
                target_price = current_close+self.timeframe_tp
                if self.LIVE:
                    self.trade_alert('Long', current_close)
                    trade = self.db_add_trades(lmt=current_close, action="BUY", quantity=1, target=target_price, stop=stop_price, strategy=self.name)
                    trade_id = trade.id
                main_order = self.buy(price=current_close, exectype=exectype, tradeid=trade_id)
                sl_order = self.sell(price=stop_price, exectype=bt.Order.Stop, tradeid=trade_id)
                tp_order = self.sell(price=target_price, exectype=bt.Order.Limit, tradeid=trade_id, oco=sl_order)
                logger.debug('------------------------------------')
                logger.debug(f'{self.name} long@{current_close} time@{str(_time)} st@{stop_price} tp@{target_price} ref:{main_order.ref}/{sl_order.ref}/{tp_order.ref} tradeid:{trade_id}')
            elif signal == -1:
                # 做空
                stop_price = current_close+self.timeframe_sl
                target_price = current_close-self.timeframe_tp
                if self.LIVE:
                    self.trade_alert('Short', current_close)
                    trade = self.db_add_trades(lmt=current_close, action="SELL", quantity=1, target=target_price, stop=stop_price, strategy=self.name)
                    trade_id = trade.id
                main_order = self.sell(price=current_close, exectype=exectype, tradeid=trade_id)
                sl_order = self.buy(price=stop_price, exectype=bt.Order.Stop, tradeid=trade_id)
                tp_order = self.buy(price=target_price, exectype=bt.Order.Limit, tradeid=trade_id, oco=sl_order)
                logger.debug('------------------------------------')
                logger.debug(f'{self.name} short@{current_close} time@{str(_time)} st@{stop_price} tp@{target_price} ref:{main_order.ref}/{sl_order.ref}/{tp_order.ref} tradeid:{trade_id}')

        elif self.position_size < 0:  # 持有空仓
            if signal > 0:
                self.close_all_position()
        elif self.position_size > 0:  # 持有多仓
            if signal < 0:
                self.close_all_position()

        if self.LIVE:
            self.signal_alert(signal, current_close, self._stime, self.name)

    def unrealized_pnl(self):
        position_price = self.last_complete_order.executed.price
        if self.position_size < 0:
            pnl = position_price - self.data.close[0]
        if self.position_size > 0:
            pnl = self.data.close[0] - position_price
        return pnl

    def signal_alert(self, _signal, _price, _time, _strategy_name):
        if _signal < 0:
            message = f"看跌信号, price={_price},  Time={_time}  {_strategy_name}"
        elif _signal > 0:
            message = f"看涨信号, Price={_price},  Time={_time}  {_strategy_name}"

        requests.post(self.SIGNAL_WEBHOOK_URL, data={'content': message})

    def trade_alert(self, action, price, pnl=None):
        message = f"{self.name}-{action}@{price}"
        if pnl:
            message += f"  pnl: ${pnl}"
        requests.post(self.TRADE_WEBHOOK_URL, data={'content': message})

    @property
    def timeframe_sl(self):
        _hour = self._time.hour
        if _hour in self.RTH:
            return self.p.RTH_stop
        elif _hour in self.ETH2:
            return self.p.ETH2_stop
        elif _hour in self.ETH1:
            return self.p.ETH1_stop

    @property
    def timeframe_tp(self):
        _hour = self._time.hour
        if _hour in self.RTH:
            return self.p.RTH_target
        elif _hour in self.ETH2:
            return self.p.ETH2_target
        elif _hour in self.ETH1:
            return self.p.ETH1_target

    def f2t(self, t):
        return str(bt.num2date(t))

    @property
    def _time(self):
        return self.data.datetime.datetime()

    @property
    def _stime(self):
        return str(self._time)

    @property
    def _tz(self):
        return "RTH" if dtime(16) > self._time.time() >= dtime(9, 30) else "ETH"

    def stop(self):
        pass
        # print(self.p.__dict__)

    def sell(self, *args, **kwargs):
        kwargs["m_outsideRth"] = True
        kwargs["m_orderRef"] = json.dumps(dict(strategy=self.name, order_time=int(time.time()), tradeid=kwargs["tradeid"]))
        return super().sell(*args, **kwargs)

    def buy(self, *args, **kwargs):
        kwargs["m_outsideRth"] = True
        kwargs["m_orderRef"] = json.dumps(dict(strategy=self.name, order_time=int(time.time()), tradeid=kwargs["tradeid"]))
        return super().buy(*args, **kwargs)


class Report:

    @staticmethod
    def order_group(orders):
        all_trades_map = defaultdict(list)
        for order in orders:
            if order.status in [order.Completed]:
                all_trades_map[order.tradeid].append(order)
        return [i for i in all_trades_map.values() if len(i) == 2]

    @staticmethod
    def get_performance(df, grouped_order, pnl_map):
        hour_returns_distribution = defaultdict(int)
        hour_trades_distribution = defaultdict(int)

        sorted_hour = [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

        time_returns_distribution = {hour: defaultdict(float) for hour in sorted_hour}
        time_trades_distribution = {hour: defaultdict(int) for hour in sorted_hour}

        days_pnl = defaultdict(float)
        month_pnl = defaultdict(float)
        _return = []
        for entry_order, out_order in grouped_order:
            open_time = bt.num2date(entry_order.executed.dt)
            close_time = bt.num2date(out_order.executed.dt)
            pnl = pnl_map[entry_order.tradeid]

            time_returns_distribution[open_time.hour][open_time.minute] += pnl
            time_trades_distribution[open_time.hour][open_time.minute] += 1

            _return.append(pnl)
            hour_returns_distribution[str(open_time.hour) + "点"] += pnl
            hour_trades_distribution[str(open_time.hour) + "点"] += 1
            days_pnl[str(close_time.date())] += pnl
            month_pnl[str(close_time.date())[:-2] + "01"] += pnl

        _win_trades = [i for i in _return if i > 0]
        _loss_trades = [i for i in _return if i <= 0]
        _trading_day = len({i.date() for i in list(df.index)})

        performance = {
            "Total net profit": sum(_return),
            "Gross profit": sum(_win_trades),
            "Gross loss": abs(int(sum(_loss_trades))),
            "Start date": str(df.index[0].date()),
            "End date": str(df.index[-1].date()),
            "Trading day": _trading_day,
            "Total of trades": len(_return),
            "#winning trades": len(_win_trades),
            "#losing trades": len(_loss_trades),
            "Percent profitable": int(len(_win_trades) / len(_return) * 100) if _win_trades else 0,
            "Avg. trade": str(sum(_return) / len(_return))[:4] if _return else 0,
            "Avg. winning trade": str(sum(_win_trades) / len(_win_trades))[:4] if _win_trades else 0,
            "Avg. losing trade": str(abs(sum(_loss_trades) / len(_loss_trades)))[:4] if _loss_trades else 0,
            "Avg. days PnL": round(sum(_return) / _trading_day, 1),
            "Ratio avg.win / avg.loss": round(
                float(sum(_win_trades) / len(_win_trades)) / abs(float(sum(_loss_trades) / len(_loss_trades))),
                2) if _win_trades and _loss_trades else 0,
            "Frequency day": str(len(_return) / _trading_day)[:3],

            "hour_returns_distribution": hour_returns_distribution,  # 时间收益分布,
            "hour_trades_distribution": hour_trades_distribution,  # 时间交易次数分布

            "time_returns_distribution": [[hour, sorted(data.items(), key=lambda x: x[0])] for hour, data in
                                          time_returns_distribution.items()],
            "time_trades_distribution": [[hour, sorted(data.items(), key=lambda x: x[0])] for hour, data in
                                         time_trades_distribution.items()],

            "days_pnl": [[_d, _pnl] for _d, _pnl in sorted(days_pnl.items(), key=lambda x: x[0])],
            "month_pnl": [[_d, _pnl] for _d, _pnl in sorted(month_pnl.items(), key=lambda x: x[0])]
        }
        return performance

    @staticmethod
    def create_report(cerebro):

        grouped_order = list(Report.order_group(cerebro.broker.orders))
        grouped_order.sort(key=lambda x: x[0].executed.dt)

        pnl_map = {k: v for st in cerebro.back for k, v in st.analyzers.pnl_analysis.id_pnl_map.items()}

        echarts_positions = []
        for entry_order, out_order in grouped_order:
            open_time = bt.num2date(entry_order.executed.dt)
            close_time = bt.num2date(out_order.executed.dt)
            pnl = pnl_map[entry_order.tradeid]
            action = "long" if entry_order.isbuy() else "short"
            strategy = entry_order.p.owner.name

            echarts_positions.append([
                {
                    'coord': [str(open_time), entry_order.executed.price],
                    'name': '{} {} {}'.format(strategy, action, pnl),
                    'itemStyle': {
                        'color': '#3ea869' if pnl > 0 else '#f64e56',
                    },
                    '_ts': open_time.timestamp(),
                    '_st': strategy
                },
                {'coord': [str(close_time), out_order.executed.price], 'PnL': pnl}
            ])

        performance = Report.get_performance(cerebro.df, grouped_order, pnl_map)

        mark_line = []
        mark_point = []
        for st in cerebro.back:
            if getattr(st, '_mark_line', None):
                mark_line += st._mark_line
            if getattr(st, '_mark_point', None):
                mark_point += st._mark_point

        data_json = {
            "positions": echarts_positions,
            "performance": performance,
            "strategy_params": [{'name': st.name, **st.params.__dict__} for st in cerebro.back],
            "mark_line": mark_line,
            "mark_point": mark_point
        }

        return data_json
        # 将数据保存为JSON文件
