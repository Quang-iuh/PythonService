import streamlit as st


def check_login():
    """Kiểm tra trạng thái đăng nhập"""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 Vui lòng đăng nhập để truy cập hệ thống")
        return False
    return True