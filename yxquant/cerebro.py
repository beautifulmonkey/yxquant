import backtrader as bt
from yxquant.yxquant.trading import Trading, Report
from yxquant.yxquant.analyzer import PnlAnalysis
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

    def init_project(self):
        self.addanalyzer(PnlAnalysis, _name='pnl_analysis')

    def run(self, *args, **kwargs):
        self.back = super().run(*args, **kwargs)
        return self.back

    def plot(self, port=2918):
        import os
        data_json = Report.export_result_to_json(self)

        fmt_df = self.df.reset_index()[['date', 'open', 'high', 'low', 'close', 'volume']]
        fmt_df['date'] = fmt_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        stock_data = {'stock_data': fmt_df.values.tolist()}

        # 指定你的dist文件夹的路径
        dist_dir = os.path.dirname(os.path.abspath(__file__)) + '/dist'

        # 保存交易结果
        with open(f"{dist_dir}/stock_data.json", "w") as outfile:
            json.dump(stock_data, outfile)

        with open(f"{dist_dir}/trade_data.json", "w") as outfile:
            json.dump(data_json, outfile)

        with open(f"{dist_dir}/indicator_data.json", "w") as outfile:
            json.dump({}, outfile)

        os.chdir(dist_dir)

        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            url = f"Web: http://localhost:{port}"
            print(url)
            webbrowser.open(url)
            httpd.serve_forever()

    def adddata(self, df):
        self.df = df
        super().adddata(bt.feeds.PandasData(dataname=self.df))