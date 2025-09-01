import json
import os
from datetime import datetime

def get_last_qr():
    """Lấy QR code cuối cùng"""
    data = load_qr_data()
    if data:
        return data[-1]['data']
    return ""

def get_daily_filename(date=None):
    """Tạo filename theo ngày"""
    if date is None:
        date = datetime.now()
    return f"./qr_data_{date.strftime('%Y-%m-%d')}.json"

def save_qr_data(qr_entry):
    """Lưu QR data vào file theo ngày"""
    data_file = get_daily_filename()

    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                data = json.loads(content) if content else []
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(qr_entry)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_qr_data(date=None):
    """Load QR data theo ngày"""
    data_file = get_daily_filename(date)

    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error loading QR data: {e}")
            return []
    return []


def get_available_dates():
    """Lấy danh sách ngày có data"""
    files = [f for f in os.listdir('.') if f.startswith('qr_data_') and f.endswith('.json')]
    dates = []
    for file in files:
        try:
            date_str = file.replace('qr_data_', '').replace('.json', '')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(date_obj)
        except ValueError:
            continue
    return sorted(dates, reverse=True)