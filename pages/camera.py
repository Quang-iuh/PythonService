import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
from pyzbar.pyzbar import decode

st.title("📷 Camera")

# Đọc config từ session_state
grayscale = st.session_state.get("grayscale", False)
resolution = st.session_state.get('resolution',(640,480))
zoom_level = st.session_state.get('zoom_level',1.0)

# Khung hiển thị QR
qr_placeholder = st.empty()

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.last_qr = ""

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Áp dụng grayscale nếu bật
        if grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Resize theo setting
        img = cv2.resize(img, resolution)

        # Quét mã QR
        decoded_objs = decode(img)
        for obj in decoded_objs:
            # Vẽ khung quanh QR
            (x, y, w, h) = obj.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            qr_data = obj.data.decode("utf-8")
            cv2.putText(img, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 255, 0), 2)

            # Nếu QR mới → cập nhật text
            if qr_data != self.last_qr:
                self.last_qr = qr_data
                qr_placeholder.success(f"📌 QR Detected: {qr_data}")

        return img


webrtc_streamer(
    key="camera",
    video_transformer_factory=VideoTransformer,
    media_stream_constraints={"video": True, "audio": False}
)
