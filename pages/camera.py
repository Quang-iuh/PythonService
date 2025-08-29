import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

st.title("📷 Trang Camera")
st.write("Demo hiển thị nội dung cho trang Camera.")

# Bạn có thể thêm code WebRTC vào đây sau
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # 👉 Ví dụ: chuyển sang grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Trả về ảnh màu để hiển thị


# Kích hoạt camera từ trình duyệt
webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)