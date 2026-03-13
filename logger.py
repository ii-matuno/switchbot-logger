import hashlib, hmac, base64, time, requests, uuid, csv, os
from datetime import datetime

TOKEN = os.environ["SWITCHBOT_TOKEN"]
SECRET = os.environ["SWITCHBOT_SECRET"]

DEVICES = {
    "防水温湿度計 箱の外 上": "CD3430371046",
    "防水温湿度計 上": "CE2A82C61C3C",
    "防水温湿度計 下": "CE2A86462A49",
}

API = "https://api.switch-bot.com/v1.1"
LOG_FILE = "switchbot_log.csv"

def get_headers():
    t = str(round(time.time() * 1000))
    nonce = str(uuid.uuid4())
    sign = base64.b64encode(
        hmac.new(SECRET.encode(), (TOKEN + t + nonce).encode(), hashlib.sha256).digest()
    ).decode()
    return {"Authorization": TOKEN, "sign": sign, "t": t, "nonce": nonce}

def fetch_status(device_id):
    res = requests.get(f"{API}/devices/{device_id}/status", headers=get_headers())
    return res.json()["body"]

def main():
    # CSVがなければヘッダーを作成
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["datetime", "device", "temperature", "humidity"])
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for name, device_id in DEVICES.items():
            try:
                data = fetch_status(device_id)
                temp = data["temperature"]
                hum = data["humidity"]
                writer.writerow([now, name, temp, hum])
                print(f"{name}: {temp}°C / {hum}%")
            except Exception as e:
                print(f"{name} エラー: {e}")

if __name__ == "__main__":
    main()
