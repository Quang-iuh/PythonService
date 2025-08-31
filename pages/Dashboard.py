import streamlit as st
import pandas as pd
import plotly.express as px
from utils.qr_storage import load_qr_data  # Import hàm load dữ liệu từ file JSON

# --- Cấu hình trang ---
st.set_page_config(
    page_title="📊 Thống kê & Báo cáo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS tùy chỉnh ---
st.markdown("""    
<style>    
    .main-header {    
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);    
        padding: 1.5rem;    
        border-radius: 10px;    
        color: white;    
        text-align: center;    
        margin-bottom: 2rem;    
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);    
    }    

    .metric-card {    
        background: #ffffff;    
        border: 1px solid #e1e5e9;    
        border-radius: 10px;    
        padding: 1.5rem;    
        margin: 0.5rem 0;    
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);    
        text-align: center;    
    }    

    .metric-value {    
        font-size: 2.5rem;    
        font-weight: bold;    
        color: #2c3e50;    
        margin-bottom: 0.5rem;    
    }    

    .metric-label {    
        color: #6c757d;    
        font-size: 1rem;    
    }    

    .chart-container {    
        background: #ffffff;    
        border: 1px solid #e1e5e9;    
        border-radius: 10px;    
        padding: 1.5rem;    
        margin: 1rem 0;    
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);    
    }    

    .data-table {    
        border: 1px solid #dee2e6;    
        border-radius: 8px;    
        overflow: hidden;    
    }    

    .sidebar-section {    
        background: #f8f9fa;    
        padding: 1rem;    
        border-radius: 8px;    
        margin: 1rem 0;    
        border-left: 4px solid #667eea;    
    }    
</style>    
""", unsafe_allow_html=True)

# --- Header chính ---
st.markdown("""    
<div class="main-header">    
    <h1>📊 THỐNG KÊ & BÁO CÁO</h1>    
    <p>Phân tích dữ liệu quét mã QR theo thời gian thực</p>    
</div>    
""", unsafe_allow_html=True)

# --- Kiểm tra đăng nhập ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# --- Load dữ liệu từ file JSON ---
try:
    qr_history = load_qr_data()  # Thay thế st.session_state.qr_history
except Exception as e:
    st.error(f"Lỗi khi tải dữ liệu: {e}")
    qr_history = []

# --- Tính toán thống kê ---
total_scans = len(qr_history)

# Tách dữ liệu theo miền
unique_north = {item["data"] for item in qr_history if item["region"] == "Miền Bắc"}
unique_central = {item["data"] for item in qr_history if item["region"] == "Miền Trung"}
unique_south = {item["data"] for item in qr_history if item["region"] == "Miền Nam"}
unique_other = {item["data"] for item in qr_history if item["region"] == "Miền khác"}

unique_scans = len(unique_north | unique_central | unique_south | unique_other)

# --- Metrics Dashboard ---
st.markdown("## 📈 Tổng quan thống kê")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""    
    <div class="metric-card">    
        <div class="metric-value">{total_scans}</div>    
        <div class="metric-label">Tổng số quét</div>    
    </div>    
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""    
    <div class="metric-card">    
        <div class="metric-value">{unique_scans}</div>    
        <div class="metric-label">Mã duy nhất</div>    
    </div>    
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""    
    <div class="metric-card">    
        <div class="metric-value">{len(unique_north)}</div>    
        <div class="metric-label">Miền Bắc</div>    
    </div>    
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""    
    <div class="metric-card">    
        <div class="metric-value">{len(unique_central)}</div>    
        <div class="metric-label">Miền Trung</div>    
    </div>    
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""    
    <div class="metric-card">    
        <div class="metric-value">{len(unique_south)}</div>    
        <div class="metric-label">Miền Nam</div>    
    </div>    
    """, unsafe_allow_html=True)

# --- Layout 2 cột cho biểu đồ ---
if qr_history:  # Thay đổi từ st.session_state.qr_history
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("""    
        <div class="chart-container">    
            <h3>📊 Phân bố theo miền</h3>    
        </div>    
        """, unsafe_allow_html=True)

        # Pie chart
        chart_data = {
            'Miền': ['Miền Bắc', 'Miền Trung', 'Miền Nam', 'Miền khác'],
            'Số lượng': [len(unique_north), len(unique_central), len(unique_south), len(unique_other)]
        }
        df_chart = pd.DataFrame(chart_data)
        df_chart = df_chart[df_chart['Số lượng'] > 0]

        if not df_chart.empty:
            fig_pie = px.pie(df_chart, values='Số lượng', names='Miền',
                             color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c'])
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("""    
        <div class="chart-container">    
            <h3>📈 Biểu đồ cột</h3>    
        </div>    
        """, unsafe_allow_html=True)

        # Bar chart
        if not df_chart.empty:
            fig_bar = px.bar(df_chart, x='Miền', y='Số lượng',
                             color='Miền',
                             color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c'])
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- Bảng dữ liệu chi tiết ---
    st.markdown("## 📋 Lịch sử quét chi tiết")

    df = pd.DataFrame(qr_history)  # Thay đổi từ st.session_state.qr_history

    # Filters
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        region_filter = st.selectbox(
            "Lọc theo miền:",
            ["Tất cả"] + list(df['region'].unique()) if not df.empty else ["Tất cả"]
        )

    with col_filter2:
        if not df.empty:
            date_filter = st.date_input("Lọc theo ngày:", value=None)

            # Apply filters
    filtered_df = df.copy()
    if region_filter != "Tất cả" and not df.empty:
        filtered_df = filtered_df[filtered_df['region'] == region_filter]

        # Display table
    if not filtered_df.empty:
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            filtered_df[['data', 'region', 'time']],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống CSV",
            data=csv,
            file_name=f"qr_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("🔍 Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")

else:
    st.info("🔍 Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""    
    <div class="sidebar-section">    
        <h3>👤 Người dùng</h3>    
        <p>Xin chào, <strong>{st.session_state.username}</strong></p>    
    </div>    
    """, unsafe_allow_html=True)

    st.markdown("""    
    <div class="sidebar-section">    
        <h3>📊 Thống kê nhanh</h3>    
    </div>    
    """, unsafe_allow_html=True)

    if qr_history:  # Thay đổi từ st.session_state.qr_history
        st.metric("Tổng quét", total_scans)
        st.metric("Mã duy nhất", unique_scans)

        # Tỷ lệ phần trăm
        if total_scans > 0:
            north_pct = round(len(unique_north) / unique_scans * 100, 1) if unique_scans > 0 else 0
            central_pct = round(len(unique_central) / unique_scans * 100, 1) if unique_scans > 0 else 0
            south_pct = round(len(unique_south) / unique_scans * 100, 1) if unique_scans > 0 else 0

            st.write("**Tỷ lệ theo miền:**")
            st.write(f"🔵 Miền Bắc: {north_pct}%")
            st.write(f"🟡 Miền Trung: {central_pct}%")
            st.write(f"🔴 Miền Nam: {south_pct}%")

    st.markdown("---")

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/login.py")