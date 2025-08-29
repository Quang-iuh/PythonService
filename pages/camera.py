import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2

# Khởi tạo QRCodeDetector
qr_detector = cv2.QRCodeDetector()

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Phát hiện QR
        data, points, _ = qr_detector.detectAndDecode(img)

        if points is not None:
            points = points.astype(int).reshape(-1, 2)
            # Vẽ khung QR
            for i in range(len(points)):
                pt1 = tuple(points[i])
                pt2 = tuple(points[(i + 1) % len(points)])
                cv2.line(img, pt1, pt2, (0, 255, 0), 2)

            # Hiển thị dữ liệu QR
            if data:
                cv2.putText(img, f"QR: {data}", (points[0][0], points[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                st.session_state["last_qr"] = data

        return img


st.title("📷 QR Code Scanner (OpenCV)")

webrtc_streamer(
    key="camera",
    video_transformer_factory=VideoTransformer,
    media_stream_constraints={"video": True, "audio": False}
)

# Hiển thị QR code đã đọc
st.subheader("📌 QR Code nhận được:")
if "last_qr" in st.session_state:
    st.success(st.session_state["last_qr"])
else:
    st.info("Chưa phát hiện mã QR")
