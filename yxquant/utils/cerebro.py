import pickle
import time
import os
import json
import itertools
import backtrader as bt
from tqdm import tqdm
from typing import List, Dict
from backtrader import observers
from backtrader.utils.py3 import integer_types
from backtrader.utils import tzparse
from yxquant.profiles import RunningMode

class OptReturn(object):
    def __init__(self, params, **kwargs):
        self.p = self.params = params
        for k, v in kwargs.items():
            setattr(self, k, v)

class FusionCerebro(bt.Cerebro):
    params = (
        ('running_mode', RunningMode.BACKTEST),
        ('enable_cache', False),
        ('output_path', 'runs'),
    )
    tqdm: tqdm = None

    def load_data_from_pickle(self, path="cache_datas.pkl"):
        ''' add from pickle'''
        try:
            with open(path, "rb") as f:
                _data = pickle.load(f)
        except AttributeError as e:
            raise Exception(f"缓存失效, 请删除缓存后重新运行! {e}")
        return _data

    def _get_cache_path(self):
        cache_dir = os.path.join(self.p.output_path, 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, 'cache_datas.pkl')

    def _get_cache_info_path(self):
        cache_dir = os.path.join(self.p.output_path, 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, 'cache_info.json')

    def _preload_all_datas(self):
        begin_time = time.time()
        for data in self.datas:
            data.reset()
            if self._exactbars < 1:  # datas can be full length
                data.extend(size=self.params.lookahead)
            data._start()
            if self._dopreload:
                data.preload()
        end_time = time.time()
        return int(end_time - begin_time)

    def _collect_feed_metadata(self):
        meta_list = list()
        for feed in self.datas:
            _datetime_array = feed.p.dataname.index.tolist()
            _close_array = feed.p.dataname.close.tolist()
            name = getattr(feed, '_name', None)

            length = len(_datetime_array)
            start_datetime = str(_datetime_array[0])
            end_datetime = str(_datetime_array[-1])
            first_close = _close_array[0]
            last_close = _close_array[-1]
            meta = {
                'name': name,
                'length': length,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'first_close': first_close,
                'last_close': last_close,
            }
            meta_list.append(meta)
        return meta_list

    def _read_cache_info(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_cache_info(self, path, meta_list):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(meta_list, f, ensure_ascii=False, indent=4)

    def _cache_meta_matches(self, current_meta, cached_meta):
        if not isinstance(cached_meta, list) or len(current_meta) != len(cached_meta):
            return False
        for cur, old in zip(current_meta, cached_meta):
            keys = set(cur.keys()) | set(old.keys())
            for k in keys:
                if cur.get(k) != old.get(k):
                    return False
        return True

    def optstrategy_combos(self, strategy, *args, kwcombos: List[Dict]):
        """
            用于分批优化, 解决backtrader内存泄露问题
            :param kwcombos: e.g. [{period: 14, stop_loss: 20}, {period: 30, stop_loss: 15}, ...]
        """
        self._dooptimize = True
        args = self.iterize(args)
        optargs = itertools.product(*args) if args else [()]
        # 生成器，惰性加载
        optkwargs = (k for k in kwcombos)
        it = itertools.product([strategy], optargs, optkwargs)
        self.strats.append(it)


    def runstrategies(self, iterstrat, predata=False):
        '''
        Internal method invoked by ``run``` to run a set of strategies
        '''
        self._init_stcount()

        self.runningstrats = runstrats = list()
        for store in self.stores:
            store.start()

        if self.p.cheat_on_open and self.p.broker_coo:
            # try to activate in broker
            if hasattr(self._broker, 'set_coo'):
                self._broker.set_coo(True)

        if self._fhistory is not None:
            self._broker.set_fund_history(self._fhistory)

        for orders, onotify in self._ohistory:
            self._broker.add_order_history(orders, onotify)

        self._broker.start()

        for feed in self.feeds:
            feed.start()

        if self.writers_csv:
            wheaders = list()
            for data in self.datas:
                if data.csv:
                    wheaders.extend(data.getwriterheaders())

            for writer in self.runwriters:
                if writer.p.csv:
                    writer.addheaders(wheaders)

        # self._plotfillers = [list() for d in self.datas]
        # self._plotfillers2 = [list() for d in self.datas]

        if not predata:
            if self.p.enable_cache:
                cache_path = self._get_cache_path()
                info_path = self._get_cache_info_path()
                use_cache = False
                if os.path.exists(cache_path) and os.path.exists(info_path):
                    cached_info = self._read_cache_info(info_path)
                    current_info = self._collect_feed_metadata()
                    if cached_info and self._cache_meta_matches(current_info, cached_info):
                        use_cache = True
                if use_cache:
                    print("Loading cache")
                    self.datas = self.load_data_from_pickle(cache_path)
                else:
                    consume_time = self._preload_all_datas()
                    print("Generating cache, Approx. {}S saved".format(consume_time))
                    with open(cache_path, 'wb') as f:
                        pickle.dump(self.datas, f)
                    self._write_cache_info(info_path, self._collect_feed_metadata())
            else:
                self._preload_all_datas()

        if self.p.running_mode == RunningMode.BACKTEST:
            self.tqdm = tqdm(total=len(self.datas[0].array) * len(self.strats),  desc="Backtesting 🚀🚀🚀")

        for stratcls, sargs, skwargs in iterstrat:
            sargs = self.datas + list(sargs)
            try:
                strat = stratcls(*sargs, **skwargs)
            except bt.errors.StrategySkipError:
                continue  # do not add strategy to the mix

            if self.p.oldsync:
                strat._oldsync = True  # tell strategy to use old clock update
            if self.p.tradehistory:
                strat.set_tradehistory()
            runstrats.append(strat)

        tz = self.p.tz
        if isinstance(tz, integer_types):
            tz = self.datas[tz]._tz
        else:
            tz = tzparse(tz)

        if runstrats:
            # loop separated for clarity
            defaultsizer = self.sizers.get(None, (None, None, None))
            for idx, strat in enumerate(runstrats):
                if self.p.stdstats:
                    strat._addobserver(False, observers.Broker)
                    if self.p.oldbuysell:
                        strat._addobserver(True, observers.BuySell)
                    else:
                        strat._addobserver(True, observers.BuySell,
                                           barplot=True)

                    if self.p.oldtrades or len(self.datas) == 1:
                        strat._addobserver(False, observers.Trades)
                    else:
                        strat._addobserver(False, observers.DataTrades)

                for multi, obscls, obsargs, obskwargs in self.observers:
                    strat._addobserver(multi, obscls, *obsargs, **obskwargs)

                for indcls, indargs, indkwargs in self.indicators:
                    strat._addindicator(indcls, *indargs, **indkwargs)

                for ancls, anargs, ankwargs in self.analyzers:
                    strat._addanalyzer(ancls, *anargs, **ankwargs)

                sizer, sargs, skwargs = self.sizers.get(idx, defaultsizer)
                if sizer is not None:
                    strat._addsizer(sizer, *sargs, **skwargs)

                strat._settz(tz)
                strat._start()

                for writer in self.runwriters:
                    if writer.p.csv:
                        writer.addheaders(strat.getwriterheaders())

            if not predata:
                for strat in runstrats:
                    strat.qbuffer(self._exactbars, replaying=self._doreplay)

            for writer in self.runwriters:
                writer.start()

            # Prepare timers
            self._timers = []
            self._timerscheat = []
            for timer in self._pretimers:
                # preprocess tzdata if needed
                timer.start(self.datas[0])

                if timer.params.cheat:
                    self._timerscheat.append(timer)
                else:
                    self._timers.append(timer)

            if self._dopreload and self._dorunonce:
                if self.p.oldsync:
                    self._runonce_old(runstrats)
                else:
                    self._runonce(runstrats)
            else:
                if self.p.oldsync:
                    self._runnext_old(runstrats)
                else:
                    self._runnext(runstrats)

            for strat in runstrats:
                strat._stop()

        self._broker.stop()

        if not predata:
            for data in self.datas:
                data.stop()

        for feed in self.feeds:
            feed.stop()

        for store in self.stores:
            store.stop()

        self.stop_writers(runstrats)

        if self._dooptimize and self.p.optreturn:
            # Results can be optimized
            results = list()
            for strat in runstrats:
                for a in strat.analyzers:
                    a.strategy = None
                    a._parent = None
                    for attrname in dir(a):
                        if attrname.startswith('data'):
                            setattr(a, attrname, None)

                oreturn = OptReturn(strat.params, analyzers=strat.analyzers, strategycls=type(strat))
                results.append(oreturn)

            return results

        if self.tqdm:
            self.tqdm.close()

        return runstrats


