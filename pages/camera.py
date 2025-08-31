import streamlit as st
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
render_main_header("🔬 HỆ THỐNG QUÉT MÃ QR", "Công nghệ nhận diện và phân loại tự động")

# Check authentication
if not check_login():
    st.stop()


# Video Processor (simplified)
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        data, points, _ = self.detector.detectAndDecode(img)

        if points is not None and data:
            # Vẽ khung
            points = points.astype(int).reshape(-1, 2)
            for j in range(len(points)):
                pt1 = tuple(points[j])
                pt2 = tuple(points[(j + 1) % len(points)])
                cv2.line(img, pt1, pt2, (0, 255, 0), 3)

                # Process QR
            if process_qr_detection(data):
                st.session_state.data_updated = True

                # Hiển thị text
            cv2.rectangle(img, (points[0][0], points[0][1] - 35),
                          (points[0][0] + len(data) * 12, points[0][1] - 5),
                          (0, 255, 0), -1)
            cv2.putText(img, data, (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        st.session_state.last_active = time.time()
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    # Auto-refresh logic


if st.session_state.get('data_updated', False):
    st.session_state.data_updated = False
    st.rerun()

# Load data
qr_data = load_qr_data()
total_scans = len(qr_data)
last_qr = get_last_qr()

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📹 Camera Scanner")
    ctx = webrtc_streamer(
        key="qr-camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": "stun:stun.l.google.com:19302"}]},
    )

with col2:
    render_system_metrics(total_scans, last_qr)

# Render data table
render_qr_history_table(qr_data)

# Render sidebar
render_sidebar(st.session_state.username)