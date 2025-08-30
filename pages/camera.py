import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import pandas as pd
import av
import time
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Quét Mã QR", layout="wide")
st.title("📷 Trang Quét Mã QR")
time.sleep(0.5)

# --- Khởi tạo session state nếu chưa có ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'qr_history' not in st.session_state:
    st.session_state.qr_history = []

if 'last_qr' not in st.session_state:
    st.session_state.last_qr = ""  # Khởi tạo giá trị mặc định cho last_qr

if 'last_active' not in st.session_state:
    st.session_state.last_active = time.time()  # Khởi tạo thời gian hoạt động


# --- Check login ---
if not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# --- Hàm phân loại QR ---
def classify_qr(qr_data: str) -> str:
    qr_lower = qr_data.lower()
    if qr_data.startswith("MB-") or "mien bac" in qr_lower:
        return "Miền Bắc"
    if qr_data.startswith("MT-") or "mien trung" in qr_lower:
        return "Miền Trung"
    if qr_data.startswith("MN-") or "mien nam" in qr_lower:
        return "Miền Nam"
    return "Miền khác"

# --- Video Processor ---
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.last_qr = ""
        self.qr_history = []
        logger.info("QRCodeDetector initialized.")

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        data, points, _ = self.detector.detectAndDecode(img)

        if points is not None and data:
            # Vẽ khung QR
            points = points.astype(int).reshape(-1, 2)
            for j in range(len(points)):
                pt1 = tuple(points[j])
                pt2 = tuple(points[(j + 1) % len(points)])
                cv2.line(img, pt1, pt2, (0, 255, 0), 2)

                # Lưu vào instance thay vì session_state
            if data != self.last_qr:
                qr_region = classify_qr(data)
                qr_entry = {
                    "data": data,
                    "type": "QRCODE",
                    "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "region": qr_region,
                }
                self.qr_history.append(qr_entry)
                self.last_qr = data
                logger.info(f"New QR Code detected: {data} in region: {qr_region}")

            cv2.putText(img, data, (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")
# --- Run WebRTC ---
ctx = webrtc_streamer(
    key="qr-camera",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},  # Bỏ deviceId cụ thể
    rtc_configuration={
        "iceServers": [
            {"urls": "stun:stun.l.google.com:19302"}
        ]
    },
)
# Thêm vào đầu file sau phần khởi tạo session state
if 'qr_display_placeholder' not in st.session_state:
    st.session_state.qr_display_placeholder = None

# Tạo placeholder cho hiển thị real-time
qr_display_container = st.empty()
history_container = st.empty()

# Sau phần WebRTC, thay thế logic hiển thị bằng:
if ctx.video_processor:
    # Đồng bộ dữ liệu
    if hasattr(ctx.video_processor, 'qr_history'):
        for entry in ctx.video_processor.qr_history:
            if entry not in st.session_state.qr_history:
                st.session_state.qr_history.append(entry)

    if hasattr(ctx.video_processor, 'last_qr'):
        st.session_state.last_qr = ctx.video_processor.last_qr

    # Cập nhật hiển thị liên tục
with qr_display_container.container():
    if st.session_state.last_qr:
        st.info(f"✅ Đã quét thành công mã QR: **{st.session_state.last_qr}**")

with history_container.container():
    if st.session_state.qr_history:
        df = pd.DataFrame(st.session_state.qr_history)
        st.subheader("📜 Lịch sử quét")
        st.dataframe(df[['data', 'region', 'time']], use_container_width=True)

# Kiểm tra trạng thái của WebRTC
if ctx:
    logger.info(f"WebRTC session started")
else:
    logger.error("Failed to initialize WebRTC session.")
# Sau phần khởi tạo WebRTC
if ctx.video_processor:
    if hasattr(ctx.video_processor, 'qr_history'):
        processor_count = len(ctx.video_processor.qr_history)
        session_count = len(st.session_state.qr_history)

        if processor_count > session_count:
            # Đồng bộ dữ liệu mới
            for entry in ctx.video_processor.qr_history:
                if entry not in st.session_state.qr_history:
                    st.session_state.qr_history.append(entry)

            if hasattr(ctx.video_processor, 'last_qr'):
                st.session_state.last_qr = ctx.video_processor.last_qr

                # Force rerun ngay lập tức
            st.rerun()
# THÊM ĐOẠN CODE ĐỒNG BỘ TẠI ĐÂY:
if ctx.video_processor:
    # Đồng bộ dữ liệu từ processor về session_state
    if hasattr(ctx.video_processor, 'qr_history'):
        # Cập nhật session_state với dữ liệu mới từ processor
        for entry in ctx.video_processor.qr_history:
            if entry not in st.session_state.qr_history:
                st.session_state.qr_history.append(entry)

                # Cập nhật last_qr
    if hasattr(ctx.video_processor, 'last_qr'):
        st.session_state.last_qr = ctx.video_processor.last_qr

    # Thêm auto-refresh mỗi 0.5 giây chỉ khi có WebRTC đang chạy
    if ctx and ctx.state.playing:
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()

        if time.time() - st.session_state.last_refresh > 0.5:
            st.session_state.last_refresh = time.time()
            st.rerun()
    # Kiểm tra trạng thái của WebRTC
    if ctx:
        logger.info(f"WebRTC session started")
    else:
        logger.error("Failed to initialize WebRTC session.")

        # Đồng bộ dữ liệu và kiểm tra cập nhật
    if ctx.video_processor:
        if hasattr(ctx.video_processor, 'qr_history'):
            processor_count = len(ctx.video_processor.qr_history)
            session_count = len(st.session_state.qr_history)

            # Chỉ đồng bộ và rerun khi có dữ liệu mới
            if processor_count > session_count:
                for entry in ctx.video_processor.qr_history:
                    if entry not in st.session_state.qr_history:
                        st.session_state.qr_history.append(entry)

                if hasattr(ctx.video_processor, 'last_qr'):
                    st.session_state.last_qr = ctx.video_processor.last_qr

                    # Force rerun để hiển thị ngay lập tức
                st.rerun()

                # --- Auto stop nếu idle quá lâu ---
    if ctx and ctx.state.playing:
        idle_time = time.time() - st.session_state.last_active
        if idle_time > 600:
            st.warning("⚠️ Camera session đã hết hạn, vui lòng reload trang để kết nối lại.")
            logger.info("Camera session expired, stopping.")
            ctx.stop()

            # --- Hiển thị kết quả (chỉ giữ lại 1 đoạn) ---
    if st.session_state.last_qr:
        st.info(f"✅ Đã quét thành công mã QR: **{st.session_state.last_qr}**")

    if st.session_state.qr_history:
        df = pd.DataFrame(st.session_state.qr_history)
        st.subheader("📜 Lịch sử quét")
        st.dataframe(df[['data', 'region', 'time']], use_container_width=True)


# Lịch sử quét
st.subheader("Lịch sử quét mã")
if st.session_state.qr_history:
    df = pd.DataFrame(st.session_state.qr_history)
    st.dataframe(df[['data','region','time']], use_container_width=True)
else:
    st.info("Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")
  # --- Sidebar ---
    st.sidebar.title(f"Chào {st.session_state.username}")
    if st.sidebar.button("🔒 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
        logger.info("User logged out.")
