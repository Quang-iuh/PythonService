import os


class Config:
    CAMERA_SERVER_URL = os.getenv('CAMERA_SERVER_URL', 'https://70059b6f137f.ngrok-free.app')

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