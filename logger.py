import datetime
import os

LOG_FILE = "activity_log.txt"

def log_activity(description: str, value: float):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] - 類型: {description} | 值: {value:.2f}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"✅ 日誌紀錄成功：{description} 已經寫入 {LOG_FILE}")
    except Exception as e:
        print(f"❌ 寫入日誌發生錯誤：{e}")

if __name__ == "__main__":
    print("--- 🏃‍♂️ 執行本地日誌紀錄程序開始 ---")
    log_activity("跑步訓練-心率", 145.5) 
    log_activity("活動強度-平均心率", 110.2) 
    print("--- 🏁 日誌紀錄程序執行結束 ---")
