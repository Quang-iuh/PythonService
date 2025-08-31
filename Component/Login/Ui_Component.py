import streamlit as st

from Component.Camera.CameraHeader import load_css

load_css("LoginStyle.css")

def render_login_form():
    """Render form đăng nhập"""
    st.markdown("""  
    <div class="main-container">  
        <div class="login-card">  
            <div class="login-header">  
                <h1 class="login-title">🔐 ĐĂNG NHẬP</h1>  
                <p class="login-subtitle">Vui lòng nhập thông tin để truy cập hệ thống QR Scanner</p>  
            </div>  
    """, unsafe_allow_html=True)


def render_login_footer():
    """Render footer đăng nhập"""
    st.markdown("""  
            <div class="login-footer">  
                <p>🔬 <strong>Hệ thống QR Scanner</strong></p>  
                <p>Phiên bản 1.0 - Công nghệ nhận diện tự động</p>  
            </div>  
        </div>  
    </div>  
    """, unsafe_allow_html=True)