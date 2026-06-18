import plotly.graph_objects as go
import streamlit as st

from analyzer import analyze

st.set_page_config(page_title="价值投资分析器", page_icon="📈", layout="centered")

st.title("📈 上市公司价值投资分析器")
st.caption("基于巴菲特式经典指标（ROE、毛利率、负债率、自由现金流等），数据来源 Yahoo Finance")

ticker = st.text_input(
    "输入股票代码",
    value="AAPL",
    help="美股如 AAPL、MSFT；港股如 0700.HK；A股如 600519.SS / 000001.SZ",
)

if st.button("开始分析", type="primary") and ticker:
    with st.spinner("正在获取数据并分析..."):
        try:
            result = analyze(ticker.strip())
        except Exception as e:
            st.error(str(e))
            st.stop()

    st.subheader(f"{result.company_name} ({result.ticker})")

    pct = result.score / result.max_score
    st.metric("综合得分", f"{result.score} / {result.max_score}")
    st.progress(pct)

    if pct >= 0.75:
        st.success(result.verdict)
    elif pct >= 0.5:
        st.warning(result.verdict)
    else:
        st.error(result.verdict)

    st.markdown("### 指标明细")
    for c in result.criteria:
        icon = "✅" if c.passed else "❌"
        with st.expander(f"{icon} {c.name}：{c.value}"):
            st.write(c.note)

    if result.history is not None and not result.history.empty:
        st.markdown("### 近5年股价走势")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=result.history.index, y=result.history["Close"], mode="lines", name="收盘价"
        ))
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("免责声明：本工具仅供学习研究参考，不构成任何投资建议。")
