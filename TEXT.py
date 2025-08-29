import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2

# Tiêu đề
st.title("ĐỒ ÁN TỐT NGHIỆP")
cap=cv2.VideoCapture(0)
frame_placehodler = st.empty()
#Tạo class xử lý video
#class VideoTransformer(VideoTransformerBase):
#   def transform(self, frame):
#        img = frame.to_ndarray(format="bgr24")

        # 👉 Ví dụ: chuyển sang grayscale
#        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Trả về ảnh màu để hiển thị

# Kích hoạt camera từ trình duyệt
#webrtc_streamer(key="camera", video_transformer_factory=VideoTransformer)
while True:
    ret, frame = cap.read()
    if ret:
        st.write("khong mo camera")
        break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder = frame_placeholder.image(frame, channels="RGB")
        cap.release()