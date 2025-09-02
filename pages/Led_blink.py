import streamlit as st
import time
from datetime import datetime
from utils.qr_storage import load_qr_data
from Component.Camera.CameraHeader import load_css

# Cấu hình trang
st.set_page_config(
    page_title="🚦 LED Controller",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS từ file external
load_css("Led_blinkStyle.css")

# Khởi tạo session state
if 'distanceMN' not in st.session_state:
    st.session_state.distanceMN = 750
if 'distanceMT' not in st.session_state:
    st.session_state.distanceMT = 500
if 'distanceMB' not in st.session_state:
    st.session_state.distanceMB = 250
if 'speed_motor' not in st.session_state:
    st.session_state.speed_motor = 10.0
if 'led_status' not in st.session_state:
    st.session_state.led_status = {
        "Miền Bắc": False,
        "Miền Trung": False,
        "Miền Nam": False
    }
if 'active_timers' not in st.session_state:
    st.session_state.active_timers = {}
if 'log_stack' not in st.session_state:
    st.session_state.log_stack = []
if 'last_qr_count' not in st.session_state:
    st.session_state.last_qr_count = 0

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Header - sử dụng CSS class thay vì inline style
st.markdown("""  
<div class="main-header">  
    <h1>🚦 LED CONTROLLER</h1>  
    <p>Xử lý LED song song theo thời gian thực tế</p>  
</div>  
""", unsafe_allow_html=True)

# Load QR data hiện tại
qr_data = load_qr_data()

# Input khoảng cách
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    st.session_state.distanceMB = st.number_input(
        "Khoảng cách Miền Bắc (mm)",
        min_value=0, max_value=2000,
        value=st.session_state.distanceMB,
        step=1
    )

with col_input2:
    st.session_state.distanceMT = st.number_input(
        "Khoảng cách Miền Trung (mm)",
        min_value=0, max_value=2000,
        value=st.session_state.distanceMT,
        step=1
    )

with col_input3:
    st.session_state.distanceMN = st.number_input(
        "Khoảng cách Miền Nam (mm)",
        min_value=0, max_value=2000,
        value=st.session_state.distanceMN,
        step=1
    )

# Distance mapping
distance_map = {
    "Miền Bắc": st.session_state.distanceMB,
    "Miền Trung": st.session_state.distanceMT,
    "Miền Nam": st.session_state.distanceMN
}

# Tính tốc độ
v = st.session_state.speed_motor * 1000 / 60  # mm/s


# Functions
def add_to_log_stack(message):
    """Thêm log vào stack"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.log_stack.append(log_entry)

    if len(st.session_state.log_stack) > 20:
        st.session_state.log_stack.pop(0)


def process_parallel_timers():
    """Xử lý parallel timers - mỗi QR có timer riêng"""
    current_time = time.time()
    completed_timers = []

    for timer_id, timer in st.session_state.active_timers.items():
        elapsed = current_time - timer['start_time']

        if timer['status'] == 'waiting' and elapsed >= timer['delay']:
            # Bật LED
            st.session_state.led_status[timer['region']] = True
            timer['status'] = 'led_on'
            timer['led_on_time'] = current_time
            add_to_log_stack(f"[LED ON] {timer['region']} sáng! (Delay: {timer['delay']:.1f}s)")

        elif timer['status'] == 'led_on' and elapsed >= timer['delay'] + 2:
            # Tắt LED sau 2s
            st.session_state.led_status[timer['region']] = False
            timer['status'] = 'completed'
            add_to_log_stack(f"[LED OFF] {timer['region']} tắt")
            completed_timers.append(timer_id)

            # Xóa completed timers
    for timer_id in completed_timers:
        del st.session_state.active_timers[timer_id]

    # Monitor QR data và xử lý tất cả QR mới


if len(qr_data) > st.session_state.last_qr_count:
    # Lấy tất cả QR mới, không chỉ QR cuối
    new_qr_count = len(qr_data) - st.session_state.last_qr_count
    new_qrs = qr_data[-new_qr_count:]

    for new_qr in new_qrs:
        region = new_qr.get("region", "")

        if region in distance_map:
            current_time = time.time()
            delay = distance_map[region] / v if v > 0 else 0

            # Tạo timer riêng cho mỗi QR
            timer_id = f"{region}_{current_time}"
            st.session_state.active_timers[timer_id] = {
                'start_time': current_time,
                'delay': delay,
                'region': region,
                'status': 'waiting',
                'qr_data': new_qr.get("data", "")
            }

            add_to_log_stack(f"[NEW QR] {region} - Delay: {delay:.1f}s")

    st.session_state.last_qr_count = len(qr_data)

# Xử lý parallel processing
process_parallel_timers()

# LED Display
st.markdown("### 💡 Trạng thái LED")

col1, col2, col3 = st.columns(3)
regions = ["Miền Bắc", "Miền Trung", "Miền Nam"]
colors = ["red", "yellow", "green"]

for i, (region, color) in enumerate(zip(regions, colors)):
    with [col1, col2, col3][i]:
        led_class = f"led-{color}" if st.session_state.led_status[region] else "led-off"
        distance = distance_map[region]
        delay = distance / v if v > 0 else 0

        st.markdown(f"""  
        <div class="led-container">  
            <div>  
                <div class="led-circle {led_class}">{region[:2]}</div>  
                <div class="region-info">  
                    <strong>{region}</strong><br>  
                    {distance}mm - {delay:.1f}s  
                </div>  
            </div>  
        </div>  
        """, unsafe_allow_html=True)

    # System Info
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### ⚙️ Thông số hệ thống")
    st.metric("Tốc độ băng tải", f"{v:.1f} mm/s")
    st.metric("Tổng QR đã quét", len(qr_data))

with col_info2:
    st.markdown("### ⚡ Active Timers")
    if st.session_state.active_timers:
        current_time = time.time()
        for timer_id, timer in st.session_state.active_timers.items():
            elapsed = current_time - timer['start_time']
            if timer['status'] == 'waiting':
                remaining = max(0, timer['delay'] - elapsed)
                st.markdown(f"""  
                <div class="active-timer">  
                    <strong>{timer['region']}</strong> - Chờ<br>  
                    <small>Còn: {remaining:.1f}s</small>  
                </div>  
                """, unsafe_allow_html=True)
            elif timer['status'] == 'led_on':
                remaining = max(0, 2 - (elapsed - timer['delay']))
                st.markdown(f"""  
                <div class="active-timer">  
                    <strong>{timer['region']}</strong> - LED ON<br>  
                    <small>Tắt sau: {remaining:.1f}s</small>  
                </div>  
                """, unsafe_allow_html=True)
    else:
        st.info("Không có timer đang chạy")

    # Log Stack - chỉ hiển thị QR mới nhất
st.markdown("### 📜 Log History (Real-time)")
if st.session_state.log_stack:
    recent_logs = st.session_state.log_stack[-8:]
    for log in reversed(recent_logs):
        st.text(log)
else:
    st.info("Chưa có log nào...")

# Auto refresh
time.sleep(0.5)
st.rerun()