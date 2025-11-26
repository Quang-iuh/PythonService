
import streamlit as st
import time
import base64

# Cấu hình trang

st.set_page_config(
    page_title="🔐 Đăng nhập QR System",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# CSS hiện đại
st.markdown("""  
<style>  
    
    .login-container {  
        max-width: 400px;  
        margin: 0 auto;  
        padding: 2rem;  
    }  

    .login-header {  
        background: linear-gradient(blue, white);  
        padding: 2rem;  
        border-radius: 20px 20px 0 0;  
        color: white;  
        text-align: center;  
    }  

    .login-form {  
        background: white;  
        padding: 2rem;  
        border-radius: 0 0 20px 20px;  
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);  
        border: 1px solid #e1e5e9;  
    }  

    .login-footer {  
        text-align: center;  
        margin-top: 2rem;  
        color: #6c757d;  
        font-size: 0.9rem;  
    }  

    .demo-info {  
        background: #f8f9fa;  
        padding: 1rem;  
        border-radius: 10px;  
        margin-top: 1rem;  
        border-left: 4px solid #28a745;  
    }  
</style>  
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Redirect nếu đã đăng nhập
if st.session_state.logged_in:
    st.switch_page("Home.py")

# Container chính
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Header
st.markdown("""  
<div class="login-header">  
    <h1>🔐 ĐĂNG NHẬP</h1>  
    <p>Hệ thống quét QR </p>  
</div>  
""", unsafe_allow_html=True)

# Form đăng nhập
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Gọi hàm ngoài định nghĩa
set_bg_image("image/IUH.jpg")

with ((st.container())):

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

    col_login, col_demo = st.columns([2, 1])

    with col_login:
        if st.button("🚀 ĐĂNG NHẬP", use_container_width=True, type="primary"):
            if username == "admin" and password == "123456"or username == "quang" and password == "2603":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Đăng nhập thành công!")
                time.sleep(1)
                st.switch_page("Home.py")
            else:
                st.error("❌ Sai thông tin đăng nhập!")

    with col_demo:
        if st.button("🎯 Truy Cập Nhanh", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.username = "demo_user"
            st.switch_page("Home.py")

        # Thông tin demo
st.markdown("""<div class="demo-info">  
    <strong>🔑 Thông tin đăng nhập:</strong><br>  
    Username: <code>admin</code><br>  
    Password: <code>123456</code><br>  
    <small>Hoặc click "Truy cập nhanh" để truy cập nhanh</small>  
</div>    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""  
<div class="login-footer">  
</div>  
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)