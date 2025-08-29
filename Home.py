# app.py (Trang chính)
import streamlit as st

st.set_page_config(
    page_title="Ứng Dụng Đa Trang",
)

st.title("Đây là Trang Chủ")
st.header("Cách sử dụng")
st.write("Sử dụng thanh điều hướng bên trái để chọn các chức năng:")
st.markdown("- **📊 Trang Phân Tích**: Xem báo cáo chi tiết về hiệu suất phân loại.")
st.markdown("- **⚙️ Cài Đặt**: Tùy chỉnh các thông số của ứng dụng.")
st.markdown("- **📸 Trang camera**.")
# Bạn có thể thêm nội dung cho trang chủ tại đây
st.header("Chào mừng đến với ứng dụng của bạn!")
st.write("Sử dụng thanh bên để điều hướng giữa các trang.")

# Thêm nút điều hướng đến trang "settings"
# LƯU Ý: Đảm bảo rằng bạn có một file tên là "setting.py" trong thư mục "pages"
st.page_link("pages/setting.py", label="Setting", icon="⚙️")
st.page_link("pages/Thống kê.py", label="Thống ke", icon="📈")
st.page_link("pages/camera.py", label="Camera", icon="📸")
