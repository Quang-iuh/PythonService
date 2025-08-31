import os


class Config:
    CAMERA_SERVER_URL = os.getenv('CAMERA_SERVER_URL', 'http://192.168.1.11:8000')

    @classmethod
    def get_camera_start_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/camera/start"

    @classmethod
    def get_camera_stop_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/camera/stop"

    @classmethod
    def get_camera_stream_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/camera/stream"

    @classmethod
    def get_camera_frame_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/camera/frame"

    @classmethod
    def get_camera_status_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/camera/status"

    @classmethod
    def get_health_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/health"