#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理页面 - 从 Streamlit Secrets 读取配置
"""

import streamlit as st
import pandas as pd


def main():
    """主函数"""

    st.title("⚙️ 配置管理")
    st.markdown("---")

    # 加载配置（从 session_state 或 secrets）
    assets = st.session_state.get('assets', [])

    # 显示配置说明
    st.info("""
    💡 **配置说明**

    本应用从 **Streamlit Secrets** 读取资产配置。Secrets 是只读的，不能在页面中直接修改。

    **如何配置**：
    1. 在本地开发：创建 `.streamlit/secrets.toml` 文件
    2. 在 Streamlit Cloud：在 Settings → Secrets 中添加配置

    配置格式示例：
    ```toml
    _assets = [
        { 代码 = "510300", 名称 = "300ETF", 代码类型 = "股票", 资产类别 = "股票", 初始份额 = 2200.0, 备注 = "沪深300ETF" },
        { 代码 = "518660", 名称 = "工银黄金", 代码类型 = "股票", 资产类别 = "黄金", 初始份额 = 15700.0, 备注 = "黄金ETF" },
    ]
    ```
    """, icon="💡")

    st.markdown("---")

    # 显示当前配置
    st.subheader("📋 当前配置")

    if not assets:
        st.warning("⚠️ 未找到资产配置。请在 `.streamlit/secrets.toml` 或 Streamlit Cloud 的 Secrets 中添加配置。")

        # 显示配置示例
        st.markdown("### 📝 配置示例")

        st.code("""
# .streamlit/secrets.toml

_assets = [
    { 代码 = "510300", 名称 = "300ETF", 代码类型 = "股票", 资产类别 = "股票", 初始份额 = 2200.0, 备注 = "沪深300ETF" },
    { 代码 = "518660", 名称 = "工银黄金", 代码类型 = "股票", 资产类别 = "黄金", 初始份额 = 15700.0, 备注 = "黄金ETF" },
    { 代码 = "5350", 名称 = "短债基金", 代码类型 = "基金", 资产类别 = "现金", 初始份额 = 160000.0, 备注 = "短债基金" },
    { 代码 = "19789", 名称 = "25特国06", 代码类型 = "基金", 资产类别 = "国债", 初始份额 = 1000.0, 备注 = "特别国债" },
]
""", language="toml")

        st.markdown("""
**字段说明**：
- `代码` - 基金或股票代码
- `名称` - 标的名称
- `代码类型` - "基金" 或 "股票"
- `资产类别` - "股票"、"黄金"、"现金" 或 "国债"
- `初始份额` - 持有份额
- `备注` - 可选备注信息
        """)
    else:
        # 显示配置表格
        df = pd.DataFrame(assets)
        df.index += 1

        st.dataframe(
            df[['代码', '名称', '代码类型', '资产类别', '初始份额', '备注']],
            use_container_width=True,
            hide_index=True
        )

        # 统计信息
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总资产数", f"{len(assets)} 个")

        with col2:
            asset_types = set([a.get('资产类别', '股票') for a in assets])
            st.metric("资产类别", f"{len(asset_types)} 类")

        with col3:
            total_shares = sum([a.get('初始份额', 0) for a in assets])
            st.metric("总份额", f"{total_shares:,.2f}")

        with col4:
            # 按资产类型统计
            type_counts = {}
            for asset in assets:
                asset_type = asset.get('资产类别', '股票')
                type_counts[asset_type] = type_counts.get(asset_type, 0) + 1

            type_summary = ", ".join([f"{k}:{v}" for k, v in type_counts.items()])
            st.metric("资产分布", type_summary)

        # 显示详细配置
        st.markdown("---")
        st.subheader("📄 配置详情")

        for i, asset in enumerate(assets, 1):
            with st.expander(f"{i}. {asset['名称']} ({asset['代码']})"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"""
                    - **代码类型**: {asset['代码类型']}
                    - **资产类别**: {asset['资产类别']}
                    - **初始份额**: {asset['初始份额']:.2f}
                    - **备注**: {asset.get('备注', '无')}
                    """)

    st.markdown("---")

    # Streamlit Cloud 配置说明
    st.subheader("☁️ Streamlit Cloud 部署配置")

    st.markdown("""
**在 Streamlit Cloud 上配置 Secrets**：

1. 访问你的应用 workspace
2. 点击 **Settings** → **Secrets**
3. 添加一个新的 secret：
   - Key: `assets`
   - Value: 你的配置（TOML 格式，不要包含 `_assets = ` 部分）
4. 点击 **Save**
5. 重启应用

**Secret 配置格式**（只填写数组部分）：
```toml
[
    { 代码 = "510300", 名称 = "300ETF", 代码类型 = "股票", 资产类别 = "股票", 初始份额 = 2200.0, 备注 = "" },
    ...
]
```
    """)


if __name__ == "__main__":
    main()
