import streamlit as st

# Cấu hình trang
st.set_page_config(
    page_title="🏠 QR Scanner System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tối ưu
st.markdown("""  
<style>  
    .main-header {  
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  
        padding: 2.5rem;  
        border-radius: 20px;  
        color: white;  
        text-align: center;  
        margin-bottom: 2rem;  
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);  
    }  

    .feature-card {  
        background: white;  
        border-radius: 15px;  
        padding: 2rem;  
        margin: 1rem 0;  
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);  
        transition: all 0.3s ease;  
        border: 1px solid #f0f0f0;  
    }  

    .feature-card:hover {  
        transform: translateY(-5px);  
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);  
    }  

    .feature-icon {  
        font-size: 3.5rem;  
        margin-bottom: 1rem;  
        text-align: center;  
    }  

    .stats-grid {  
        display: grid;  
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));  
        gap: 1rem;  
        margin: 2rem 0;  
    }  

    .stat-card {  
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);  
        padding: 1.5rem;  
        border-radius: 15px;  
        color: white;  
        text-align: center;  
    }  

    .quick-nav {  
        background: #f8f9fa;  
        padding: 1.5rem;  
        border-radius: 15px;  
        margin: 1rem 0;  
    }  
</style>  
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/login.py")

# Header chính
st.markdown("""  
<div class="main-header">  
    <h1>🏠 HỆ THỐNG XỬ LÝ ẢNH</h1>   
</div>  
""".format(st.session_state.get('username', 'User')), unsafe_allow_html=True)

# Thống kê nhanh
if 'qr_history' in st.session_state:
    total_scans = len(st.session_state.qr_history)
    st.markdown(f"""  
    <div class="stats-grid">  
        <div class="stat-card">  
            <h2>{total_scans}</h2>  
            <p>QR Đã Quét</p>  
        </div>  
    </div>  
    """, unsafe_allow_html=True)

# Chức năng chính - Layout 4 cột
col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">📸</div>  
        <h4>Camera Scanner</h4>  
        <p>Quét QR </p>  
    </div>  
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""    
    <div class="feature-card">    
        <div class="feature-icon">🔌</div>    
        <h4>PLC Controller</h4>    
        <p>Truyền dữ liệu cho PLC</p>    
    </div>    
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">📊</div>  
        <h4>THỐNG KÊ</h4>  
        <p>Thống kê và báo cáo chi tiết</p>  
    </div>  
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">⚙️</div>  
        <h4>SETTING</h4>  
        <p>Cài đặt thông số hệ thống</p>  
    </div>  
    """, unsafe_allow_html=True)

bu_col1, bu_col2, bu_col3, bu_col4 = st.columns(4)
with bu_col1:
     if st.button("🎯 Mở Camera", use_container_width=True, type="primary"):
         st.switch_page("pages/camera.py")
with bu_col2:
    if st.button("📈 Xem thống kê", use_container_width=True, type="primary"):
        st.switch_page("pages/Dashboard.py")
with bu_col3:
    if st.button("🔌 PLC", use_container_width=True, type="primary"):
        st.switch_page("pages/PLC.py")
with bu_col4:
    if st.button("⚙️ Setting", use_container_width=True, type="primary"):
        st.switch_page("pages/Setting.py")
    # Quick Navigation
nav_col1, nav_col2= st.columns(2)

with nav_col1:
    if st.button("📋 Hướng dẫn", use_container_width=True):
        with st.expander("📖 Hướng dẫn sử dụng", expanded=True):
            st.markdown("""  
            **🔍 Camera Scanner:**  
            1. Click "Mở Camera" → Cấp quyền camera  
            2. Đưa QR vào khung hình → Tự động phân loại  

            **🚦 PLC Control:**  
            1. Monitor LED 3 khu vực phân loại  
            2. Xem timing và delay của từng miền  
            """)

with nav_col2:
    if st.button("🔒 Đăng xuất", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()