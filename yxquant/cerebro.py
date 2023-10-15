import time

import backtrader as bt
from yxquant.trading import Trading, Report
from yxquant.analyzer import PnlAnalysis, ParamsOpt
import http.server
import socketserver
import webbrowser
import json


class Cerebro(bt.Cerebro):
    def __init__(self):
        super().__init__()
        self.init_project()
        self.df = None
        self.back = None
        self.opt_params = None

    def init_project(self):
        self.addanalyzer(PnlAnalysis, _name='pnl_analysis')

    def run(self, *args, **kwargs):
        self.back = super().run(*args, **kwargs)
        return self.back

    def plot(self, port=2918):
        import os
        dist_dir = os.path.dirname(os.path.abspath(__file__)) + '/dist'

        if self.opt_params:
            back = ParamsOpt(self.back, self.opt_params)
            performance = back.params_performance()
            curve = back.params_pnl_curve()
            analysis = {"lines": curve, "table": performance}
            with open(f"{dist_dir}/optimizing_report.json", "w") as outfile:
                json.dump(analysis, outfile)
            url = f"Web: http://localhost:{port}?optimizing=1"

        else:
            data_json = Report.create_report(self)
            fmt_df = self.df.reset_index()[['date', 'open', 'high', 'low', 'close', 'volume']]
            fmt_df['date'] = fmt_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            stock_data = {'stock_data': fmt_df.values.tolist()}

            with open(f"{dist_dir}/stock_data.json", "w") as outfile:
                json.dump(stock_data, outfile)
            with open(f"{dist_dir}/trade_data.json", "w") as outfile:
                json.dump(data_json, outfile)
            with open(f"{dist_dir}/indicator_data.json", "w") as outfile:
                json.dump({}, outfile)
            url = f"Web: http://localhost:{port}"

        os.chdir(dist_dir)

        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(url)
            time.sleep(2)
            webbrowser.open(url)
            httpd.serve_forever()

    def adddata(self, df):
        self.df = df
        super().adddata(bt.feeds.PandasData(dataname=self.df))

    def addalert(self, signal_webhook=None, trading_webhook=None):
        # Discord alert
        Trading.LIVE = True
        Trading.SIGNAL_WEBHOOK_URL = signal_webhook
        Trading.TRADE_WEBHOOK_URL = trading_webhook

    def optparams(self, strategy, params):
        self.opt_params = params
        self.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
        self.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.addanalyzer(bt.analyzers.Returns, _name="returns")
        self.addanalyzer(PnlAnalysis, _name='pnl_analysis')
        super().optstrategy(strategy, **params)


