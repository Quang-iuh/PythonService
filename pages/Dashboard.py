import streamlit as st
import pandas as pd
import plotly.express as px
from utils.qr_storage import load_qr_data, get_available_dates
from Component.Camera.CameraHeader import load_css
# Cấu hình trang
st.set_page_config(
    page_title="📊 Thống kê & Báo cáo",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_css("dashboard.css")
# CSS tùy chỉnh

# Header chính
st.markdown("""        
<div class="main-header">        
    <h1>📊 THỐNG KÊ & BÁO CÁO</h1>  
    <p>Phân tích dữ liệu quét mã QR theo thời gian thực</p>        
</div>        
""", unsafe_allow_html=True)
# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Date Filter
nav_col1, nav_col2= st.columns(2)
with nav_col1:
    st.markdown("""    
<div class="date-filter">    
    <h3>📅 Chọn ngày xem data</h3>    
</div>    
""", unsafe_allow_html=True)

    available_dates = get_available_dates()
with nav_col2:
    if available_dates:
        selected_date = st.selectbox(
        "Chọn ngày:",
        options=available_dates,
        format_func=lambda x: x.strftime("%Y-%m-%d (%A)"),
        index=0
    )
    # Load data theo ngày được chọn

        qr_history = load_qr_data(selected_date)
        st.info(f"📊 Hiển thị data ngày {selected_date.strftime('%Y-%m-%d')}: {len(qr_history)} QR codes")
    else:
        st.warning("Chưa có data nào")
        qr_history = []

# Tính toán thống kê
total_scans = len(qr_history)

# Tách dữ liệu theo miền
unique_north = {item["data"] for item in qr_history if item["region"] == "Miền Bắc"}
unique_central = {item["data"] for item in qr_history if item["region"] == "Miền Trung"}
unique_south = {item["data"] for item in qr_history if item["region"] == "Miền Nam"}
unique_other = {item["data"] for item in qr_history if item["region"] == "Miền khác"}

unique_scans = len(unique_north | unique_central | unique_south | unique_other)

# Metrics Dashboard
st.markdown("## 📈 Tổng quan thống kê")

col1, col2, col3, col4, col5 = st.columns(5)
st.markdown('<div class="metric_card">', unsafe_allow_html=True)
st.markdown('<div class="metric-value">', unsafe_allow_html=True)
st.markdown('<div class="metric-label">', unsafe_allow_html=True)
with col1:
    st.markdown(f"""        
    <div class="metric-card">        
        <div class="metric-label">Tổng số quét</div>        
        <div class="metric-value">{total_scans}</div>    
    </div>        
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""        
    <div class="metric-card">              
        <div class="metric-label">Mã duy nhất</div>
        <div class="metric-value">{unique_scans}</div>          
    </div>        
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""        
    <div class="metric-card">            
        <div class="metric-label">Miền Bắc </div>      
        <div class="metric-value">{len(unique_north)}</div>      
    </div>        
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""        
    <div class="metric-card">           
        <div class="metric-label">Miền Trung</div>       
        <div class="metric-value">{len(unique_central)}</div>      
    </div>        
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""        
    <div class="metric-card">             
        <div class="metric-label">Miền Nam</div>   
        <div class="metric-value">{len(unique_south)}</div>        
    </div>        
    """, unsafe_allow_html=True)
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
# Layout 2 cột cho biểu đồ
if qr_history:
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

            # Bảng dữ liệu chi tiết (chỉ có filter theo miền)
    st.markdown("## 📋 Lịch sử quét chi tiết")

    df = pd.DataFrame(qr_history)

    # Chỉ có filter theo miền
    region_filter = st.selectbox(
        "Lọc theo miền:",
        ["Tất cả"] + list(df['region'].unique()) if not df.empty else ["Tất cả"]
    )
    st.markdown('<div class="date-filter">', unsafe_allow_html=True)
    # Apply filter
    filtered_df = df.copy()
    if region_filter != "Tất cả" and not df.empty:
        filtered_df = filtered_df[filtered_df['region'] == region_filter]

        # Display table
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    if not filtered_df.empty:
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            filtered_df[['data', 'region', 'time']],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Download button
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Tải xuống",
            data=csv,
            file_name=f"Dữ_liệu_đơn_hàng_{selected_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("🔍 Không có dữ liệu cho bộ lọc đã chọn.")

else:
    st.info("🔍 Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")

# Sidebar
with st.sidebar:
    st.markdown(f"""        
    <div class="sidebar-section">        
        <h3>👤 Người dùng</h3>        
        <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>        
    </div>        
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("""        
    <div class="sidebar-section">        
        <h3>📊 Thống kê nhanh</h3>        
    </div>        
    """, unsafe_allow_html=True)

    if qr_history:
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
        st.session_state.logged_in = False,
        st.session_state.username = ""
        st.switch_page("pages/login.py")