# 价值投资分析器

基于巴菲特式经典指标分析上市公司是否值得价值投资，数据来源 [yfinance](https://pypi.org/project/yfinance/)（Yahoo Finance）。

## 评分指标

- ROE（净资产收益率）> 15%
- 毛利率 > 40%
- 负债权益比 < 80%
- 自由现金流为正
- 营业利润率 > 15%
- 市盈率 PE(TTM) < 25
- 市净率 PB < 5
- 营收同比增长 > 0
- 流动比率 > 1.5

按通过项数给出综合得分与结论（值得关注 / 中性 / 暂不建议）。

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

支持代码示例：美股 `AAPL`、`MSFT`；港股 `0700.HK`；A股 `600519.SS` / `000001.SZ`。

## 免责声明

本工具仅供学习研究参考，不构成任何投资建议。
