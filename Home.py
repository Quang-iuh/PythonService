# app.py (Trang chính)
import streamlit as st

st.set_page_config(
    page_title="Báo cáo dữ liu",
)
# Nội dung chính của trang
st.title("Trang Chủ")
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()  # Ngăn nội dung phía dưới hiển thị
# Nội dung chính của trang

st.write("Sử dụng thanh điều hướng bên trái để chọn các chức năng:")
# Bạn có thể thêm nội dung cho trang chủ tại đây

# Thêm nút điều hướng đến trang "settings"
# LƯU Ý: Đảm bảo rằng bạn có một file tên là "setting.py" trong thư mục "pages"
st.page_link("pages/setting.py", label="Setting", icon="⚙️")
st.page_link("pages/Thống kê.py", label="Thống ke", icon="📈")
st.page_link("pages/camera.py", label="Camera", icon="📸")
st.sidebar.title(f"Chào {st.session_state.username}")

if st.sidebar.button("🔒 Đăng xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()