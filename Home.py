# app.py (Trang chính)
import streamlit as st

st.set_page_config(
    page_title="Báo cáo dữ liu",
)

st.title("Trang Chủ")
st.write("Sử dụng thanh điều hướng bên trái để chọn các chức năng:")
# Bạn có thể thêm nội dung cho trang chủ tại đây

# Thêm nút điều hướng đến trang "settings"
# LƯU Ý: Đảm bảo rằng bạn có một file tên là "setting.py" trong thư mục "pages"
st.page_link("pages/setting.py", label="Setting", icon="⚙️")
st.page_link("pages/Thống kê.py", label="Thống ke", icon="📈")
st.page_link("pages/camera.py", label="Camera", icon="📸")
