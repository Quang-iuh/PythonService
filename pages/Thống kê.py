import streamlit as st
import pandas as pd

st.title("📊 Trang Thống Kê")

# Khởi tạo danh sách lịch sử trong session_state nếu chưa có
if 'qr_history' not in st.session_state:
    st.session_state.qr_history = []

# ---
# HIỂN THỊ DỮ LIỆU THỐNG KÊ
# ---
st.subheader("Thông tin thống kê tổng quát")
total_scans = len(st.session_state.qr_history)

# Tạo các bộ dữ liệu cho từng miền
unique_north = set()
unique_central = set()
unique_south = set()

for item in st.session_state.qr_history:
    if item['data'].startswith("MB-"):
        unique_north.add(item['data'])
    elif item['data'].startswith("MT-"):
        unique_central.add(item['data'])
    elif item['data'].startswith("MN-"):
        unique_south.add(item['data'])

# Tổng số mã duy nhất của cả 3 miền
unique_scans = len(unique_north | unique_central | unique_south)

# Sử dụng 3 cột để hiển thị số liệu của từng miền
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Tổng số đã quét", total_scans)
with col2:
    st.metric("Miền Trung", len(unique_central))
with col3:
    st.metric("Miền Bắc", len(unique_north))
with col4:
    st.metric("Miền Nam", len(unique_south))



st.write("---")
# ---
# VẼ BIỂU ĐỒ
# ---
st.subheader("Biểu đồ Phân loại theo Miền")
chart_data = {
    'Miền': ['Miền Bắc', 'Miền Trung', 'Miền Nam'],
    'Số lượng': [len(unique_north), len(unique_central), len(unique_south)]
}
df_chart = pd.DataFrame(chart_data)
st.bar_chart(df_chart, x='Miền', y='Số lượng')

st.write("---")


# ---
# HIỂN THỊ LỊCH SỬ DƯỚI DẠNG BẢNG
# ---
st.subheader("Lịch sử quét mã")
if st.session_state.qr_history:
    df = pd.DataFrame(st.session_state.qr_history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Chưa có dữ liệu nào được quét. Vui lòng trở về trang Camera để quét mã.")
