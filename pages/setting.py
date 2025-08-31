import streamlit as st

# --- Cấu hình trang ---
st.set_page_config(
    page_title="⚙️ Cài đặt hệ thống",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS tùy chỉnh ---
st.markdown("""  
<style>  
    .main-header {  
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);  
        padding: 1.5rem;  
        border-radius: 10px;  
        color: white;  
        text-align: center;  
        margin-bottom: 2rem;  
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  
    }  

    .setting-card {  
        background: #f8f9fa;  
        border: 1px solid #dee2e6;  
        border-radius: 10px;  
        padding: 1.5rem;  
        margin: 1rem 0;  
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);  
    }  

    .setting-title {  
        color: #2c3e50;  
        font-weight: bold;  
        margin-bottom: 1rem;  
        border-bottom: 2px solid #3498db;  
        padding-bottom: 0.5rem;  
    }  

    .status-display {  
        background: #e8f5e8;  
        border: 1px solid #28a745;  
        border-radius: 8px;  
        padding: 1rem;  
        margin: 1rem 0;  
    }  

    .sidebar-section {  
        background: #f1f3f4;  
        padding: 1rem;  
        border-radius: 8px;  
        margin: 1rem 0;  
    }  
</style>  
""", unsafe_allow_html=True)

# --- Header chính ---
st.markdown("""  
<div class="main-header">  
    <h1>⚙️ CÀI ĐẶT HỆ THỐNG</h1>  
    <p>Điều chỉnh thông số và cấu hình ứng dụng</p>  
</div>  
""", unsafe_allow_html=True)

# --- Kiểm tra đăng nhập ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# --- Khởi tạo session state ---
if "grayscale" not in st.session_state:
    st.session_state.grayscale = False
if "resolution" not in st.session_state:
    st.session_state.resolution = (640, 480)
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 1.0
if 'speed_motor' not in st.session_state:
    st.session_state.speed_motor = 10.0

# --- Layout 2 cột ---
col1, col2 = st.columns([1, 1])

with col1:
    # --- Cài đặt Camera ---
    st.markdown("""  
    <div class="setting-card">  
        <h3 class="setting-title">📹 Cài đặt Camera</h3>  
    </div>  
    """, unsafe_allow_html=True)

    # Grayscale
    st.session_state.grayscale = st.checkbox(
        "🎨 Bật chế độ Grayscale",
        value=st.session_state.grayscale,
        help="Chuyển đổi hình ảnh sang màu xám"
    )

    # Zoom level
    st.markdown("**🔍 Điều chỉnh độ phóng đại**")
    st.session_state.zoom_level = st.slider(
        "Mức phóng đại camera:",
        min_value=1.0,
        max_value=3.0,
        value=st.session_state.zoom_level,
        step=0.1,
        help="1.0 = Zoom mặc định, giá trị lớn hơn sẽ phóng to hình ảnh"
    )

    # Resolution
    st.markdown("**📐 Độ phân giải**")
    resolution_options = {
        "640x480 (SD)": (640, 480),
        "1280x720 (HD)": (1280, 720),
        "1920x1080 (Full HD)": (1920, 1080)
    }

    current_res = f"{st.session_state.resolution[0]}x{st.session_state.resolution[1]}"
    for key, value in resolution_options.items():
        if value == st.session_state.resolution:
            current_res = key
            break

    selected_res = st.selectbox(
        "Chọn độ phân giải:",
        list(resolution_options.keys()),
        index=list(resolution_options.keys()).index(current_res) if current_res in resolution_options.keys() else 0
    )
    st.session_state.resolution = resolution_options[selected_res]

with col2:
    # --- Cài đặt Động cơ ---
    st.markdown("""  
    <div class="setting-card">  
        <h3 class="setting-title">⚡ Cài đặt Động cơ</h3>  
    </div>  
    """, unsafe_allow_html=True)

    st.markdown("**🚀 Tốc độ động cơ**")
    st.session_state.speed_motor = st.slider(
        "Tốc độ (m/phút):",
        min_value=10.0,
        max_value=20.0,
        value=st.session_state.speed_motor,
        step=1.0,
        help="Điều chỉnh tốc độ hoạt động của động cơ"
    )

    # Hiển thị trạng thái
    st.markdown("**📊 Trạng thái hiện tại**")

    # Metrics
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric("Zoom Level", f"{st.session_state.zoom_level}x")
        st.metric("Tốc độ", f"{st.session_state.speed_motor} m/ph")

    with col_metric2:
        st.metric("Độ phân giải", f"{st.session_state.resolution[0]}x{st.session_state.resolution[1]}")
        st.metric("Grayscale", "Bật" if st.session_state.grayscale else "Tắt")

    # --- Hiển thị cấu hình đã lưu ---
st.markdown("### 💾 Cấu hình đã lưu")

config_data = {
    "Thông số": ["Grayscale", "Zoom Level", "Độ phân giải", "Tốc độ động cơ"],
    "Giá trị": [
        "Bật" if st.session_state.grayscale else "Tắt",
        f"{st.session_state.zoom_level}x",
        f"{st.session_state.resolution[0]}x{st.session_state.resolution[1]}",
        f"{st.session_state.speed_motor} m/phút"
    ]
}

import pandas as pd

config_df = pd.DataFrame(config_data)
st.dataframe(config_df, use_container_width=True, hide_index=True)

st.success("✅ Tất cả cài đặt đã được lưu tự động!")

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
        <h3>🔧 Thao tác</h3>  
    </div>  
    """, unsafe_allow_html=True)

    if st.button("🔄 Reset về mặc định", use_container_width=True):
        st.session_state.grayscale = False
        st.session_state.zoom_level = 1.0
        st.session_state.resolution = (640, 480)
        st.session_state.speed_motor = 10.0
        st.success("Đã reset về cài đặt mặc định!")
        st.rerun()

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()