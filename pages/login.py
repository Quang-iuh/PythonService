import time
import streamlit as st

from Component.Camera.CameraHeader import load_css
from Component.Login.Ui_Component import render_login_form, render_login_footer

# --- Cấu hình trang đăng nhập ---
st.set_page_config(
    page_title="🔐 Đăng nhập hệ thống",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS tùy chỉnh cho giao diện đăng nhập ---
load_css("LoginStyle.css")

# --- Khởi tạo session state ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Kiểm tra nếu đã đăng nhập ---
if st.session_state.logged_in:
    st.switch_page("Home.py")

# --- Giao diện đăng nhập ---
render_login_form()

# --- Form đăng nhập ---
with st.container():
    # Input fields với styling đẹp hơn
    username = st.text_input(
        "👤 Tên đăng nhập",
        placeholder="Nhập username...",
        label_visibility="visible"
    )

    password = st.text_input(
        "🔒 Mật khẩu",
        type="password",
        placeholder="Nhập password...",
        label_visibility="visible"
    )

    # Login button
    if st.button("🚀 ĐĂNG NHẬP", use_container_width=True):
        if username == "admin" and password == "123456":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Đăng nhập thành công!")
            time.sleep(1)
            st.switch_page("Home.py")
        else:
            st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")

        # --- Footer ---
render_login_footer()

# --- Thông tin đăng nhập mẫu ---
with st.expander("ℹ️ Thông tin đăng nhập mẫu"):
    st.info("""  
    **Tài khoản demo:**  
    - Username: `admin`  
    - Password: `123456`  
    """)