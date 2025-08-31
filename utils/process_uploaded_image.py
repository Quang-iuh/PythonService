import streamlit as st
import cv2
from PIL import Image
import numpy as np
import pandas as pd

from utils.qr_storage import save_qr_data


def classify_qr(qr_data: str) -> str:
    qr_lower = qr_data.lower()
    if qr_data.startswith("MB-") or "mien bac" in qr_lower:
        return "Miền Bắc"
    if qr_data.startswith("MT-") or "mien trung" in qr_lower:
        return "Miền Trung"
    if qr_data.startswith("MN-") or "mien nam" in qr_lower:
        return "Miền Nam"
    return "Miền khác"


def process_uploaded_image():
    """Xử lý ảnh upload thay vì WebRTC camera"""
    st.markdown("### 📷 QR Scanner - Upload Image")

    uploaded_file = st.file_uploader(
        "Chọn ảnh chứa QR code",
        type=['png', 'jpg', 'jpeg'],
        help="Upload ảnh từ camera hoặc gallery"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã upload", use_column_width=True)

        # Convert to OpenCV format
        img_array = np.array(image)
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(img_array)

        if data:
            st.success(f"✅ QR Code detected: **{data}**")

            # Save to storage
            qr_region = classify_qr(data)
            qr_entry = {
                "data": data,
                "type": "QRCODE",
                "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "region": qr_region,
            }
            save_qr_data(qr_entry)
            st.rerun()  # Refresh để hiển thị data mới
        else:
            st.error("❌ Không tìm thấy QR code trong ảnh")