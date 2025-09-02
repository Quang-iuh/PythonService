import streamlit as st
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import pandas as pd
from Component.Camera.CameraHeader import load_css
# --- Cấu hình trang ---
st.set_page_config(
    page_title="⚙️ Cài đặt hệ thống",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_css("SettingStyle.css")

# --- CSS tùy chỉnh ---
# PLC Manager Class với Modbus TCP
class PLCManager:
    def __init__(self):
        self.client = None
        self.connected = False
        self.ip = None
        self.port = 502

    def connect(self, ip, port=502):
        """Kết nối đến PLC qua Modbus TCP"""
        try:
            self.ip = ip
            self.port = port
            self.client = ModbusTcpClient(ip, port)
            self.connected = self.client.connect()

            if self.connected:
                return True, "Kết nối PLC thành công"
            else:
                return False, "Không thể kết nối đến PLC"
        except Exception as e:
            self.connected = False
            return False, f"Lỗi kết nối: {str(e)}"

    def disconnect(self):
        """Ngắt kết nối PLC"""
        if self.client and self.connected:
            self.client.close()
            self.connected = False

    def read_motor_speed(self, address=0, unit=1):
        """Đọc tốc độ động cơ từ PLC (Holding Register)"""
        if not self.connected:
            return None

        try:
            # Đọc 2 registers để lấy float value (32-bit)
            result = self.client.read_holding_registers(address, 2, unit=unit)
            if result.isError():
                st.error(f"Lỗi đọc PLC: {result}")
                return None

                # Convert 2 registers to float (IEEE 754)
            registers = result.registers
            speed = self._registers_to_float(registers[0], registers[1])
            return speed

        except ModbusException as e:
            st.error(f"Lỗi Modbus: {e}")
            return None
        except Exception as e:
            st.error(f"Lỗi đọc dữ liệu PLC: {e}")
            return None

    def write_motor_speed(self, speed, address=0, unit=1):
        """Ghi tốc độ động cơ vào PLC (Holding Register)"""
        if not self.connected:
            return False

        try:
            # Convert float to 2 registers (IEEE 754)
            reg1, reg2 = self._float_to_registers(speed)

            # Ghi 2 registers
            result = self.client.write_registers(address, [reg1, reg2], unit=unit)
            if result.isError():
                st.error(f"Lỗi ghi PLC: {result}")
                return False

            return True

        except ModbusException as e:
            st.error(f"Lỗi Modbus: {e}")
            return False
        except Exception as e:
            st.error(f"Lỗi ghi dữ liệu PLC: {e}")
            return False

    def read_digital_input(self, address, unit=1):
        """Đọc digital input từ PLC"""
        if not self.connected:
            return None

        try:
            result = self.client.read_discrete_inputs(address, 1, unit=unit)
            if result.isError():
                return None
            return result.bits[0]
        except Exception as e:
            st.error(f"Lỗi đọc digital input: {e}")
            return None

    def write_digital_output(self, address, value, unit=1):
        """Ghi digital output vào PLC"""
        if not self.connected:
            return False

        try:
            result = self.client.write_coil(address, value, unit=unit)
            return not result.isError()
        except Exception as e:
            st.error(f"Lỗi ghi digital output: {e}")
            return False

    def get_connection_status(self):
        """Kiểm tra trạng thái kết nối"""
        return {
            "connected": self.connected,
            "ip": self.ip,
            "port": self.port
        }

    def _float_to_registers(self, value):
        """Convert float to 2 Modbus registers (IEEE 754)"""
        import struct
        # Pack float as big-endian IEEE 754
        packed = struct.pack('>f', value)
        # Unpack as 2 16-bit integers
        reg1, reg2 = struct.unpack('>HH', packed)
        return reg1, reg2

    def _registers_to_float(self, reg1, reg2):
        """Convert 2 Modbus registers to float (IEEE 754)"""
        import struct
        # Pack 2 16-bit integers
        packed = struct.pack('>HH', reg1, reg2)
        # Unpack as big-endian float
        value = struct.unpack('>f', packed)[0]
        return value

    # --- Header chính ---


st.markdown("""    
<div class="main-header">    
    <h1>⚙️ CÀI ĐẶT HỆ THỐNG</h1>    
    <p>Điều chỉnh thông số và cấu hình ứng dụng</p>    
</div>    
""", unsafe_allow_html=True)

# --- Kiểm tra đăng nhập ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# --- Khởi tạo session state ---
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
    st.session_state.plc_ip = "192.168.1.100"
if 'plc_port' not in st.session_state:
    st.session_state.plc_port = 502
if 'plc_unit_id' not in st.session_state:
    st.session_state.plc_unit_id = 1

# --- Layout 2 cột ---
col1, col2 = st.columns([1, 1])

with col1:
    # --- Cài đặt Camera ---
    st.markdown("""    
    <div class="setting-card">    
        <h3 class="setting-title">📹 Cài đặt Camera</h3>    
    </div>    
    """, unsafe_allow_html=True)

    # Grayscale
    st.session_state.grayscale = st.checkbox(
        "🎨 Bật chế độ Grayscale",
        value=st.session_state.grayscale,
        help="Chuyển đổi hình ảnh sang màu xám"
    )

    # Zoom level
    st.markdown("**🔍 Điều chỉnh độ phóng đại**")
    st.session_state.zoom_level = st.slider(
        "Mức phóng đại camera:",
        min_value=1.0,
        max_value=3.0,
        value=st.session_state.zoom_level,
        step=0.1,
        help="1.0 = Zoom mặc định, giá trị lớn hơn sẽ phóng to hình ảnh"
    )

    # Resolution
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
    # --- Cài đặt Động cơ ---
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

    # --- Cài đặt PLC ---
    st.markdown("""    
    <div class="setting-card">    
        <h3 class="setting-title">🔌 Kết nối PLC Modbus</h3>    
    </div>    
    """, unsafe_allow_html=True)

    # PLC Connection Settings
    st.markdown("**🌐 Thông số kết nối**")

    col_ip, col_port = st.columns([2, 1])
    with col_ip:
        st.session_state.plc_ip = st.text_input(
            "Địa chỉ IP PLC:",
            value=st.session_state.plc_ip,
            help="Nhập địa chỉ IP của PLC"
        )

    with col_port:
        st.session_state.plc_port = st.number_input(
            "Port:",
            min_value=1,
            max_value=65535,
            value=st.session_state.plc_port
        )

    st.session_state.plc_unit_id = st.number_input(
        "Unit ID:",
        min_value=1,
        max_value=255,
        value=st.session_state.plc_unit_id,
        help="Modbus Unit ID (thường là 1)"
    )

    # Connection Controls
    col_connect, col_disconnect = st.columns(2)

    with col_connect:
        if st.button("🔗 Kết nối PLC", use_container_width=True):
            if 'plc_manager' not in st.session_state:
                st.session_state.plc_manager = PLCManager()

            success, message = st.session_state.plc_manager.connect(
                st.session_state.plc_ip,
                st.session_state.plc_port
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

                # Status và Controls
    if st.session_state.plc_connected:
        st.success("🟢 PLC đã kết nối")

        col_sync, col_test = st.columns(2)

        with col_sync:
            if st.button("🔄 Đồng bộ tốc độ"):
                if st.button("🔄 Reset về mặc định", use_container_width=True):
                    st.session_state.grayscale = False
                    st.session_state.zoom_level = 1.0
                    st.session_state.resolution = (640, 480)
                    st.session_state.speed_motor = 2.5
                    st.session_state.plc_connected = False
                    st.session_state.plc_ip = "192.168.1.100"
                    st.session_state.plc_port = 502
                    st.session_state.plc_unit_id = 1
                    st.success("Đã reset về cài đặt mặc định!")
                    st.rerun()

                if st.button("🔒 Đăng xuất", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.rerun()
