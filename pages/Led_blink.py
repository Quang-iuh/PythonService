import streamlit as st
import time
import struct
from datetime import datetime
from collections import deque
from utils.qr_storage import load_qr_data
from Component.Camera.CameraHeader import load_css

# Cấu hình trang
st.set_page_config(
    page_title="🚦 LED Controller - Counter Based",
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
if 'cb2_trigger_simulation' not in st.session_state:
    st.session_state.cb2_trigger_simulation = False
if 'processing_package' not in st.session_state:
    st.session_state.processing_package = None
if 'led_timer' not in st.session_state:
    st.session_state.led_timer = None

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Header
st.markdown("""  
<div class="main-header">  
    <h1>🚦 LED CONTROLLER - COUNTER BASED</h1>  
    <p>Phân loại dựa trên Package ID và Queue Management với PLC Snap7</p>  
</div>  
""", unsafe_allow_html=True)

# Load QR data
qr_data = load_qr_data()


def write_package_to_db10(self, package_id, region_code):
    """Ghi package vào DB10 array với Package ID làm index"""
    if not self.connected:
        return False

    try:
        # Tính offset trong DB10 array: mỗi package chiếm 4 bytes (2 cho ID, 2 cho region)
        array_offset = (package_id - 1) * 4

        # Ghi Package ID (2 bytes) và Region Code (2 bytes)
        package_data = bytearray(4)
        package_data[0:2] = package_id.to_bytes(2, 'big')
        package_data[2:4] = region_code.to_bytes(2, 'big')

        self.client.db_write(10, array_offset, package_data)
        return True
    except Exception as e:
        st.error(f"Lỗi ghi DB10: {str(e)}")
        return False


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


def simulate_cb2_sensor():
    """CB2 Sensor: PLC processing với DB10 Package Array"""
    if st.session_state.package_queue and st.session_state.cb2_trigger_simulation:
        # CB2 Sensor triggered - Dequeue FIFO
        current_package = st.session_state.package_queue.popleft()
        package_id, region_code = current_package
        region_name = region_code_to_name(region_code)

        # PLC Communication - Gửi vào DB10 Array
        add_to_log_stack(f"[CB2] Package {package_id} detected at sorting position")

        if 'plc_manager' in st.session_state and st.session_state.plc_connected:
            # Ghi vào DB10 Array với Package ID làm index
            success = st.session_state.plc_manager.write_package_to_db10(package_id, region_code)
            if success:
                add_to_log_stack(f"[DB10] Package ID:{package_id}, Region:{region_code} → Array[{package_id}]")
            else:
                add_to_log_stack(f"[ERROR] Failed to write to DB10")

                # Reset DB1,2,3 về 0
            st.session_state.plc_manager.write_db(1, 0, bytearray([0, 0]))
            st.session_state.plc_manager.write_db(2, 0, bytearray([0, 0]))
            st.session_state.plc_manager.write_db(3, 0, bytearray([0, 0]))

            # Gửi region code vào DB tương ứng
            if region_code == 1:  # Miền Nam
                st.session_state.plc_manager.write_db(1, 0, bytearray([0, 1]))
                add_to_log_stack(f"[PLC] DB1=1 (Miền Nam)")
            elif region_code == 2:  # Miền Bắc
                st.session_state.plc_manager.write_db(2, 0, bytearray([0, 1]))
                add_to_log_stack(f"[PLC] DB2=1 (Miền Bắc)")
            elif region_code == 3:  # Miền Trung
                st.session_state.plc_manager.write_db(3, 0, bytearray([0, 1]))
                add_to_log_stack(f"[PLC] DB3=1 (Miền Trung)")
        else:
            add_to_log_stack(f"[SIMULATION] DB10[{package_id}] = ({package_id}, {region_code})")

            # Kích hoạt LED
        if region_name in st.session_state.led_status:
            st.session_state.led_status[region_name] = True
            st.session_state.led_timer = time.time() + 3.0
            add_to_log_stack(f"[LED ON] {region_name} sáng!")

        st.session_state.cb2_trigger_simulation = False
        st.session_state.processing_package = None


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


process_new_packages()

# Xử lý CB2 sensor
simulate_cb2_sensor()

# Kiểm tra LED timer
check_led_timer()

# Control Panel
st.markdown("## 🎛️ Control Panel")

col_control1, col_control2, col_control3, col_control4 = st.columns(4)

with col_control1:
    st.metric("Package Counter", st.session_state.package_counter)

with col_control2:
    st.metric("Queue Size", len(st.session_state.package_queue))

with col_control3:
    if st.session_state.processing_package:
        pkg_id, region_code = st.session_state.processing_package
        st.metric("Processing", f"ID:{pkg_id}")
    else:
        st.metric("Processing", "None")

with col_control4:
    if st.button("🔄 Simulate CB2 Trigger", disabled=len(st.session_state.package_queue) == 0):
        st.session_state.cb2_trigger_simulation = True
        st.rerun()

    # Queue Display
st.markdown("### 📊 Package Queue (FIFO)")
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

# DB10 Array Status
st.markdown("### 🗄️ DB10 Package Array Status")
if 'plc_manager' in st.session_state and st.session_state.plc_connected:
    col_db1, col_db2, col_db3 = st.columns(3)

    with col_db1:
        st.markdown("**📊 Recent Packages in DB10:**")
        if st.session_state.package_counter > 0:
            # Hiển thị 5 packages gần nhất
            for i in range(max(1, st.session_state.package_counter - 4), st.session_state.package_counter + 1):
                package_data = st.session_state.plc_manager.read_package_from_db10(i)
                if package_data:
                    pkg_id, region_code = package_data
                    region_name = region_code_to_name(region_code)
                    st.text(f"Array[{i}]: ID={pkg_id}, Region={region_name}")
                else:
                    st.text(f"Array[{i}]: Empty")
        else:
            st.info("Chưa có packages trong DB10")

    with col_db2:
        st.markdown("**🎯 Current DB Status:**")
        st.text("DB1 (Miền Nam): Active" if st.session_state.led_status.get("Miền Nam", False) else "DB1: Inactive")
        st.text("DB2 (Miền Bắc): Active" if st.session_state.led_status.get("Miền Bắc", False) else "DB2: Inactive")
        st.text("DB3 (Miền Trung): Active" if st.session_state.led_status.get("Miền Trung", False) else "DB3: Inactive")

    with col_db3:
        st.markdown("**📈 Array Statistics:**")
        st.metric("Total Packages in Array", st.session_state.package_counter)
        st.metric("Array Size (bytes)", st.session_state.package_counter * 4)
        st.metric("Next Array Index", st.session_state.package_counter + 1)
else:
    st.warning("🔴 PLC chưa kết nối - DB10 monitoring không khả dụng")

# LED Display
st.markdown("### 💡 Trạng thái LED/Xy lanh")

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
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### ⚙️ Thông số hệ thống")
    st.metric("Tổng QR đã quét", len(qr_data))
    st.metric("Packages đã xử lý", st.session_state.package_counter - len(st.session_state.package_queue))

    # PLC Status
    if 'plc_connected' in st.session_state and st.session_state.plc_connected:
        st.success("🟢 PLC Connected")
    else:
        st.error("🔴 PLC Disconnected")

with col_info2:
    st.markdown("### 📋 Next Package in Queue")
    if st.session_state.package_queue:
        next_package = st.session_state.package_queue[0]
        pkg_id, region_code = next_package
        region_name = region_code_to_name(region_code)

        st.markdown(f"""  
        <div class="active-timer">  
            <strong>Package ID: {pkg_id}</strong><br>  
            <small>Region: {region_name} (Code: {region_code})</small><br>  
            <small>Status: Waiting for CB2 trigger</small>  
        </div>  
        """, unsafe_allow_html=True)
    else:
        st.info("Không có package trong queue")

    # Log Stack
st.markdown("### 📜 Log History (Real-time)")
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

    st.markdown("### 📊 Counter Statistics")
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

    # Auto refresh - chỉ khi không có CB2 trigger simulation
if not st.session_state.cb2_trigger_simulation:
    time.sleep(0.5)
    st.rerun()