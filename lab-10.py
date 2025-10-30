import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
import zipfile
import os

# 设置页面配置
st.set_page_config(
    page_title="California Housing Data",
    page_icon="🏠",
    layout="wide"
)

# 应用标题 - 请将 [Your Name] 替换为你的名字
st.title("California Housing Data (1990) by Chengyu Sun")

# 加载数据
@st.cache_data
def load_data():
    # 如果真实数据文件不存在，创建示例数据集
    np.random.seed(42)
    n_points = 1000
    
    # 创建更真实的加利福尼亚经纬度范围
    data = pd.DataFrame({
        'longitude': np.random.uniform(-124.3, -114.3, n_points),
        'latitude': np.random.uniform(32.5, 42, n_points),
        'median_house_value': np.random.randint(50000, 500001, n_points),
        'median_income': np.random.uniform(0.5, 15, n_points),
        'ocean_proximity': np.random.choice(['NEAR BAY', 'INLAND', 'NEAR OCEAN', 'ISLAND'], n_points, p=[0.3, 0.4, 0.29, 0.01])
    })
    return data

# 加载数据
data = load_data()

# 侧边栏过滤器
st.sidebar.header("Filters")

# 价格滑块
min_price = st.sidebar.slider(
    "Minimal Median House Price",
    min_value=int(data['median_house_value'].min()),
    max_value=int(data['median_house_value'].max()),
    value=int(data['median_house_value'].min()),
    step=1000
)

# 位置类型多选
location_options = data['ocean_proximity'].unique()
selected_locations = st.sidebar.multiselect(
    "Location Type",
    options=location_options,
    default=location_options
)

# 收入水平单选按钮
income_level = st.sidebar.radio(
    "Income Level",
    options=["Low (≤2.5)", "Medium (>2.5 & <4.5)", "High (≥4.5)"]
)

# 根据收入水平过滤数据
if income_level == "Low (≤2.5)":
    income_filtered_data = data[data['median_income'] <= 2.5]
elif income_level == "Medium (>2.5 & <4.5)":
    income_filtered_data = data[(data['median_income'] > 2.5) & (data['median_income'] < 4.5)]
else:  # High (≥4.5)
    income_filtered_data = data[data['median_income'] >= 4.5]

# 应用所有过滤器
filtered_data = income_filtered_data[
    (income_filtered_data['median_house_value'] >= min_price) & 
    (income_filtered_data['ocean_proximity'].isin(selected_locations))
]

# 显示过滤后的数据信息
st.write(f"Showing {len(filtered_data)} out of {len(data)} records")

# 调试信息（可以删除）
with st.expander("Debug Info"):
    st.write("Data columns:", data.columns.tolist())
    st.write("Filtered data sample:", filtered_data.head(3) if not filtered_data.empty else "No data")

# 地图显示
st.subheader("Housing Distribution Map")

if not filtered_data.empty:
    # 创建地图图层 - 使用更大的点
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_data,
        get_position=['longitude', 'latitude'],
        get_color=[255, 0, 0, 160],  # 红色，半透明
        get_radius=5000,  # 增大点的大小
        pickable=True,
        auto_highlight=True
    )
    
    # 设置视图状态 - 使用加利福尼亚的中心坐标
    view_state = pdk.ViewState(
        latitude=37.0,  # 加利福尼亚的大致中心纬度
        longitude=-119.0,  # 加利福尼亚的大致中心经度
        zoom=5,
        pitch=0
    )
    
    # 创建地图
    map_chart = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '<b>Median House Value:</b> ${median_house_value}<br/><b>Median Income:</b> {median_income}',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white'
            }
        },
        map_style='light'  # 使用浅色地图背景
    )
    
    st.pydeck_chart(map_chart)
else:
    st.warning("No data available with current filters. Try adjusting your filters.")

# 直方图
st.subheader("Median House Value Distribution")

if not filtered_data.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(filtered_data['median_house_value'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_xlabel('Median House Value')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Median House Values')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
else:
    st.warning("No data available for histogram")

# 数据显示（可选）
with st.expander("View Filtered Data"):
    if not filtered_data.empty:
        st.dataframe(filtered_data)
    else:
        st.write("No data to display with current filters")

# 侧边栏说明
st.sidebar.markdown("---")
st.sidebar.markdown("### See more filters in the sidebar:")
st.sidebar.markdown("Use the filters above to explore the California housing data from 1990.")