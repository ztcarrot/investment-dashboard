#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资组合仪表盘 - 主应用
"""

import streamlit as st
import os
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="投资组合仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'assets' not in st.session_state:
    # 从 Streamlit Secrets 读取资产配置
    if hasattr(st, 'secrets') and 'assets' in st.secrets:
        assets_data = st.secrets['assets']

        # 判断配置类型
        if isinstance(assets_data, str):
            # Streamlit Cloud: JSON 字符串格式
            import json
            try:
                st.session_state.assets = json.loads(assets_data)
            except json.JSONDecodeError:
                st.error("❌ Secrets 配置格式错误：assets 必须是有效的 JSON 数组")
                st.session_state.assets = []
        elif isinstance(assets_data, list):
            # 本地开发: 已经解析的列表
            st.session_state.assets = assets_data
        else:
            st.error(f"❌ 未知的配置格式: {type(assets_data)}")
            st.session_state.assets = []
    else:
        st.session_state.assets = []
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = None


def main():
    """主函数"""

    # 侧边栏
    with st.sidebar:
        st.title("📊 投资组合仪表盘")
        st.markdown("---")

        # 项目信息
        st.markdown("""
        ### 功能模块

        - 📊 **仪表盘** - 查看投资组合概览
        - ⚙️ **配置管理** - 管理投资标的配置
        - 📈 **数据分析** - 深度数据分析

        ---
        """)

        # 数据状态
        if st.session_state.assets:
            st.success(f"✅ 已配置 {len(st.session_state.assets)} 个标的")
        else:
            st.info("⚠️ 尚未配置任何标的")

        st.markdown("---")

        # 关于
        st.markdown("""
        ### 关于

        本项目用于追踪和分析投资组合表现，
        支持多种资产类型和历史数据分析。

        **技术栈**: Streamlit + Pandas + Plotly
        """)

    # 主标题
    st.markdown('<h1 class="main-header">投资组合仪表盘</h1>', unsafe_allow_html=True)

    # 说明信息
    if not st.session_state.assets:
        st.info("""
        👋 欢迎使用投资组合仪表盘！

        请先在 **⚙️ 配置管理** 页面添加你的投资标的，
        然后系统会自动抓取数据并生成分析图表。

        开始使用：
        1. 点击左侧菜单的 **⚙️ 配置管理**
        2. 添加你的投资标的
        3. 返回 **📊 仪表盘** 查看分析
        """, icon="👋")
    else:
        # 显示快速统计
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("配置标的", f"{len(st.session_state.assets)} 个")

        with col2:
            asset_types = set([asset.get('资产类别', '股票') for asset in st.session_state.assets])
            st.metric("资产类别", f"{len(asset_types)} 类")

        with col3:
            total_shares = sum([asset.get('初始份额', 0) for asset in st.session_state.assets])
            st.metric("总份额", f"{total_shares:,.2f}")

        with col4:
            st.metric("数据状态", "✅ 就绪" if st.session_state.historical_data is not None else "⏳ 待更新")

        st.markdown("---")

        # 操作提示
        st.markdown("""
        ### 🚀 快速开始

        1. **查看仪表盘** - 查看投资组合概览和图表
        2. **管理配置** - 添加、编辑或删除投资标的
        3. **数据分析** - 深度分析收益率和资产配置

        点击左侧菜单开始探索！
        """)


if __name__ == "__main__":
    main()
