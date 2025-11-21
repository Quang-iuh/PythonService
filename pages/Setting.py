import streamlit as st
import snap7
import struct

from Component.Camera.CameraHeader import load_css


# Cấu hình trang


st.set_page_config(
    page_title="⚙️ Cài đặt hệ thống",
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
            return True, "Kết nối PLC S7 thành công"
        except Exception as e:
            self.connected = False
            return False, f"Lỗi kết nối với PLC: {str(e)}"
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
    <p></p>      
</div>      
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("🔒 Vui lòng đăng nhập trước khi truy cập trang này.")
    st.stop()

# Khởi tạo session state
if "resolution" not in st.session_state:
    st.session_state.resolution = (1280, 720)
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 1.0
if 'speed_motor' not in st.session_state:
    st.session_state.speed_motor = 2.5
if 'camera_fps' not in st.session_state:
    st.session_state.camera_fps = 30  # Default 30 FPS

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

    # FPS Selector
    st.markdown("**🎬 Số khung hình trên giây (FPS)**")
    fps_options = {
        "15 FPS ": 15,
        "30 FPS ": 30,
        "60 FPS ": 60
    }

    current_fps_label = f"{st.session_state.camera_fps} FPS"
    for key, value in fps_options.items():
        if value == st.session_state.camera_fps:
            current_fps_label = key
            break

    selected_fps = st.selectbox(
        "Chọn FPS:",
        list(fps_options.keys()),
        index=list(fps_options.keys()).index(current_fps_label) if current_fps_label in fps_options.keys() else 1
    )
    st.session_state.camera_fps = fps_options[selected_fps]

    # Resolution selector (existing code)
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
    # Cài đặt PLC Snap7
    st.markdown("""      
    <div class="setting-card">      
        <h3 class="setting-title">🔌 Kết nối PLC</h3>      
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
        if st.button("🔗 Kết nối PLC", use_container_width=True,type=("primary")):
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
        if st.button("Test Connection"):
            if 'plc_manager' in st.session_state:
                success = st.session_state.plc_manager.write_db(14, 0, 2)
                if success:
                    st.success("✅ Connection successful!")
                    st.switch_page("pages/PLC.py")
                else:
                    st.error("❌Error to connect")
    else:
        st.error("🔴 PLC chưa kết nối")

    # Reset button
if st.button("🔄 Reset về mặc định", use_container_width=True):
    st.session_state.resolution = (1280, 720)
    st.session_state.camera_fps = 30  # Reset FPS về 30
    st.session_state.plc_connected = False
    st.session_state.plc_ip = "192.168.0.1"
    st.session_state.plc_rack = 0
    st.session_state.plc_slot = 1
    st.session_state.FPS=24
    st.success("Đã reset về cài đặt mặc định!")
    st.rerun()

col1_b, col2_b, col3_b = st.columns([1, 1, 1])
with col1_b:
    if st.button("Home", use_container_width=True):
        st.switch_page("Home.py")
with col2_b:
    if st.button("Camera", use_container_width=True):
        st.switch_page("pages/camera.py")
with col3_b:
    if st.button("Thống kê", use_container_width=True):
        st.switch_page("pages/Dashboard.py")




# Sidebar
with st.sidebar:
    st.markdown(f"""  
    <div class="sidebar-section">  
        <h3>👤 Người dùng</h3>  
        <p>Xin chào, <strong>{st.session_state.get('username', 'User')}</strong></p>  
    </div>  
    """, unsafe_allow_html=True)
    im_co1, im_co2 = st.columns(2)
    with im_co1:
        st.image("image/images2.jfif", width=80)
    with im_co2:
        st.image("image/images.png", width=80)

    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("pages/Login.py")