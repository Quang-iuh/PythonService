import streamlit as st
import snap7
import struct
import time
import socket
from Component.Camera.CameraHeader import load_css
from pages.Dashboard import qr_history, total_scans, unique_scans, unique_north, unique_central, unique_south

# Cấu hình trang
st.set_page_config(
    page_title="⚙️ Cài đặt hệ thống",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_css("SettingStyle.css")


class Snap7Exception:
    pass


class PLCManager:
    def __init__(self):
        self.client = None
        self.connected = False
        self.ip = None
        self.rack = 0
        self.slot = 1

    def connect(self, ip, rack=0, slot=1):
        """Kết nối đến PLC qua Snap7"""
        try:
            # Khởi tạo Snap7 client trước khi connect
            self.client = snap7.client.Client()

            # Snap7 connection code
            self.client.connect(ip, rack, slot)
            self.connected = True
            return True, "Kết nối S7 PLC thành công"
        except Exception as e:
            self.connected = False
            return False, f"Lỗi kết nối S7: {str(e)}"
        except Snap7Exception as e:
            self.connected = False
            return False, f"Lỗi Snap7: {str(e)}"
        except Exception as e:
            self.connected = False
            return False, f"Lỗi kết nối: {str(e)}"

    def disconnect(self):
        """Ngắt kết nối PLC"""
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
            except:
                pass

    def write_db(self, db_number, start_offset, data):
        """Ghi data vào Data Block của PLC"""
        if not self.connected:
            return False

        try:
            if isinstance(data, int):
                # Convert int to bytearray
                data = struct.pack('>H', data)  # Big-endian 16-bit
            elif isinstance(data, list):
                # Convert list of ints to bytearray
                data = bytearray()
                for val in data:
                    data.extend(struct.pack('>H', val))

            self.client.db_write(db_number, start_offset, data)
            return True
        except Exception as e:
            st.error(f"Lỗi ghi DB{db_number}: {str(e)}")
            return False

    def read_db(self, db_number, start_offset, size):
        """Đọc data từ Data Block của PLC"""
        if not self.connected:
            return None

        try:
            data = self.client.db_read(db_number, start_offset, size)
            return data
        except Exception as e:
            st.error(f"Lỗi đọc DB{db_number}: {str(e)}")
            return None

    def write_db4_status(self, status_value):
        """Ghi trạng thái CB2 vào DB4"""
        if not self.connected:
            return False

        try:
            # Đảm bảo data format đúng cho Sint
            data = struct.pack('>h', int(status_value))  # Signed 16-bit
            self.client.db_write(4, 0, data)
            return True
        except Exception as e:
            st.error(f"Lỗi ghi DB4: {str(e)}")
            return False


    def get_connection_status(self):
        """Kiểm tra trạng thái kết nối"""
        return {
            "connected": self.connected,
            "ip": self.ip,
            "rack": self.rack,
            "slot": self.slot
        }
    # Header chính


st.markdown("""      
<div class="main-header">      
    <h1>⚙️ CÀI ĐẶT HỆ THỐNG</h1>      
    <p>Điều chỉnh thông số và cấu hình ứng dụng</p>      
</div>      
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Khởi tạo session state
if "grayscale" not in st.session_state:
    st.session_state.grayscale = False
if "resolution" not in st.session_state:
    st.session_state.resolution = (640, 480)
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 1.0
if 'speed_motor' not in st.session_state:
    st.session_state.speed_motor = 2.5

# PLC session state
if 'plc_connected' not in st.session_state:
    st.session_state.plc_connected = False
if 'plc_ip' not in st.session_state:
    st.session_state.plc_ip = "192.168.0.1"
if 'plc_rack' not in st.session_state:
    st.session_state.plc_rack = 0
if 'plc_slot' not in st.session_state:
    st.session_state.plc_slot = 1

# Layout 2 cột
col1, col2 = st.columns([1, 1])

with col1:
    # Cài đặt Camera
    st.markdown("""      
    <div class="setting-card">      
        <h3 class="setting-title">📹 Cài đặt Camera</h3>      
    </div>      
    """, unsafe_allow_html=True)

    st.session_state.grayscale = st.checkbox(
        "🎨 Bật chế độ Grayscale",
        value=st.session_state.grayscale,
        help="Chuyển đổi hình ảnh sang màu xám"
    )

    st.markdown("**🔍 Điều chỉnh độ phóng đại**")
    st.session_state.zoom_level = st.slider(
        "Mức phóng đại camera:",
        min_value=1.0,
        max_value=3.0,
        value=st.session_state.zoom_level,
        step=0.1,
        help="1.0 = Zoom mặc định, giá trị lớn hơn sẽ phóng to hình ảnh"
    )

    st.markdown("**📐 Độ phân giải**")
    resolution_options = {
        "640x480 (SD)": (640, 480),
        "1280x720 (HD)": (1280, 720),
        "1920x1080 (Full HD)": (1920, 1080)
    }

    current_res = f"{st.session_state.resolution[0]}x{st.session_state.resolution[1]}"
    for key, value in resolution_options.items():
        if value == st.session_state.resolution:
            current_res = key
            break

    selected_res = st.selectbox(
        "Chọn độ phân giải:",
        list(resolution_options.keys()),
        index=list(resolution_options.keys()).index(current_res) if current_res in resolution_options.keys() else 0
    )
    st.session_state.resolution = resolution_options[selected_res]

with col2:
    # Cài đặt Động cơ
    st.markdown("""      
    <div class="setting-card">      
        <h3 class="setting-title">⚡ Cài đặt Động cơ</h3>      
    </div>      
    """, unsafe_allow_html=True)

    st.markdown("**🚀 Tốc độ động cơ**")
    st.session_state.speed_motor = st.slider(
        "Tốc độ (m/phút):",
        min_value=2.5,
        max_value=5.0,
        value=st.session_state.speed_motor,
        step=0.1,
        help="Điều chỉnh tốc độ hoạt động của động cơ"
    )

    # Cài đặt PLC Snap7
    st.markdown("""      
    <div class="setting-card">      
        <h3 class="setting-title">🔌 Kết nối PLC Snap7</h3>      
    </div>      
    """, unsafe_allow_html=True)

    st.markdown("**🌐 Thông số kết nối S7**")

    col_ip, col_rack, col_slot = st.columns([2, 1, 1])
    with col_ip:
        st.session_state.plc_ip = st.text_input(
            "Địa chỉ IP PLC:",
            value=st.session_state.plc_ip,
            help="Nhập địa chỉ IP của PLC"
        )

    with col_rack:
        st.session_state.plc_rack = st.number_input(
            "Rack:",
            min_value=0,
            max_value=7,
            value=st.session_state.plc_rack
        )

    with col_slot:
        st.session_state.plc_slot = st.number_input(
            "Slot:",
            min_value=0,
            max_value=31,
            value=st.session_state.plc_slot
        )

        # Connection Controls
    col_connect, col_disconnect = st.columns(2)

    with col_connect:
        if st.button("🔗 Kết nối PLC", use_container_width=True):
            if 'plc_manager' not in st.session_state:
                st.session_state.plc_manager = PLCManager()

            success, message = st.session_state.plc_manager.connect(
                st.session_state.plc_ip,
                st.session_state.plc_rack,
                st.session_state.plc_slot
            )

            if success:
                st.session_state.plc_connected = True
                st.success(message)
            else:
                st.session_state.plc_connected = False
                st.error(message)

    with col_disconnect:
        if st.button("❌ Ngắt kết nối", use_container_width=True):
            if 'plc_manager' in st.session_state:
                st.session_state.plc_manager.disconnect()
                st.session_state.plc_connected = False
                st.warning("Đã ngắt kết nối PLC")

                # Status Display
    if st.session_state.plc_connected:
        st.success("🟢 PLC đã kết nối (Snap7 S7 Protocol)")

        # Test DB Write
        if st.button("🧪 Test ghi DB1"):
            if 'plc_manager' in st.session_state:
                success = st.session_state.plc_manager.write_db(1, 0, 123)
                if success:
                    st.success("✅ Ghi DB1 thành công!")
                else:
                    st.error("❌ Lỗi ghi DB1")
    else:
        st.error("🔴 PLC chưa kết nối")

    # Reset button
if st.button("🔄 Reset về mặc định", use_container_width=True):
    st.session_state.grayscale = False
    st.session_state.zoom_level = 1.0
    st.session_state.resolution = (640, 480)
    st.session_state.speed_motor = 2.5
    st.session_state.plc_connected = False
    st.session_state.plc_ip = "192.168.0.1"
    st.session_state.plc_rack = 0
    st.session_state.plc_slot = 1
    st.success("Đã reset về cài đặt mặc định!")
    st.rerun()

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

    if qr_history:
        st.metric("Tổng quét", total_scans)
        st.metric("Mã duy nhất", unique_scans)

        if total_scans > 0:
            north_pct = round(len(unique_north) / unique_scans * 100, 1) if unique_scans > 0 else 0
            central_pct = round(len(unique_central) / unique_scans * 100, 1) if unique_scans > 0 else 0
            south_pct = round(len(unique_south) / unique_scans * 100, 1) if unique_scans > 0 else 0

            st.write("**Tỷ lệ theo miền:**")
            st.write(f"🔵 Miền Bắc: {north_pct}%")
            st.write(f"🟡 Miền Trung: {central_pct}%")
            st.write(f"🔴 Miền Nam: {south_pct}%")

    st.markdown("---")

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/login.py")