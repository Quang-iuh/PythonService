import streamlit as st

# --- Cấu hình trang ---
st.set_page_config(
    page_title="🏠 Hệ thống QR Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS tùy chỉnh ---
st.markdown("""  
<style>  
    .main-header {  
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  
        padding: 2rem;  
        border-radius: 15px;  
        color: white;  
        text-align: center;  
        margin-bottom: 2rem;  
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);  
    }  

    .feature-card {  
        background: #ffffff;  
        border: 1px solid #e1e5e9;  
        border-radius: 12px;  
        padding: 2rem;  
        margin: 1rem 0;  
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);  
        transition: transform 0.2s ease, box-shadow 0.2s ease;  
    }  

    .feature-card:hover {  
        transform: translateY(-2px);  
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);  
    }  

    .feature-icon {  
        font-size: 3rem;  
        margin-bottom: 1rem;  
        display: block;  
        text-align: center;  
    }  

    .feature-title {  
        color: #2c3e50;  
        font-weight: bold;  
        font-size: 1.5rem;  
        margin-bottom: 1rem;  
        text-align: center;  
    }  

    .feature-description {  
        color: #6c757d;  
        text-align: center;  
        line-height: 1.6;  
    }  

    .stats-container {  
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  
        padding: 1.5rem;  
        border-radius: 10px;  
        color: white;  
        text-align: center;  
        margin: 1rem 0;  
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
    <h1>🏠 HỆ THỐNG QR SCANNER</h1>  
    <p>Giải pháp quét và phân loại mã QR tự động</p>  
    <p><em>Chào mừng bạn đến với hệ thống quản lý QR hiện đại</em></p>  
</div>  
""", unsafe_allow_html=True)

# --- Kiểm tra đăng nhập ---
# if 'logged_in' not in st.session_state or not st.session_state.logged_in:
#     st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
#     st.stop()
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/login.py")
# --- Thống kê nhanh ---
if 'qr_history' in st.session_state:
    total_scans = len(st.session_state.qr_history)
    st.markdown(f"""  
    <div class="stats-container">  
        <h2>{total_scans}</h2>  
        <p>Tổng số mã QR đã quét</p>  
    </div>  
    """, unsafe_allow_html=True)

# --- Layout chính với 3 cột ---
st.markdown("## 🚀 Chức năng chính")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">📸</div>  
        <div class="feature-title">Camera Scanner</div>  
        <div class="feature-description">  
            Quét mã QR trực tiếp từ camera với công nghệ WebRTC.  
            Hỗ trợ phân loại tự động theo miền địa lý.  
        </div>  
    </div>  
    """, unsafe_allow_html=True)

    if st.button("🎯 Mở Camera", use_container_width=True, type="primary"):
        st.switch_page("pages/camera.py")

with col2:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">📊</div>  
        <div class="feature-title">Thống kê & Báo cáo</div>  
        <div class="feature-description">  
            Xem báo cáo chi tiết, biểu đồ phân tích và   
            thống kê dữ liệu quét theo thời gian.  
        </div>  
    </div>  
    """, unsafe_allow_html=True)

    if st.button("📈 Xem Thống kê", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

with col3:
    st.markdown("""  
    <div class="feature-card">  
        <div class="feature-icon">⚙️</div>  
        <div class="feature-title">Cài đặt Hệ thống</div>  
        <div class="feature-description">  
            Điều chỉnh thông số camera, độ phân giải,  
            tốc độ động cơ và các cấu hình khác.  
        </div>  
    </div>  
    """, unsafe_allow_html=True)

    if st.button("🔧 Cài đặt", use_container_width=True):
        st.switch_page("pages/setting.py")

    # --- Hướng dẫn sử dụng ---
st.markdown("## 📋 Hướng dẫn sử dụng")

with st.expander("🔍 Cách sử dụng Camera Scanner"):
    st.markdown("""  
    1. **Mở Camera**: Click vào nút "Mở Camera" hoặc sử dụng menu bên trái  
    2. **Cấp quyền**: Cho phép trình duyệt truy cập camera khi được yêu cầu  
    3. **Quét mã**: Đưa mã QR vào khung hình để hệ thống tự động nhận diện  
    4. **Xem kết quả**: Dữ liệu sẽ được phân loại và lưu tự động  
    """)

with st.expander("📊 Cách xem Thống kê"):
    st.markdown("""  
    1. **Truy cập**: Click "Xem Thống kê" để mở trang báo cáo  
    2. **Phân tích**: Xem biểu đồ phân loại theo miền địa lý  
    3. **Lịch sử**: Kiểm tra danh sách tất cả mã QR đã quét  
    4. **Xuất dữ liệu**: Tải về báo cáo dưới dạng file CSV  
    """)

# --- Thông tin hệ thống ---
st.markdown("## ℹ️ Thông tin hệ thống")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.info("""  
    **🔧 Tính năng chính:**  
    - Quét QR code real-time  
    - Phân loại tự động theo miền  
    - Lưu trữ lịch sử quét  
    - Báo cáo thống kê chi tiết  
    """)

with info_col2:
    st.success("""  
    **✅ Trạng thái hệ thống:**  
    - Camera: Sẵn sàng  
    - Database: Hoạt động  
    - WebRTC: Kết nối ổn định  
    - Phân loại: Tự động  
    """)

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""  
    <div class="sidebar-section">  
        <h3>👤 Thông tin người dùng</h3>  
        <p>Xin chào, <strong>{st.session_state.username}</strong></p>  
        <p>Phiên làm việc đang hoạt động</p>  
    </div>  
    """, unsafe_allow_html=True)

    st.markdown("""  
    <div class="sidebar-section">  
        <h3>🔗 Liên kết nhanh</h3>  
    </div>  
    """, unsafe_allow_html=True)

    # Navigation buttons
    if st.button("📸 Camera", use_container_width=True):
        st.switch_page("pages/camera.py")

    if st.button("📊 Thống kê", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

    if st.button("⚙️ Cài đặt", use_container_width=True):
        st.switch_page("pages/setting.py")

    st.markdown("---")

    if st.button("🔒 Đăng xuất", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        # st.rerun()