import json
import os


def save_qr_data(qr_entry):
    data_file = "./qr_data.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(qr_entry)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_qr_data():
    data_file = "./qr_data.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_last_qr():
    data = load_qr_data()
    if data:
        return data[-1]['data']
    return ""