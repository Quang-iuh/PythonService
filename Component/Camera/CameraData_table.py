import streamlit as st
import pandas as pd


def render_qr_history_table(qr_data):
    """Render bảng lịch sử quét QR"""
    st.markdown("### 📋 Lịch sử quét mã")

    if qr_data:
        df = pd.DataFrame(qr_data)

        # Thống kê nhanh
        col1, col2, col3, col4 = st.columns(4)

        regions = df['region'].value_counts()
        with col1:
            st.metric("Miền Bắc", regions.get("Miền Bắc", 0))
        with col2:
            st.metric("Miền Trung", regions.get("Miền Trung", 0))
        with col3:
            st.metric("Miền Nam", regions.get("Miền Nam", 0))
        with col4:
            st.metric("Miền khác", regions.get("Miền khác", 0))

            # Bảng dữ liệu với styling
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            df[['data', 'region', 'time']],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔍 Chưa có dữ liệu. Hãy quét mã QR để bắt đầu!")