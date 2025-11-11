import os
import requests
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
from Config.config import Config
from utils.process_uploaded_image import process_uploaded_image
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
render_main_header("🔬 HỆ THỐNG QUÉT MÃ QR", "Nhận diện và phân loại tự động")

# Check authentication
if not check_login():
    st.stop()


# Function để render remote camera với auto-start stream
def render_remote_camera():
    """Render camera stream từ Flask service local với auto QR detection"""
    st.markdown("### 📹 Remote Camera Scanner")

    col_cam, col_control = st.columns([3, 1])

    # Initialize session state
    if 'camera_started' not in st.session_state:
        st.session_state.camera_started = False
    if 'auto_qr_detection' not in st.session_state:
        st.session_state.auto_qr_detection = False

    with col_control:
        if st.button("🎬 Start Camera"):
            try:
                response = requests.get(Config.get_camera_start_url(), timeout=10)
                if response.status_code == 200:
                    st.success("Camera started!")
                    st.session_state.camera_started = True
                    st.rerun()
                else:
                    st.error("Failed to start camera")
            except Exception as e:
                st.error(f"Connection error: {e}")

        if st.button("⏹️ Stop Camera"):
            try:
                requests.get(Config.get_camera_stop_url(), timeout=5)
                st.success("Camera stopped!")
                st.session_state.camera_started = False
                st.session_state.auto_qr_detection = False
                st.rerun()
            except Exception as e:
                st.error(f"Connection error: {e}")

                # Toggle auto QR detection
        if st.session_state.camera_started:
            st.session_state.auto_qr_detection = st.checkbox(
                "🔄 Auto QR Detection (200ms)",
                value=st.session_state.auto_qr_detection
            )

    with col_cam:
        # Hiển thị video stream
        if st.session_state.camera_started:
            stream_url = Config.get_camera_stream_url()
            st.markdown(f"""  
            <div style="text-align: center; border: 2px solid #0066cc; border-radius: 10px; padding: 10px;">  
                <img src="{stream_url}"   
                     style="max-width: 100%; height: auto; border-radius: 5px;"   
                     alt="Camera Stream" />  
                <p style="margin-top: 10px; color: #666;">Live Camera Feed</p>  
            </div>  
            """, unsafe_allow_html=True)

            # Auto QR detection placeholder
            qr_status_placeholder = st.empty()

            # Auto-polling logic
            if st.session_state.auto_qr_detection:
                try:
                    response = requests.get(Config.get_camera_frame_url(), timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('qr_data'):
                            qr_data = data['qr_data']
                            qr_status_placeholder.success(f"✅ QR Detected: {qr_data}")

                            # Process QR detection using existing logic
                            if process_qr_detection(qr_data):
                                st.session_state.data_updated = True
                        else:
                            qr_status_placeholder.info("🔍 Scanning for QR codes...")
                    else:
                        qr_status_placeholder.error("Failed to get frame data")
                except Exception as e:
                    qr_status_placeholder.error(f"Connection error: {e}")

                    # Auto-refresh every 1s
                time.sleep(1)
                st.rerun()
        else:
            # Placeholder khi camera chưa start
            st.markdown("""  
            <div style="text-align: center; border: 2px dashed #ccc; border-radius: 10px; padding: 50px;">  
                <p style="color: #666; font-size: 18px;">📹</p>  
                <p style="color: #666;">Click "Start Camera" to begin streaming</p>  
            </div>  
            """, unsafe_allow_html=True)

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
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)# chỉnh fontScant thì chữ nhỏ hơn và thinkness thi chu manh hơn

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
    st.markdown("<h2 style='text-align: center;'> 📹 Camera Scanner</2>", unsafe_allow_html=True)

    # Logic với 3 options
    camera_mode = st.radio(
        "Select Camera Mode:",
        ["WebRTC (Local)", "File Upload"],
        index=0 if not (os.getenv('RENDER') or os.getenv('STREAMLIT_SHARING')) else 2
    )

    if camera_mode == "WebRTC (Local)":
        # WebRTC cho local development
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


    else:
        # File upload fallback
        process_uploaded_image()

with col2:
    render_system_metrics(total_scans, last_qr)

# Render data table
render_qr_history_table(qr_data)

# Render sidebar
render_sidebar(st.session_state.username)
