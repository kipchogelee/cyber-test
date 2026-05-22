import datetime
import os
import subprocess
from garminconnect import Garmin

# ========================================================
# 🛰️ 賽博大戰艦：Garmin 真數據自動化流水線
# ========================================================

# 1. 填入你真實登入 Garmin Connect App 的電郵和密碼
GARMIN_EMAIL = "chonkin@gmail.com"
GARMIN_PASSWORD = "N7vbkech"

LOG_FILE = "activity_log.txt"

def get_garmin_data():
    print("🛰️ 正在連線至 Garmin 國際雲端伺服器...")
    try:
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        
        today_str = datetime.date.today().isoformat()
        summary = client.get_user_summary(today_str)
        
        avg_hr = summary.get('averageHeartRate', 0)
        max_hr = summary.get('maxHeartRate', 0)
        distance_cm = summary.get('totalDistanceInMeters', 0) * 100 
        distance_km = (distance_cm / 100000) if distance_cm > 0 else 0
        
        print(f"🎯 成功抓取今日 Garmin 數據！平均心率: {avg_hr} | 最高心率: {max_hr} | 距離: {distance_km:.2f} km")
        return avg_hr, max_hr, distance_km
    except Exception as e:
        print(f"❌ Garmin 登入或抓取翻車: {e}")
        return None

def log_activity(avg_hr, max_hr, distance):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if distance == 0:
        log_entry = f"[{current_time}] - 🏃‍♂️ 狀態: 賽博修整休息日 | 保持充沛體能\n"
    else:
        log_entry = f"[{current_time}] - 🏃‍♂️ 類型: 實戰跑步訓練 | 距離: {distance:.2f} km | 平均心率: {avg_hr} bpm | 最高心率: {max_hr} bpm\n"
        
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"✅ 真實運動數據已成功寫入 {LOG_FILE}")
    except Exception as e:
        print(f"❌ 寫入日誌發生錯誤: {e}")

def push_to_github():
    print("🐙 正在啟動 Git 自動化流水線...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"feat: 🛰️ Garmin 真數據自動無感上傳 - {datetime.date.today().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🎉 【GitHub 全線通車】Garmin 跑步數據已經安全備份上雲端！")
    except Exception as e:
        print(f"❌ Git 上傳失敗: {e}")

if __name__ == "__main__":
    print("--- 🏁 賽博大戰艦：Garmin 自動化流水線啟動 ---")
    data = get_garmin_data()
    if data:
        avg_hr, max_hr, distance_km = data
        log_activity(avg_hr, max_hr, distance_km)
        push_to_github()
    print("--- 🏁 流程執行完畢 ---")
