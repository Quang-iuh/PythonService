import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import pandas as pd

# --- Cấu hình trang ---
st.set_page_config(page_title="Quét Mã QR", layout="wide")

st.title("📷 Trang Quét Mã QR")
st.write("Sử dụng camera của bạn để quét và phân loại mã QR.")
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()  # Ngăn nội dung phía dưới hiển thị
# --- Khởi tạo session state ---
if "qr_history" not in st.session_state:
    st.session_state.qr_history = []
if "last_qr" not in st.session_state:
    st.session_state.last_qr = ""


# --- Hàm phân loại mã QR ---
def classify_qr(qr_data: str) -> str:
    if qr_data.startswith("MB-"):
        return "Miền Bắc"
    if qr_data.startswith("MT-"):
        return "Miền Trung"
    if qr_data.startswith("MN-"):
        return "Miền Nam"
    return "Miền khác"


# --- Lớp xử lý video với QRCodeDetector ---
class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Phát hiện và giải mã QR
        data, points, _ = self.detector.detectAndDecode(img)

        if points is not None and data:
            points = points[0].astype(int)
            for j in range(len(points)):
                pt1 = tuple(points[j])
                pt2 = tuple(points[(j + 1) % len(points)])
                cv2.line(img, pt1, pt2, (0, 255, 0), 2)

            # Nếu là mã QR mới thì lưu
            if data != st.session_state.last_qr:
                qr_region = classify_qr(data)
                qr_entry = {
                    "data": data,
                    "type": "QRCODE",
                    "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "region": qr_region,
                }
                st.session_state.qr_history.append(qr_entry)
                st.session_state.last_qr = data

            cv2.putText(img, data, (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return img


# --- Khởi chạy camera ---
webrtc_streamer(
    key="camera",
    video_processor_factory=VideoTransformer,   # thay vì video_transformer_factory
    media_stream_constraints={"video": True, "audio": False},
)

# --- Hiển thị kết quả ---
if st.session_state.last_qr:
    st.info(f"✅ Đã quét thành côngrun mã QR: **{st.session_state.last_qr}**")

if st.session_state.qr_history:
    df = pd.DataFrame(st.session_state.qr_history)
    st.subheader("📜 Lịch sử quét")
    st.dataframe(df, use_container_width=True)
st.sidebar.title(f"Chào {st.session_state.username}")
if st.sidebar.button("🔒 Đăng xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()