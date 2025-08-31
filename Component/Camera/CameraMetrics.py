import streamlit as st


def render_metric_card(value: int, label: str):
    """Render một metric card"""
    st.markdown(f"""  
    <div class="metric-container">  
        <h3>{value}</h3>  
        <p>{label}</p>  
    </div>  
    """, unsafe_allow_html=True)


def render_system_metrics(total_scans: int, last_qr: str):
    """Render metrics hệ thống"""
    st.markdown("### 📊 Thông tin hệ thống")

    render_metric_card(total_scans, "Tổng số mã đã quét")

    if last_qr:
        st.markdown(f"""  
        <div class="metric-container">  
            <h4>Mã QR mới nhất:</h4>  
            <p><strong>{last_qr}</strong></p>  
        </div>  
        """, unsafe_allow_html=True)