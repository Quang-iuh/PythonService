import streamlit as st
import time
import struct
from datetime import datetime
from collections import deque
from utils.qr_storage import load_qr_data
from Component.Camera.CameraHeader import load_css

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
.led-container {  
    display: flex;  
    justify-content: center;  
    align-items: center;  
    margin: 20px 0;  
}  
.led-circle {  
    width: 80px;  
    height: 80px;  
    border-radius: 50%;  
    border: 3px solid #333;  
    margin: 0 20px;  
    display: flex;  
    align-items: center;  
    justify-content: center;  
    font-weight: bold;  
    color: white;  
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);  
}  
.led-off { background-color: #666; }  
.led-red { background-color: #ff4444; box-shadow: 0 0 20px #ff4444; }  
.led-yellow { background-color: #ffdd44; box-shadow: 0 0 20px #ffdd44; }  
.led-green { background-color: #44ff44; box-shadow: 0 0 20px #44ff44; }  
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
if 'led_status' not in st.session_state:
    st.session_state.led_status = {
        "Miền Bắc": False,
        "Miền Trung": False,
        "Miền Nam": False
    }
if 'log_stack' not in st.session_state:
    st.session_state.log_stack = []
if 'last_qr_count' not in st.session_state:
    st.session_state.last_qr_count = 0
if 'processing_package' not in st.session_state:
    st.session_state.processing_package = None
if 'led_timer' not in st.session_state:
    st.session_state.led_timer = None
if 'db_array_position' not in st.session_state:
    st.session_state.db_array_position = 1
if 'vfd_frequency' not in st.session_state:
    st.session_state.vfd_frequency = 0.0
if 'vfd_frequency_speed' not in st.session_state:
    st.session_state.vfd_frequency_speed = 0
# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()


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
        "Miền khác": 0
    }
    return region_mapping.get(region, 0)

def region_code_to_name(code):
    """Convert region code to name"""
    code_mapping = {
        1: "Miền Nam",
        2: "Miền Bắc",
        3: "Miền Trung",
        0: "Miền khác"
    }
    return code_mapping.get(code, "Miền khác")

def process_new_packages():
    """CB1 Sensor + Camera: Xử lý packages mới"""
    if len(qr_data) > st.session_state.last_qr_count:
        # Lấy tất cả QR mới
        new_qr_count = len(qr_data) - st.session_state.last_qr_count
        new_qrs = qr_data[-new_qr_count:]

        for new_qr in new_qrs:
            # CB1 Sensor: Đếm package
            st.session_state.package_counter += 1
            package_id = st.session_state.package_counter

            # Camera: Classification
            region = new_qr.get("region", "")
            region_code = classify_qr_to_region_code(region)

            # Lưu vào Queue (PackageID, RegionCode)
            package_address = (package_id, region_code)
            st.session_state.package_queue.append(package_address)

            add_to_log_stack(f"[CB1+CAMERA] Package ID:{package_id}, Region:{region} (Code:{region_code})")

        st.session_state.last_qr_count = len(qr_data)

def process_cb2_sensor():
    """CB2 Sensor: Sequential array storage cho DB1,2,3"""

    # Kiểm tra kết nối PLC
    if 'plc_manager' not in st.session_state or not st.session_state.plc_connected:
        return

        # Kiểm tra có package trong queue không
    if not st.session_state.package_queue:
        return

    try:
        # Đọc DB14[0] để detect CB2 trigger
        db14_data = st.session_state.plc_manager.read_db(14, 0, 2)

        if db14_data and len(db14_data) >= 2:
            db14_value = int.from_bytes(db14_data[0:2], byteorder='big')

            # Nếu DB14[0] = 1, xử lý package
            if db14_value == 1:
                # Dequeue package từ FIFO
                current_package = st.session_state.package_queue.popleft()
                package_id, region_code = current_package
                region_name = region_code_to_name(region_code)

                # Lấy vị trí hiện tại trong array
                current_position = st.session_state.db_array_position

                # Tính offset cho vị trí array (mỗi int = 2 bytes)
                array_offset = current_position * 2

                add_to_log_stack(f"[CB2] Processing Package {package_id} at position [{current_position}]")

                # Ghi vào DB arrays tại vị trí tuần tự
                if 'plc_manager' in st.session_state and st.session_state.plc_connected:
                    if region_code == 1:  # Miền Nam
                        st.session_state.plc_manager.write_db(1, array_offset, 1)
                        st.session_state.plc_manager.write_db(2, array_offset, 0)
                        st.session_state.plc_manager.write_db(3, array_offset, 0)
                        add_to_log_stack(
                            f"[PLC] DB1[{current_position}]=1, DB2[{current_position}]=0, DB3[{current_position}]=0")

                    elif region_code == 2:  # Miền Bắc
                        st.session_state.plc_manager.write_db(1, array_offset, 0)
                        st.session_state.plc_manager.write_db(2, array_offset, 2)
                        st.session_state.plc_manager.write_db(3, array_offset, 0)
                        add_to_log_stack(
                            f"[PLC] DB1[{current_position}]=0, DB2[{current_position}]=2, DB3[{current_position}]=0")

                    elif region_code == 3:  # Miền Trung
                        st.session_state.plc_manager.write_db(1, array_offset, 0)
                        st.session_state.plc_manager.write_db(2, array_offset, 0)
                        st.session_state.plc_manager.write_db(3, array_offset, 3)
                        add_to_log_stack(
                            f"[PLC] DB1[{current_position}]=0, DB2[{current_position}]=0, DB3[{current_position}]=3")
                    elif region_code == 0:  # Miền Khác
                        st.session_state.plc_manager.write_db(1, array_offset, 0)
                        st.session_state.plc_manager.write_db(2, array_offset, 0)
                        st.session_state.plc_manager.write_db(3, array_offset, 0)
                        add_to_log_stack(
                            f"[PLC] DB1[{current_position}]=0, DB2[{current_position}]=0, DB3[{current_position}]=0")

                        # Tăng array position cho lần tiếp theo
                st.session_state.db_array_position += 1

                # Reset về 0 nếu vượt quá 100
                if st.session_state.db_array_position > 100:
                    st.session_state.db_array_position = 0
                    add_to_log_stack("[ARRAY] Reset position to 0")

                    # Kích hoạt LED
                if region_name in st.session_state.led_status:
                    st.session_state.led_status[region_name] = True
                    st.session_state.led_timer = time.time() + 3.0
                    add_to_log_stack(f"[LED ON] {region_name} activated")

    except Exception as e:
        add_to_log_stack(f"[ERROR] Lỗi đọc DB14[0]: {str(e)}")

def check_led_timer():
    """Kiểm tra và tắt LED sau thời gian quy định"""
    if hasattr(st.session_state, 'led_timer') and st.session_state.led_timer:
        if time.time() >= st.session_state.led_timer:
            # Tắt tất cả LED
            for region in st.session_state.led_status:
                if st.session_state.led_status[region]:
                    st.session_state.led_status[region] = False
                    add_to_log_stack(f"[LED OFF] {region} tắt")
            st.session_state.led_timer = None

        # Xử lý packages mới

    def read_vfd_frequency():
        """Đọc tần số biến tần từ DB4"""
        if 'plc_manager' not in st.session_state or not st.session_state.plc_connected:
            return 0.0

        try:
            # Đọc DB4 - giả sử frequency được lưu ở offset 0, 2 bytes
            db4_data = st.session_state.plc_manager.read_db(4, 4, 2)

            if db4_data and len(db4_data) >= 2:
                # Convert 2 bytes thành integer (big-endian)
                frequency_raw = int.from_bytes(db4_data[0:2], byteorder='big')
                frequency = frequency_raw
                st.session_state.vfd_frequency_speed = frequency*120/200
                return frequency
            return 0
        except Exception as e:
            add_to_log_stack(f"[ERROR] Lỗi đọc frequency DB4: {str(e)}")
            return 0.0

process_new_packages()

# Xử lý CB2 sensors
process_cb2_sensor()

# Kiểm tra LED timer
check_led_timer()

# Control Panel
#st.markdown("<h2 style='text-align: center;'>🎛️ Bộ đếm</h2>", unsafe_allow_html=True)

#col_control1, col_control2, col_control3 = st.columns(3)

#with col_control1:
#    st.metric("Sản phẩm đã quét", st.session_state.package_counter)

#with col_control2:
#    st.metric("Số lượng hàng hóa truyền cho PLC", len(st.session_state.package_queue))
#with col_control3:
#    if st.session_state.processing_package:
#        pkg_id, region_code = st.session_state.processing_package
#        st.metric("Processing", f"ID:{pkg_id}")
#    else:
#        st.metric("Processing", "None")

col_info1, col_info2, col_info3= st.columns(3)

with col_info1:
    st.markdown("#### ⚙️ Thông số hệ thống")
    st.metric("Tổng QR đã quét", len(qr_data))
    st.metric("Packages đã xử lý", st.session_state.package_counter - len(st.session_state.package_queue))

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
            <strong>Mã ID: {pkg_id}</strong><br>  
            <small>Khu vực: {region_name} (Code: {region_code})</small><br>  
            <small>trạng thái: Chờ tín hiệu từ cảm bien phân loại</small>  
        </div>  
        """, unsafe_allow_html=True)
    else:
        st.info("Không có package trong queue")

    # Log Stack
with col_info3:
    # Thêm hiển thị tần số biến tần
    st.markdown("#### ⚡ Tần số động cơ")
    st.metric(
        "",
        f"{st.session_state.vfd_frequency:.1f} Hz",
        delta=None
    )
    st.markdown("#### 🏎️ Tốc độ động cơ")
    st.metric(
        "",
        f"{st.session_state.vfd_frequency_speed:.1f} vòng/phút",
        delta=None
    )
    # Queue Display
st.markdown("<h2 style='text-align: center;'> 📊 Gói hàng chờ</2>", unsafe_allow_html=True)
if st.session_state.package_queue:
    queue_data = []

    for i, (pkg_id, region_code) in enumerate(st.session_state.package_queue):
        queue_data.append({
            "Position": i + 1,
            "Package ID": pkg_id,
            "Region Code": region_code,
            "Region": region_code_to_name(region_code),
            "Status": "Waiting for CB2"
        })

    st.dataframe(queue_data, use_container_width=True)
else:
    st.info("Queue rỗng - chưa có packages")

# LED Display
st.markdown("### 💡 Trạng thái gói hàng được truyền")

col1, col2, col3 = st.columns(3)
regions = ["Miền Bắc", "Miền Trung", "Miền Nam"]
colors = ["red", "yellow", "green"]

for i, (region, color) in enumerate(zip(regions, colors)):
    with [col1, col2, col3][i]:
        led_class = f"led-{color}" if st.session_state.led_status[region] else "led-off"

        st.markdown(f"""  
        <div class="led-container">  
            <div>  
                <div class="led-circle {led_class}">{region[:2]}</div>  
                <div class="region-info">  
                    <strong>{region}</strong><br>  
                    Code: {classify_qr_to_region_code(region)}  
                </div>  
            </div>  
        </div>  
        """, unsafe_allow_html=True)

    # System Info
st.markdown("### 📜 Lịch sử đơn hàng ")
if st.session_state.log_stack:
    recent_logs = st.session_state.log_stack[-10:]
    for log in reversed(recent_logs):
        st.text(log)
else:
    st.info("Chưa có log nào...")

# Sidebar
with st.sidebar:
    st.markdown(f"""  
    <div class="sidebar-section">  
        <h3>👤 Người dùng</h3>  
        <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>  
    </div>  
    """, unsafe_allow_html=True)

    st.markdown("""        
    <div class="sidebar-section">        
        <h3>📊 Thống kê nhanh</h3>        
    </div>        
    """, unsafe_allow_html=True)
    st.metric("Total Packages", st.session_state.package_counter)
    st.metric("Queue Length", len(st.session_state.package_queue))
    st.metric("Processed", st.session_state.package_counter - len(st.session_state.package_queue))

    if st.session_state.package_queue:
        st.write("**Next 3 in Queue:**")
        for i, (pkg_id, region_code) in enumerate(list(st.session_state.package_queue)[:3]):
            code_to_region = {1: "MN", 2: "MB", 3: "MT", 0: "Other"}
            region_short = code_to_region.get(region_code, "Other")
            st.write(f"{i + 1}. ID:{pkg_id} → {region_short}")

    st.markdown("---")

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/login.py")
    time.sleep(0.5)
    st.rerun()