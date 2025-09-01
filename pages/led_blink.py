import streamlit as st
import time
import heapq
from datetime import datetime
from utils.qr_storage import load_qr_data

# Cấu hình trang
st.set_page_config(
    page_title="🚦 LED Controller - Parallel Processing",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS cho LED display
st.markdown("""  
<style>  
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

.priority-item {  
    background: #e8f4fd;  
    padding: 10px;  
    margin: 5px 0;  
    border-radius: 5px;  
    border-left: 4px solid #2196f3;  
}  

.active-timer {  
    background: #fff3e0;  
    padding: 8px;  
    margin: 3px 0;  
    border-radius: 3px;  
    border-left: 3px solid #ff9800;  
}  
</style>  
""", unsafe_allow_html=True)


# Khởi tạo session state
if 'distanceMN' not in st.session_state:
    st.session_state.distanceMN = 750
if 'distanceMT' not in st.session_state:
    st.session_state.distanceMT = 500
if 'distanceMB' not in st.session_state:
    st.session_state.distanceMB = 250
if 'speed_motor' not in st.session_state:
    st.session_state.speed_motor = 2.5

# LED status
if 'led_status' not in st.session_state:
    st.session_state.led_status = {
        "Miền Bắc": False,
        "Miền Trung": False,
        "Miền Nam": False
    }

# Priority Queue cho timing (Min-Heap)
if 'priority_queue' not in st.session_state:
    st.session_state.priority_queue = []

# Active timers cho parallel processing
if 'active_timers' not in st.session_state:
    st.session_state.active_timers = {}

# Log stack
if 'log_stack' not in st.session_state:
    st.session_state.log_stack = []

if 'last_qr_count' not in st.session_state:
    st.session_state.last_qr_count = 0

# Header
st.markdown("""  
<div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);  
            padding: 1.5rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">  
    <h1>🚦 LED CONTROLLER - PARALLEL PROCESSING</h1>  
    <p>Xử lý LED song song theo thời gian thực tế</p>  
</div>  
""", unsafe_allow_html=True)
# --- Kiểm tra đăng nhập ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()
# Input khoảng cách
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    st.session_state.distanceMB = st.number_input(
        "Khoảng cách Miền Bắc (mm)",
        min_value=0, max_value=1000,
        value=st.session_state.distanceMB,
        step=1
    )

with col_input2:
    st.session_state.distanceMT = st.number_input(
        "Khoảng cách Miền Trung (mm)",
        min_value=0, max_value=1000,
        value=st.session_state.distanceMT,
        step=1
    )

with col_input3:
    st.session_state.distanceMN = st.number_input(
        "Khoảng cách Miền Nam (mm)",
        min_value=0, max_value=1000,
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


def process_priority_queue():
    """Xử lý priority queue theo thời gian đến thực tế"""
    current_time = time.time()

    # Xử lý các items đã đến thời gian
    while st.session_state.priority_queue:
        arrival_time, qr_item = st.session_state.priority_queue[0]

        if current_time >= arrival_time:
            # Đã đến thời gian - bật LED
            heapq.heappop(st.session_state.priority_queue)
            region = qr_item['region']

            st.session_state.led_status[region] = True
            add_to_log_stack(f"[PRIORITY LED ON] {region} sáng đúng thời gian!")

            # Tạo timer để tắt LED sau 2s
            timer_id = f"led_off_{region}_{current_time}"
            st.session_state.active_timers[timer_id] = {
                'start_time': current_time,
                'delay': 0,  # Tắt ngay lập tức sau 2s
                'region': region,
                'status': 'led_on',
                'led_on_time': current_time,
                'qr_data': qr_item['data']
            }
        else:
            break

        # Monitor QR data và tạo parallel timers


qr_data = load_qr_data()
if len(qr_data) > st.session_state.last_qr_count:
    # Có QR mới
    new_qr = qr_data[-1]
    region = new_qr.get("region", "")

    if region in distance_map:
        current_time = time.time()
        delay = distance_map[region] / v if v > 0 else 0
        arrival_time = current_time + delay

        # Thêm vào priority queue (sắp xếp theo thời gian đến)
        qr_item = {
            'region': region,
            'data': new_qr.get("data", ""),
            'time': new_qr.get("time", ""),
            'detection_time': current_time
        }
        heapq.heappush(st.session_state.priority_queue, (arrival_time, qr_item))

        add_to_log_stack(f"[NEW QR] {region} - Sẽ đến sau {delay:.1f}s")

    st.session_state.last_qr_count = len(qr_data)

# Xử lý parallel processing
process_parallel_timers()
process_priority_queue()

# Layout chính
col_main1, col_main2 = st.columns([2, 1])

with col_main1:
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

with col_main2:
    # Priority Queue Status
    st.markdown("### ⏰ Priority Queue (Theo thời gian)")
    if st.session_state.priority_queue:
        current_time = time.time()
        sorted_queue = sorted(st.session_state.priority_queue)

        for arrival_time, item in sorted_queue[:5]:  # Hiển thị 5 items đầu
            remaining = max(0, arrival_time - current_time)
            st.markdown(f"""  
            <div class="priority-item">  
                <strong>{item['region']}</strong><br>  
                <small>Còn: {remaining:.1f}s</small>  
            </div>  
            """, unsafe_allow_html=True)
    else:
        st.info("Không có QR đang chờ")

        # Active Timers
    st.markdown("### ⚡ Active Timers")
    if st.session_state.active_timers:
        current_time = time.time()
        for timer_id, timer in st.session_state.active_timers.items():
            elapsed = current_time - timer['start_time']
            if timer['status'] == 'led_on':
                remaining = max(0, 2 - (elapsed - timer['delay']))
                st.markdown(f"""  
                <div class="active-timer">  
                    <strong>{timer['region']}</strong> - LED ON<br>  
                    <small>Tắt sau: {remaining:.1f}s</small>  
                </div>  
                """, unsafe_allow_html=True)
    else:
        st.info("Không có timer đang chạy")

    # System Info
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("### ⚙️ Thông số hệ thống")
    st.metric("Tốc độ băng tải", f"{v:.1f} mm/s")
    st.metric("Tổng QR đã quét", len(qr_data))
    st.metric("Priority Queue", len(st.session_state.priority_queue))

with col_info2:
    st.markdown("### 📊 Delay Times")
    for region, distance in distance_map.items():
        delay = distance / v if v > 0 else 0
        st.metric(region, f"{delay:.1f}s")

    # Log Stack
st.markdown("### 📜 Log History")
if st.session_state.log_stack:
    recent_logs = st.session_state.log_stack[-8:]
    for log in reversed(recent_logs):
        st.text(log)
else:
    st.info("Chưa có log nào...")

# Auto refresh
time.sleep(0.5)
st.rerun()
if st.button("🔒 Đăng xuất", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()