import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

# Tiêu đề
st.title("📷 Camera Streaming qua Web (WebRTC + OpenCV)")


# Tạo class xử lý video
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # 👉 Ví dụ: chuyển sang grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (1280, 720))  # tùy chỉnh kích thước
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Trả về ảnh màu để hiển thị
st.markdown(
    """
    <style>
    video {
        width: 100% !important;
        max-width: 900px;   /* đặt khung rộng */
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Kích hoạt camera từ trình duyệt
webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)
