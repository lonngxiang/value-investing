"""Batch screen a list of tickers with the Buffett-style analyzer and print a ranked table."""

import argparse
import sys

from analyzer import analyze

DEFAULT_TICKERS = [
    "AAPL", "MSFT", "JNJ", "KO", "V",
    "0700.HK", "0941.HK", "1299.HK", "0005.HK", "2318.HK",
]


def screen(tickers):
    results = []
    for ticker in tickers:
        try:
            result = analyze(ticker)
            results.append(result)
        except Exception as e:
            print(f"[跳过] {ticker}: {e}", file=sys.stderr)
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def print_table(results):
    header = f"{'代码':<10}{'公司':<30}{'得分':<10}{'结论'}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r.ticker:<10}{r.company_name:<30}{f'{r.score}/{r.max_score}':<10}{r.verdict}")


def main():
    parser = argparse.ArgumentParser(description="批量筛选股票是否值得价值投资")
    parser.add_argument(
        "tickers", nargs="*", default=DEFAULT_TICKERS,
        help="股票代码列表，留空则使用默认的美股蓝筹+港股恒生成分股清单",
    )
    args = parser.parse_args()
    results = screen(args.tickers)
    print_table(results)


if __name__ == "__main__":
    main()
