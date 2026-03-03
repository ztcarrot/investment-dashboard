#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表盘页面
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

try:
    from utils.data_fetcher import DataFetcher
except ImportError:
    import sys
    from pathlib import Path
    # 添加项目根目录到 Python 路径
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.data_fetcher import DataFetcher


@st.cache_data(ttl=3600)
def load_data():
    """加载或抓取数据"""
    assets = st.session_state.get('assets', [])

    if not assets:
        return None, None

    # 计算日期范围（最近60天）
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

    # 抓取数据
    fetcher = DataFetcher()

    with st.spinner("🔄 正在抓取数据..."):
        historical_data = fetcher.fetch_all_assets_data(assets, start_date, end_date)

    if historical_data.empty:
        return None, None

    # 生成组合数据
    portfolio_data = fetcher.get_portfolio_summary(historical_data)

    return historical_data, portfolio_data


def render_total_assets_chart(portfolio_data):
    """渲染总资产走势图"""
    if portfolio_data is None or portfolio_data.empty:
        return

    fig = go.Figure()

    # 添加总资产折线
    fig.add_trace(go.Scatter(
        x=portfolio_data['日期'],
        y=portfolio_data['总资产'],
        mode='lines+markers',
        name='总资产',
        line=dict(color='#d62728', width=3),
        marker=dict(size=6),
        hovertemplate='%{x}<br>总资产: ¥%{y:,.2f}<extra></extra>'
    ))

    # 添加趋势线
    if len(portfolio_data) > 1:
        import numpy as np
        x = list(range(len(portfolio_data)))
        y = portfolio_data['总资产'].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        trend_line = p(x)

        fig.add_trace(go.Scatter(
            x=portfolio_data['日期'],
            y=trend_line,
            mode='lines',
            name='趋势线',
            line=dict(color='gray', width=2, dash='dash'),
            hovertemplate='趋势: ¥%{y:,.2f}<extra></extra>'
        ))

    fig.update_layout(
        title="总资产走势",
        xaxis_title="日期",
        yaxis_title="总资产（元）",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def render_allocation_chart(portfolio_data):
    """渲染资产配置图"""
    if portfolio_data is None or portfolio_data.empty:
        return

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('资产金额分布', '资产占比分布'),
        specs=[[{'type': 'pie'}, {'type': 'pie'}]]
    )

    latest = portfolio_data.iloc[-1]

    # 资产金额饼图
    fig.add_trace(
        go.Pie(
            labels=['股票', '黄金', '现金', '国债'],
            values=[latest['股票'], latest['黄金'], latest['现金'], latest['国债']],
            name="金额",
            textinfo='label+percent',
            texttemplate='%{label}<br>¥%{value:,.0f}<br>(%{percent})'
        ),
        row=1, col=1
    )

    # 资产占比饼图
    fig.add_trace(
        go.Pie(
            labels=['股票', '黄金', '现金', '国债'],
            values=[latest['股票占比'], latest['黄金占比'], latest['现金占比'], latest['国债占比']],
            name="占比",
            textinfo='label+percent',
            texttemplate='%{label}<br>%{percent}'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title_text="当前资产配置",
        template='plotly_white',
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_asset_performance(historical_data):
    """渲染各标的收益表现"""
    if historical_data is None or historical_data.empty:
        return

    # 按资产类型分组
    asset_types = historical_data['资产类型'].unique()

    for asset_type in asset_types:
        st.markdown(f"### {asset_type}类标的走势")

        # 获取该资产类型的所有数据
        asset_data = historical_data[historical_data['资产类型'] == asset_type]

        # 按标的分组绘制折线图
        fig = go.Figure()

        for asset_name in asset_data['名称'].unique():
            asset_subset = asset_data[asset_data['名称'] == asset_name]

            fig.add_trace(go.Scatter(
                x=asset_subset['日期'],
                y=asset_subset['当前市值'],
                mode='lines+markers',
                name=asset_name,
                line=dict(width=2),
                marker=dict(size=4),
                hovertemplate='%{x}<br>%{fullData.name}: ¥%{y:,.2f}<extra></extra>'
            ))

        fig.update_layout(
            title=f"{asset_type}类标的市值走势",
            xaxis_title="日期",
            yaxis_title="市值（元）",
            hovermode='x unified',
            template='plotly_white',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)


def render_data_table(historical_data, portfolio_data):
    """渲染完整数据表格"""
    if historical_data is None or historical_data.empty:
        return

    st.subheader("📊 历史数据")

    # 按日期透视表格
    pivot_data = historical_data.pivot_table(
        index='日期',
        columns='名称',
        values='当前市值',
        aggfunc='sum'
    )

    st.dataframe(
        pivot_data.style.format('¥{:,.2f}'),
        use_container_width=True,
        height=400
    )

    st.markdown("---")

    st.subheader("📈 资产组合汇总")

    # 显示汇总数据
    display_df = portfolio_data.copy()
    display_df['日期'] = pd.to_datetime(display_df['日期']).dt.strftime('%Y-%m-%d')
    display_df['总资产'] = display_df['总资产'].apply(lambda x: f'¥{x:,.2f}')
    display_df['股票'] = display_df['股票'].apply(lambda x: f'¥{x:,.2f}')
    display_df['黄金'] = display_df['黄金'].apply(lambda x: f'¥{x:,.2f}')
    display_df['现金'] = display_df['现金'].apply(lambda x: f'¥{x:,.2f}')
    display_df['国债'] = display_df['国债'].apply(lambda x: f'¥{x:,.2f}')

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def main():
    """主函数"""

    st.title("📊 投资组合仪表盘")
    st.markdown("---")

    # 检查是否有配置
    assets = st.session_state.get('assets', [])

    if not assets:
        st.warning("⚠️ 尚未配置任何资产，请先到 **⚙️ 配置管理** 页面添加资产")
        return

    # 数据抓取按钮
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.info(f"📌 当前已配置 {len(assets)} 个资产")

    with col2:
        if st.button("🔄 刷新数据", type="primary"):
            st.cache_data.clear()
            st.rerun()

    with col3:
        # 日期范围选择
        date_range = st.selectbox(
            "数据范围",
            options=["最近30天", "最近60天", "最近90天"],
            index=1
        )

    st.markdown("---")

    # 加载数据
    historical_data, portfolio_data = load_data()

    if historical_data is None or portfolio_data is None:
        st.error("❌ 数据加载失败，请检查网络连接或配置")
        return

    # 统计卡片
    latest = portfolio_data.iloc[-1]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # 显示最后一天相比前一天的变化
        if len(portfolio_data) >= 2:
            previous_value = portfolio_data['总资产'].iloc[-2]
            daily_change = ((latest['总资产'] - previous_value) / previous_value * 100)
            st.metric("总资产", f"¥{latest['总资产']:,.2f}", f"{daily_change:+.2f}%")
        else:
            st.metric("总资产", f"¥{latest['总资产']:,.2f}")

    with col2:
        if len(portfolio_data) >= 2:
            previous_stock = portfolio_data['股票'].iloc[-2]
            stock_change = ((latest['股票'] - previous_stock) / previous_stock * 100) if previous_stock > 0 else 0
            st.metric("股票占比", f"{latest['股票占比']:.2f}%", f"{stock_change:+.2f}%")
        else:
            st.metric("股票占比", f"{latest['股票占比']:.2f}%", f"¥{latest['股票']:,.2f}")

    with col3:
        if len(portfolio_data) >= 2:
            previous_gold = portfolio_data['黄金'].iloc[-2]
            gold_change = ((latest['黄金'] - previous_gold) / previous_gold * 100) if previous_gold > 0 else 0
            st.metric("黄金占比", f"{latest['黄金占比']:.2f}%", f"{gold_change:+.2f}%")
        else:
            st.metric("黄金占比", f"{latest['黄金占比']:.2f}%", f"¥{latest['黄金']:,.2f}")

    with col4:
        if len(portfolio_data) >= 2:
            previous_cash = portfolio_data['现金'].iloc[-2]
            cash_change = ((latest['现金'] - previous_cash) / previous_cash * 100) if previous_cash > 0 else 0
            st.metric("现金占比", f"{latest['现金占比']:.2f}%", f"{cash_change:+.2f}%")
        else:
            st.metric("现金占比", f"{latest['现金占比']:.2f}%", f"¥{latest['现金']:,.2f}")

    with col5:
        if len(portfolio_data) >= 2:
            previous_bond = portfolio_data['国债'].iloc[-2]
            bond_change = ((latest['国债'] - previous_bond) / previous_bond * 100) if previous_bond > 0 else 0
            st.metric("国债占比", f"{latest['国债占比']:.2f}%", f"{bond_change:+.2f}%")
        else:
            st.metric("国债占比", f"{latest['国债占比']:.2f}%", f"¥{latest['国债']:,.2f}")

    st.markdown("---")

    # 图表
    tab1, tab2, tab3, tab4 = st.tabs(["📈 总资产走势", "🥧 资产配置", "📊 标的表现", "📋 数据表格"])

    with tab1:
        render_total_assets_chart(portfolio_data)

    with tab2:
        render_allocation_chart(portfolio_data)

    with tab3:
        render_asset_performance(historical_data)

    with tab4:
        render_data_table(historical_data, portfolio_data)


if __name__ == "__main__":
    main()
