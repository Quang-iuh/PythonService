import streamlit as st


def render_sidebar(username: str):
    """Render sidebar với thông tin user và controls"""
    with st.sidebar:
        st.markdown(f"""  
        <div class="sidebar-section">  
            <h3>👤 Người dùng</h3>  
            <p>Xin chào, <strong>{username}</strong></p>  
        </div>  
        """, unsafe_allow_html=True)
        if st.button("🔒 Đăng xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.switch_page("pages/Login.py")