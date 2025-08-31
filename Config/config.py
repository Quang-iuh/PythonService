import os


class Config:
    CAMERA_SERVER_URL = os.getenv('CAMERA_SERVER_URL', 'http://192.168.1.6:8080')

    @classmethod
    def get_camera_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/video_feed"

    @classmethod
    def get_api_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/api/qr_data"

    @classmethod
    def get_last_qr_url(cls):
        return f"{cls.CAMERA_SERVER_URL}/api/last_qr"