import streamlit as st
import pandas as pd

st.title("📊 Trang Thống Kê")
import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()  # Ngăn nội dung phía dưới hiển thị

# Nội dung chính của trang

# Khởi tạo qr_history nếu chưa có
if 'qr_history' not in st.session_state:
    st.session_state.qr_history = []

st.subheader("Thông tin thống kê tổng quát")
total_scans = len(st.session_state.qr_history)

# Tách dữ liệu theo miền
unique_north = {item["data"] for item in st.session_state.qr_history if item["region"]=="Miền Bắc"}
unique_central = {item["data"] for item in st.session_state.qr_history if item["region"]=="Miền Trung"}
unique_south = {item["data"] for item in st.session_state.qr_history if item["region"]=="Miền Nam"}

# Tổng số mã duy nhất
unique_scans = len(unique_north | unique_central | unique_south)

# Hiển thị số liệu theo cột
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng số đã quét", total_scans)
col2.metric("Miền Trung", len(unique_central))
col3.metric("Miền Bắc", len(unique_north))
col4.metric("Miền Nam", len(unique_south))

st.write("---")

# Biểu đồ phân loại theo miền
st.subheader("Biểu đồ Phân loại theo Miền")
chart_data = {
    'Miền': ['Miền Bắc', 'Miền Trung', 'Miền Nam'],
    'Số lượng': [len(unique_north), len(unique_central), len(unique_south)]
}
df_chart = pd.DataFrame(chart_data)
st.bar_chart(df_chart, x='Miền', y='Số lượng')

st.write("---")

st.sidebar.title(f"Chào {st.session_state.username}")
if st.sidebar.button("🔒 Đăng xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()