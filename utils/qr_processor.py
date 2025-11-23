import pandas as pd
import logging
from utils.qr_storage import save_qr_data, get_last_qr

logger = logging.getLogger(__name__)
def classify_qr(qr_data: str) -> str:
    """Phân loại QR theo miền"""
    qr_lower = qr_data.lower()
    if qr_data.startswith("MB-") or "mien bac" in qr_lower:
        return "Miền Bắc"
    if qr_data.startswith("MT-") or "mien trung" in qr_lower:
        return "Miền Trung"
    if qr_data.startswith("MN-") or "mien nam" in qr_lower:
        return "Miền Nam"
    return "Miền khác"


def process_qr_detection(data: str) -> bool:
    """Xử lý QR được detect, return True nếu là QR mới"""
    try:
        last_qr = get_last_qr()
        if data != last_qr:
            qr_region = classify_qr(data)
            qr_entry = {
                "data": data,
                "type": "QR_code",
                "time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "region": qr_region,
            }
            save_qr_data(qr_entry)
            logger.info(f"QR Detected: {data} | Region: {qr_region}")
            return True
    except Exception as e:
        logger.error(f"Error saving QR data: {e}")
    return False