import os

import streamlit as st


def load_css(css_file):
    """Load CSS từ file external"""
    css_path = os.path.join("assets", "styles", css_file)
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def render_main_header(title: str, subtitle: str):
    """Render header chính của ứng dụng"""
    st.markdown(f"""  
    <div class="main-header">  
        <h1>{title}</h1>  
        <p>{subtitle}</p>  
    </div>  
    """, unsafe_allow_html=True)