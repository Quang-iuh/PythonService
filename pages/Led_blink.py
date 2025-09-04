import streamlit as st
import time
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
load_css("Led_blinkStyle.css")
st.markdown("""  
<style>  
.led-off { background-color: #666; }  
.led-red { background-color: #ff4444; box-shadow: 0 0 20px #ff4444; }  
.led-yellow { background-color: #ffdd44; box-shadow: 0 0 20px #ffdd44; }  
.led-green { background-color: #44ff44; box-shadow: 0 0 20px #44ff44; }  
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

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Header
st.markdown("""  
<div class="main-header">  
    <h1>🚦 LED CONTROLLER - COUNTER BASED</h1>  
    <p>Phân loại dựa trên Package ID và Queue Management</p>  
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


def process_new_packages():
    """Xử lý packages mới - Counter-based approach"""
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

            add_to_log_stack(f"[NEW PACKAGE] ID:{package_id}, Region:{region} (Code:{region_code})")

        st.session_state.last_qr_count = len(qr_data)


def simulate_cb2_sensor():
    """Mô phỏng CB2 sensor trigger và PLC processing"""
    if st.session_state.package_queue and st.session_state.cb2_trigger_simulation:
        # CB2 Sensor triggered - Dequeue FIFO
        current_package = st.session_state.package_queue.popleft()
        package_id, region_code = current_package

        # Convert region code back to region name for display
        code_to_region = {1: "Miền Nam", 2: "Miền Bắc", 3: "Miền Trung", 0: "Miền khác"}
        region_name = code_to_region.get(region_code, "Miền khác")

        # PLC Communication: DB1 = Package ID, DB2 = Region Code
        add_to_log_stack(f"[PLC] DB1={package_id}, DB2={region_code} → Activate {region_name}")

        # Kích hoạt LED/Xy lanh
        if region_name in st.session_state.led_status:
            st.session_state.led_status[region_name] = True
            add_to_log_stack(f"[CYLINDER] {region_name} activated for Package {package_id}")

            # Tự động tắt LED sau 2s (simulation)
            time.sleep(0.1)  # Simulation delay
            st.session_state.led_status[region_name] = False
            add_to_log_stack(f"[CYLINDER] {region_name} deactivated")

        st.session_state.cb2_trigger_simulation = False

    # Xử lý packages mới


process_new_packages()

# Control Panel
st.markdown("## 🎛️ Control Panel")

col_control1, col_control2, col_control3 = st.columns(3)

with col_control1:
    st.metric("Package Counter", st.session_state.package_counter)

with col_control2:
    st.metric("Queue Size", len(st.session_state.package_queue))

with col_control3:
    if st.button("🔄 Simulate CB2 Trigger"):
        st.session_state.cb2_trigger_simulation = True
        st.rerun()

    # Queue Display
st.markdown("### 📊 Package Queue (FIFO)")
if st.session_state.package_queue:
    queue_data = []
    code_to_region = {1: "Miền Nam", 2: "Miền Bắc", 3: "Miền Trung", 0: "Miền khác"}

    for i, (pkg_id, region_code) in enumerate(st.session_state.package_queue):
        queue_data.append({
            "Position": i + 1,
            "Package ID": pkg_id,
            "Region Code": region_code,
            "Region": code_to_region.get(region_code, "Miền khác")
        })

    st.dataframe(queue_data, use_container_width=True)
else:
    st.info("Queue rỗng - chưa có packages")

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
    st.metric("Packages đã xử lý", st.session_state.package_counter)

with col_info2:
    st.markdown("### 📋 Next Package in Queue")
    if st.session_state.package_queue:
        next_package = st.session_state.package_queue[0]
        pkg_id, region_code = next_package
        code_to_region = {1: "Miền Nam", 2: "Miền Bắc", 3: "Miền Trung", 0: "Miền khác"}
        region_name = code_to_region.get(region_code, "Miền khác")

        st.markdown(f"""  
        <div class="active-timer">  
            <strong>Package ID: {pkg_id}</strong><br>  
            <small>Region: {region_name} (Code: {region_code})</small>  
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

# Auto refresh
time.sleep(0.5)
st.rerun()