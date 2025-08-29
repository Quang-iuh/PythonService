import streamlit as st

st.title("⚙️ Trang Cài đặt")
st.write("Đây là nơi bạn thiết lập cấu hình ứng dụng.")
import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()  # Ngăn nội dung phía dưới hiển thị

# Nội dung chính của trang
st.title("📷 Camera quét QR")

# Tạo biến trong session_state nếu chưa có
if "grayscale" not in st.session_state:
    st.session_state.grayscale = False
if "resolution" not in st.session_state:
    st.session_state.resolution = (640, 480)
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 1.0
if 'speed_motor' not in st.session_state:
        st.session_state.speed_motor = 10.0

# Điều chỉnh grayscale
st.session_state.grayscale = st.checkbox("Bật chế độ Grayscale", value=st.session_state.grayscale)
#điều chỉnh độ zoom
st.markdown("##### Điều chỉnh độ phóng đại (Zoom)")
st.session_state.zoom_level = st.slider(
    "Kéo thanh trượt để thay đổi mức phóng đại của camera:",
    min_value=1.0,
    max_value=3.0,
    value=st.session_state.zoom_level,
    step=0.1,
    help="Giá trị 1.0 là zoom mặc định, giá trị lớn hơn sẽ phóng to hình ảnh."
)
# Chọn độ phân giải
res = st.selectbox("Độ phân giải (Resolution)", ["640x480", "1280x720", "1920x1080"])
if res == "640x480":
    st.session_state.resolution = (640, 480)
elif res == "1280x720":
    st.session_state.resolution = (1280, 720)
else:
    st.session_state.resolution = (1920, 1080)

st.success(f"✅ Đã lưu: {st.session_state}")

#ie62eu chinh toc do dong co
st.markdown("##### Điều chỉnh tốc độ động cơ")
st.session_state.speed_motor = st.slider(
    "Kéo thanh trượt để thay đổi tốc độ động cơ (m/ph):",
    min_value=10.0,
    max_value=20.0,
    value=st.session_state.speed_motor,
    step=1.0,
    help="Điều chỉnh tốc độ động cơ với nút dặn."
)
st.sidebar.title(f"Chào {st.session_state.username}")
if st.sidebar.button("🔒 Đăng xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()