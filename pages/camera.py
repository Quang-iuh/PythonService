from operator import truediv

import streamlit as st
from streamlit import switch_page
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import av
import time

# Import components
from Component.Camera.CameraHeader import load_css, render_main_header
from Component.Camera.CameraMetrics import render_system_metrics
from Component.Camera.CameraSidebar import render_sidebar
from Component.Camera.CameraData_table import render_qr_history_table
from utils.qr_processor import process_qr_detection
from utils.qr_storage import load_qr_data, get_last_qr
from utils.auth import check_login

# Cấu hình trang
st.set_page_config(
    page_title="🔬 QR Scanner System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS và render header
load_css("CameraStyle.css")
render_main_header("🔬 HỆ THỐNG QUÉT MÃ QR", "")

# Check authentication
if not check_login():
    st.stop()

def add_to_log_stack(param):
    pass
class VideoProcessor(VideoProcessorBase):
    def __init__(self):#Khởi tạo class
        self.detector = cv2.QRCodeDetector()

    def recv(self, frame):# xu lý mỗi Frame, WebRTC sẽ gữi mỗi fram từ video sang numpy array BGR24
        img = frame.to_ndarray(format="bgr24")
        data, points, _ = self.detector.detectAndDecode(img)

        # nếu phát hện QR sẽ vẽ 1 khung quanh qr để sẽ dàng xác định
        if points is not None and data:
            points = points.astype(int).reshape(-1, 2)
            for j in range(len(points)):
                pt1 = tuple(points[j])
                pt2 = tuple(points[(j + 1) % len(points)])
                cv2.line(img, pt1, pt2, (0, 255, 0), 3)

            #Xử lý QR cũ và mới và lưu dữ liệu vào file jason
            if process_qr_detection(data):
                st.session_state.data_updated = True

            # Hiển thị text và vẽ hình chữ nhat quanh qr
            (cv2.rectangle
             (img, (points[0][0], points[0][1] - 35),
              (points[0][0] + len(data) * 12, points[0][1] - 5),
              (0, 255, 0), -1))
            (cv2.putText
             (img, data, (points[0][0], points[0][1] - 10),
              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1))

        st.session_state.last_active = time.time()#Dòng này ghi lại thời gian frame video cuối cùng được xử lý.
        return av.VideoFrame.from_ndarray(img, format="bgr24")#Dòng này dùng để hiển thị lại video lên Streamlit sau khi bạn xử lý ảnh (như quét QR).

    # Load data
qr_data = load_qr_data()
total_scans = len(qr_data)
last_qr = get_last_qr()

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<h2 style='text-align: center;'> 📹 Camera Scanner</h2>", unsafe_allow_html=True)

    ctx = webrtc_streamer(
        key="qr-camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 1280},
                "height": {"ideal": 720},
                "frameRate": {"ideal": st.session_state.get('camera_fps', 30)}
            },
            "audio": False
        },
        rtc_configuration={
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"},
                {"urls": "turn:openrelay.metered.ca:80", "username": "openrelayproject",
                 "credential": "openrelayproject"}
            ]
        },
        async_processing=False
    )
    render_qr_history_table(qr_data)


with col2:
    render_system_metrics(total_scans, last_qr)
    if st.button("Setting", use_container_width=True, type=("primary"), width=("stretch")):
        switch_page("pages/Setting.py")
    if st.button("Thống kê", use_container_width=True, type=("primary"), width=("stretch")):
        switch_page("pages/Dashboard.py")
    if st.button("🔄 Reset dữ liệu lưu trữ", use_container_width=True, type="secondary"):
        from utils.qr_storage import reset_daily_data

        if reset_daily_data():
                # Reset session state
            st.session_state.package_counter = 0
            st.session_state.package_queue.clear()
            st.session_state.last_qr_count = 0
            st.session_state.log_stack = []
            st.session_state.db_array_position = 1

        # Verify PLC connection
        if 'plc_manager' in st.session_state and st.session_state.plc_connected:
            add_to_log_stack("[RESET] Đã reset dữ liệu - PLC vẫn kết nối")
        else:
            add_to_log_stack("[RESET] Đã reset dữ liệu - Cảnh báo: PLC chưa kết nối")

        st.success("✅ Đã reset toàn bộ dữ liệu!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("❌ Lỗi khi reset dữ liệu")

# Render sidebar
with st.sidebar:
    st.markdown(f"""  
    <div class="sidebar-section">  
        <h3>👤 Người dùng</h3>  
        <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>  
    </div>  
    """, unsafe_allow_html=True)
    im_co1, im_co2 = st.columns(2)
    with im_co1:
        st.image("image/images2.jfif", width=80)
    with im_co2:
        st.image("image/images.png", width=80)

    if st.button("🔒 Đăng xuất", use_container_width=True, type=("tertiary")):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/Login.py")

# Auto-refresh để cập nhật UI khi có QR mới
if ctx.state.playing:
    time.sleep(2)  # Refresh mỗi 2 giây
    st.rerun()