import streamlit as st
import time
from datetime import datetime
from collections import deque
from Component.Camera.CameraData_table import render_qr_history_table
from utils.qr_storage import load_qr_data, reset_daily_data
from Component.Camera.CameraHeader import load_css

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

col_h1,col_h2 = st.columns([1,3])
with col_h1:
    if st.button("⬅️ Quay về", use_container_width=True, type="secondary"):
        st.switch_page("Home.py")
with col_h2:
    st.markdown("")
# Cấu hình trang
st.set_page_config(
    page_title="PLC",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load CSS
load_css("Led_BlinkStyle.css")
st.markdown("""  
<style>  
.main-header {  
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  
    padding: 1.5rem;  
    border-radius: 10px;  
    color: white;  
    text-align: center;  
    margin-bottom: 2rem;  
}   
.region-info {  
    text-align: center;  
    margin-top: 10px;  
    font-size: 14px;  
    color: #666;  
}  
.active-timer {  
    background: #fff3e0;  
    padding: 8px;  
    margin: 3px 0;  
    border-radius: 3px;  
    border-left: 3px solid #ff9800;  
}  
.sidebar-section {  
    background: #f8f9fa;  
    padding: 1rem;  
    border-radius: 8px;  
    margin: 1rem 0;  
    border-left: 4px solid #667eea;  
}  
</style>  
""", unsafe_allow_html=True)

# Khởi tạo session state cho counter-based approach
if 'package_counter' not in st.session_state:
    st.session_state.package_counter = 0
if 'package_queue' not in st.session_state:
    st.session_state.package_queue = deque()  # FIFO queue
if 'log_stack' not in st.session_state:
    st.session_state.log_stack = []
if 'last_qr_count' not in st.session_state:
    st.session_state.last_qr_count = 0
if 'processing_package' not in st.session_state:
    st.session_state.processing_package = None
if 'db_array_position' not in st.session_state:
    st.session_state.db_array_position = 1
if 'vfd_frequency' not in st.session_state:
    st.session_state.vfd_frequency = 0.0
if 'confirm_reset' not in st.session_state:
    st.session_state.confirm_reset = False


# Header
st.markdown("""  
<div class="main-header">  
    <h1>📡 TRUYỀN TÍN HIỆU CHO PLC</h1>    
</div>  
""", unsafe_allow_html=True)

# Load QR data
qr_data = load_qr_data()

# Functions
def add_to_log_stack(message):
    """Thêm log vào stack"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.log_stack.append(log_entry)

    if len(st.session_state.log_stack) > 20:
        st.session_state.log_stack.pop(0)

def classify_qr_to_region_code(region):
    """Convert region name to region code"""
    region_mapping = {
        "Miền Nam": 1,
        "Miền Bắc": 2,
        "Miền Trung": 3,
        "Miền khác": 4
    }
    return region_mapping.get(region, 0)

def region_code_to_name(code):
    """Convert region code to name"""
    code_mapping = {
        1: "Miền Nam",
        2: "Miền Bắc",
        3: "Miền Trung",
        4: "Miền khác"
    }
    return code_mapping.get(code, "Miền khác")


# Thêm vào session state initialization (dòng 62-77)
if 'last_trigger_state' not in st.session_state:
    st.session_state.last_trigger_state = 0


def process_sensor_trigger():
    """Xử lý khi cảm biến CB1/CB2 trigger (gộp chung)"""
    if 'plc_manager' not in st.session_state or not st.session_state.plc_connected:
        return

    try:
        db14_data = st.session_state.plc_manager.read_db(14, 0, 2)

        if db14_data and len(db14_data) >= 2:
            trigger_value = int.from_bytes(db14_data[0:2], byteorder='big')

            # ✅ CHỈ xử lý khi trigger thay đổi từ 0 → 1 (rising edge)
            if trigger_value == 1 and st.session_state.last_trigger_state == 0:
                # Tăng bộ đếm và vị trí
                st.session_state.package_counter += 1
                package_id = st.session_state.package_counter
                current_position = st.session_state.db_array_position
                array_offset = current_position * 2

                # Kiểm tra có QR mới không
                if len(qr_data) > st.session_state.last_qr_count:
                    latest_qr = qr_data[-1]
                    region = latest_qr.get("region", "")
                    region_code = classify_qr_to_region_code(region)
                    st.session_state.plc_manager.write_db(1, array_offset, region_code)
                    st.session_state.last_qr_count = len(qr_data)
                    add_to_log_stack(f"[SENSOR] Package {package_id} - Region: {region} (Code: {region_code})")
                else:
                    # Không có QR - ghi 0 thay vì 4
                    st.session_state.plc_manager.write_db(1, array_offset, 0)
                    add_to_log_stack(f"[SENSOR] Package {package_id} - No QR detected")

                    # Tăng vị trí SAU KHI ghi xong
                st.session_state.db_array_position += 1
                if st.session_state.db_array_position > 100:
                    st.session_state.db_array_position = 0

                    # ✅ Lưu trạng thái trigger hiện tại
            st.session_state.last_trigger_state = trigger_value

    except Exception as e:
        add_to_log_stack(f"[ERROR] Lỗi xử lý sensor: {str(e)}")

process_sensor_trigger()
        # Xử lý packages mới
       # Đọc tần số biến tần từ DB4
def read_vfd_frequency():
    if 'plc_manager' not in st.session_state or not st.session_state.plc_connected:
        return 0.0

    try:
            # Đọc DB4 - giả sử frequency được lưu ở offset 0, 2 bytes
        db4_data = st.session_state.plc_manager.read_db(14, 2, 2)

        if db4_data and len(db4_data) >= 2: #dữ liệu phải có ít nhất 2 byte.
                # Convert 2 bytes thành integer (big-endian)
            frequency_raw = int.from_bytes(db4_data[0:2], byteorder='big')
            frequency = frequency_raw
            return frequency
        return 0
    except Exception as e:
        add_to_log_stack(f"[ERROR] Lỗi đọc frequency DB4: {str(e)}")
        return 0.0



# process_sensor_trigger
process_sensor_trigger()


col_info1, col_info2, col_info3= st.columns(3)

with col_info1:
    st.markdown("#### ⚙️ Thông số hệ thống")
    st.metric("Tổng QR đã quét", len(qr_data))
    st.metric("Tổng QR đã gữi cho PLC", st.session_state.package_counter - len(st.session_state.package_queue))
    # Thêm đọc DB14.ID[2]

    # PLC Status
    if 'plc_connected' in st.session_state and st.session_state.plc_connected:
        st.success("🟢 PLC Connected")
    else:
        st.error("🔴 PLC Disconnected")

with col_info2:
    st.markdown("#### 📋 Gói hàng tiếp theo")
    if st.session_state.package_queue:
        next_package = st.session_state.package_queue[0]
        pkg_id, region_code = next_package
        region_name = region_code_to_name(region_code)

        st.markdown(f"""  
        <div class="active-timer">  
            <strong>Khay số: {region_code}</strong><br>  
            <small>Khu vực: {region_name} (Mã: {region_code})</small><br>  
            <small>Trạng thái: Chờ tín hiệu từ cảm biến</small>  
        </div>  
        """, unsafe_allow_html=True)
    else:
        st.info("Chờ gói hàng tiếp theo...")

    # Log Stack
with col_info3:
    # Thêm hiển thị tần số biến tần
    db14_value = 0
    if 'plc_manager' in st.session_state and st.session_state.plc_connected:
        db14_data = st.session_state.plc_manager.read_db(14, 4, 2)  # Offset 4 cho ID[2]
        if db14_data and len(db14_data) >= 2:
            db14_value = int.from_bytes(db14_data[0:2], byteorder='big')
            st.session_state.vfd_frequency_speed=db14_value*120/120
    st.markdown("#### ⚡ Tần số động cơ", unsafe_allow_html=True)
    st.metric(
        label=(""),
        value=f"{db14_value:.0f} Hz"
    )
st.markdown("<h3 style='text-align: center;'> 🚚Hàng đang được xử lý</3>",unsafe_allow_html=True)
if st.session_state.package_queue:
    queue_data = []
    for i, (pkg_id, region_code) in enumerate(st.session_state.package_queue):
        queue_data.append({
            "Số thứ tự": i + 1,
            "Khay hàng số": region_code,
            "Vùng miền": region_code_to_name(region_code)
        })

    st.dataframe(queue_data, use_container_width=True)
else:
    st.info("Chưa có đơn hàng nào...")
    # Queue Display
st.markdown("<h2 style='text-align: center;'> 🗑️ Quản lý dữ liệu</2>", unsafe_allow_html=True)
st.markdown("---")
render_qr_history_table(qr_data)

 # Reset Data Button

if st.button("🔄 Reset dữ liệu lưu trữ", use_container_width=True, type="secondary"):
    from utils.qr_storage import reset_daily_data

    # Ghi số 1 vào DB14.1 (offset 2, vì DB14.0 là offset 0-1)
    if 'plc_manager' in st.session_state and st.session_state.plc_connected:
        # Tạo bytearray chứa 202 bytes (101 positions × 2 bytes) = tất cả là 0
        zero_array = bytearray(202)

        # Ghi 1 lần cho mỗi DB thay vì 101 lần
        st.session_state.plc_manager.client.db_write(1, 0, zero_array)
        add_to_log_stack("Đã reset dữ liệu danh sách 1")

        st.session_state.plc_manager.client.db_write(2, 0, zero_array)
        add_to_log_stack("Đã reset dữ liệu danh sách 2")

        st.session_state.plc_manager.client.db_write(3, 0, zero_array)
        add_to_log_stack("Đã reset dữ liệu danh sách 3")

        # Ghi tín hiệu reset
        success = st.session_state.plc_manager.write_db(14, 2, 1)
        if success:
            add_to_log_stack("[PLC] Đã ghi DB14.1 = 1 (Reset signal)")
        else:
            st.error("❌ Lỗi reset bộ nhớ..., Xem lại kết nối dây")
            st.stop()

    if reset_daily_data():
        # Reset session state
        st.session_state.package_counter = 0
        st.session_state.package_queue.clear()
        st.session_state.last_qr_count = 0
        st.session_state.log_stack = []
        st.session_state.db_array_position = 1

        # Ghi số 0 vào DB14.1 sau khi reset xong
        if 'plc_manager' in st.session_state and st.session_state.plc_connected:
            success = st.session_state.plc_manager.write_db(14, 2, 0)
            if success:
                add_to_log_stack("[PLC] Đã ghi DB14.1 = 0 (Reset complete)")
            else:
                st.warning("⚠️ Không thể reset DB14.1 về 0")

        st.success("✅ Đã reset toàn bộ dữ liệu!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("❌ Lỗi khi reset dữ liệu")


# Sidebar
with st.sidebar:
    st.markdown(f"""  
        <div class="sidebar-section">  
            <h3>👤 Người dùng</h3>  
            <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>  
        </div>  
        """, unsafe_allow_html=True)
    col1_im, col2_im, col3_im = st.columns([1, 2, 1])
    with col1_im:
        st.markdown("")
    with col2_im:
        st.image("image/Logo.png", width=120)
    with col3_im:
        st.markdown("")

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/Login.py")

    # Auto-refresh loop - ĐẶT Ở NGOÀI SIDEBAR
time.sleep(0.5)
st.rerun()