import streamlit as st

# --- Khởi tạo session state ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Đăng nhập")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50; /* xanh lá */
        color: white;
        font-size: 18px;
        border-radius: 10px;
        height: 50px;
        width: 200px;
    }
    .stButton>button:hover {
        background-color: #45a049; /* xanh đậm hơn khi hover */
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)


if st.button("login"):
    # Ví dụ kiểm tra tạm thời
    if username == "admin" and password == "123456":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Đăng nhập thành công! Hãy chuyển sang trang camera.")
    else:
        st.error("Sai tên đăng nhập hoặc mật khẩu")
