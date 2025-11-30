import time

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.qr_storage import load_qr_data, get_available_dates
from Component.Camera.CameraHeader import load_css

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

col_h1,col_h2 = st.columns([1,3])
with col_h1:
    if st.button("⬅️ Quay về", use_container_width=True, type="secondary"):
        st.switch_page("Home.py")
with col_h2:
    st.markdown("")
# Cấu hình trang
st.set_page_config(
    page_title="📊 Thống kê & Báo cáo",
    layout="wide",
    initial_sidebar_state="expanded"
)
def add_to_log_stack(param):
    pass
# Load CSS
load_css("Led_BlinkStyle.css")
st.markdown("""  
<style>  
.main-header {  
    font-family: 'Times New Roman', sans-serif;  /* Thêm dòng này */  
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  
    padding: 1.5rem;  
    border-radius: 10px;  
    color: white;  
    text-align: center;  
    margin-bottom: 2rem;  
}  
.led-container {  
    display: flex;  
    justify-content: center;  
    align-items: center;  
    margin: 20px 0;  
}  
.led-circle {  
    width: 80px;  
    height: 80px;  
    border-radius: 50%;  
    border: 3px solid #333;  
    margin: 0 20px;  
    display: flex;  
    align-items: center;  
    justify-content: center;  
    font-weight: bold;  
    color: white;  
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);  
}  
.led-off { background-color: #666; }  
.led-red { background-color: #ff4444; box-shadow: 0 0 20px #ff4444; }  
.led-yellow { background-color: #ffdd44; box-shadow: 0 0 20px #ffdd44; }  
.led-green { background-color: #44ff44; box-shadow: 0 0 20px #44ff44; }  
.region-info {  
    text-align: center;  
    margin-top: 10px;  
    font-size: 14px;  
    color: #666;  
}  
.active-timer {  
    background: #fff3e0;  
    padding: 8px;  
    margin: 3px 0;  
    border-radius: 3px;  
    border-left: 3px solid #ff9800;  
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

# CSS tùy chỉnh

# Header chính
st.markdown("""        
<div class="main-header">        
    <h1>📊 THỐNG KÊ & BÁO CÁO</h1>    
</div>        
""", unsafe_allow_html=True)

# Date Filter
st.markdown("""    
<div class="date-filter">    
    <h2>📅 Chọn ngày xem data</h2>    
</div>    
""", unsafe_allow_html=True)

available_dates = get_available_dates()

if available_dates:
    selected_date = st.selectbox(
    "Chọn ngày:",
    options=available_dates,
    format_func=lambda x: x.strftime("%Y-%m-%d (%A)"),
    index=0
)
    # Load data theo ngày được chọn

    qr_history = load_qr_data(selected_date)
    st.info(f"📊 Hiển thị data ngày {selected_date.strftime('%Y-%m-%d')}: {len(qr_history)}")
else:
    st.warning("Chưa có data nào")
    qr_history = []

# Tính toán thống kê
total_scans = len(qr_history)

# Tách dữ liệu theo miền
unique_south = {item["data"] for item in qr_history if item["region"] == "Miền Nam"}
unique_north = {item["data"] for item in qr_history if item["region"] == "Miền Bắc"}
unique_central = {item["data"] for item in qr_history if item["region"] == "Miền Trung"}
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

with col5:
    st.markdown(f"""        
    <div class="metric-card">              
        <div class="metric-label">Miền khác</div>
        <div class="metric-value">{len(unique_other)}</div>          
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

with col2:
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
                             color_discrete_sequence=['#7fffd4', '#deb887', '#5f9ea0', '#a52a2a'])
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
                             color_discrete_sequence=['#7fffd4', '#deb887', '#5f9ea0', '#a52a2a'])
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

    else:
        st.info("🔍 Không có dữ liệu cho bộ lọc đã chọn.")

else:
    st.info("🔍 Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")



col1_f,col2_f,col3_f = st.columns([1,1,3])
with col1_f:
    if st.button("🔄 Reset dữ liệu lưu trữ", use_container_width=True, type="secondary"):
        from utils.qr_storage import reset_daily_data

        # Ghi số 1 vào DB14.1 (offset 2, vì DB14.0 là offset 0-1)
        if 'plc_manager' in st.session_state and st.session_state.plc_connected:
            # Tạo bytearray chứa 202 bytes (101 positions × 2 bytes) = tất cả là 0
            zero_array = bytearray(202)

            # Ghi 1 lần cho mỗi DB thay vì 101 lần
            st.session_state.plc_manager.client.db_write(1, 0, zero_array)
            add_to_log_stack("Đã reset dữ liệu danh sách 1")

            st.session_state.plc_manager.client.db_write(2, 0, zero_array)
            add_to_log_stack("Đã reset dữ liệu danh sách 2")

            st.session_state.plc_manager.client.db_write(3, 0, zero_array)
            add_to_log_stack("Đã reset dữ liệu danh sách 3")

            # Ghi tín hiệu reset
            success = st.session_state.plc_manager.write_db(14, 2, 1)
            if success:
                add_to_log_stack("[PLC] Đã ghi DB14.1 = 1 (Reset signal)")
            else:
                st.error("❌ Lỗi reset bộ nhớ..., Xem lại kết nối dây")
                st.stop()

        if reset_daily_data():
            # Reset session state
            st.session_state.package_counter = 0
            st.session_state.package_queue.clear()
            st.session_state.last_qr_count = 0
            st.session_state.log_stack = []
            st.session_state.db_array_position = 1

            # Ghi số 0 vào DB14.1 sau khi reset xong
            if 'plc_manager' in st.session_state and st.session_state.plc_connected:
                success = st.session_state.plc_manager.write_db(14, 2, 0)
                if success:
                    add_to_log_stack("[PLC] Đã ghi DB14.1 = 0 (Reset complete)")
                else:
                    st.warning("⚠️ Không thể reset DB14.1 về 0")

            st.success("✅ Đã reset toàn bộ dữ liệu!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("❌ Lỗi khi reset dữ liệu")
with col2_f:
    csv = filtered_df.to_csv(index=False, encoding='utf-8-sig', sep=',')
    st.download_button(
        label="📥 Tải xuống",
        data=csv,
        file_name=f"Dữ_liệu_đơn_hàng_{selected_date.strftime('%Y%m%d')}_Manager:{st.session_state.get('username')}",
        mime="text/csv"
    )

with col3_f:
    st.markdown("")

# Sidebar
with st.sidebar:
    st.markdown(f"""        
    <div class="sidebar-section">        
        <h3>👤 Người dùng</h3>        
        <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>        
    </div>        
    """, unsafe_allow_html=True)
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
        st.switch_page("pages/Login.py")