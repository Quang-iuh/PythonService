import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
from pyzbar.pyzbar import decode
import pandas as pd
from queue import Queue

# --- Biến toàn cục cho hàng đợi QR ---
qr_queue = Queue()

# --- Cấu hình trang ---
st.set_page_config(page_title="Quét Mã QR", layout="wide")

st.title("📷 Trang Quét Mã QR")
st.write("Sử dụng camera của bạn để quét và phân loại mã QR.")

# --- Khởi tạo session state ---
if 'qr_history' not in st.session_state:
    st.session_state.qr_history = []
if 'last_qr' not in st.session_state:
    st.session_state.last_qr = ""


# --- Hàm phân loại mã QR ---
def classify_qr(qr_data):
    if qr_data.startswith("MB-"):
        return "Miền Bắc"
    if qr_data.startswith("MT-"):
        return "Miền Trung"
    if qr_data.startswith("MN-"):
        return "Miền Nam"
    return "Miền khác"


# --- Lớp xử lý video ---
class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        decoded_objs = decode(gray)

        for obj in decoded_objs:
            qr_data = obj.data.decode("utf-8")

            # Đẩy dữ liệu vào hàng đợi toàn cục
            qr_queue.put(qr_data)

            (x, y, w, h) = obj.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 255, 0), 2)

        return img


# --- Khởi chạy camera ---
webrtc_streamer(
    key="camera",
    video_transformer_factory=VideoTransformer,
    media_stream_constraints={"video": True, "audio": False}
)

# --- Xử lý dữ liệu từ hàng đợi ---
while not qr_queue.empty():
    qr_data = qr_queue.get()
    if qr_data != st.session_state.last_qr:
        qr_region = classify_qr(qr_data)
        qr_entry = {
            "data": qr_data,
            "type": "QRCODE",
            "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "region": qr_region
        }
        st.session_state.qr_history.append(qr_entry)
        st.session_state.last_qr = qr_data
        st.experimental_rerun()

# --- Hiển thị kết quả ---
if st.session_state.last_qr:
    st.info(f"✅ Đã quét thành công mã QR: **{st.session_state.last_qr}**")

if st.session_state.qr_history:
    df = pd.DataFrame(st.session_state.qr_history)
    st.subheader("Lịch sử quét")
    st.dataframe(df, use_container_width=True)
