# yxquant(云霄量化)
适用Day Trade级别回测 / 实时交易框架, 基于Backtrader, 其中包含了:
- Day Trade交易偏好
  - 不同时段交易配置
  - 跟踪止损配置
  - 仓位管理
- 回测报告可视化
- 参数优化结果可视化
- 接入IB(盈透证券)实时交易
- Discord实时交易提醒

# 安装

```
pip install git+https://github.com/beautifulmonkey/yxquant.git
```

# 回测

```
cd examples
python backtest.py
```


#### 运行完毕后访问: http://localhost:2918

#### 将会看到交易记录, 以及结果分析
![Alt text](./img/img.png)
![Alt text](./img/img_1.png)

