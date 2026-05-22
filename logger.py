import datetime
import os
import subprocess
from garminconnect import Garmin

# ========================================================
# 🛰️ 賽博大戰艦：動態自定義課表 + Garmin 手機看板完全體
# ========================================================

# 1. 填入你真實登入 Garmin Connect App 的電郵和密碼
GARMIN_EMAIL = "chonkin@gmail.com"
GARMIN_PASSWORD = "N7vbkech"

PROJECT_DIR = os.path.expanduser("~/projects/cyber-test")
LOG_FILE = os.path.join(PROJECT_DIR, "activity_log.txt")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")
SCHEDULE_FILE = os.path.join(PROJECT_DIR, "schedule.txt")

def get_garmin_data():
    print("🛰️ 正在連線至 Garmin 國際雲端伺服器...")
    try:
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        
        today_str = datetime.date.today().isoformat()
        summary = client.get_user_summary(today_str)
        
        # 安全提取數據，避免 NoneType 報錯
        avg_hr = summary.get('averageHeartRate', 0) or 0
        max_hr = summary.get('maxHeartRate', 0) or 0
        distance_m = summary.get('totalDistanceInMeters', 0) or 0
        distance_km = distance_m / 1000
        
        print(f"🎯 數據抓取成功！距離: {distance_km:.2f} km | 平均心率: {avg_hr} bpm")
        return avg_hr, max_hr, distance_km
    except Exception as e:
        print(f"⚠️ Garmin 數據未就緒或未跑步 (可忽略): {e}")
        return 0, 0, 0  # 報錯時當作 0 處理，確保後續網頁能正常更新

def load_custom_schedule():
    """讀取用戶自己輸入的課表"""
    html_lines = ""
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():
                    # 切割星期與內容
                    if "：" in line:
                        day, content = line.split("：", 1)
                    elif ":" in line:
                        day, content = line.split(":", 1)
                    else:
                        day, content = "訓練", line
                    html_lines += f'<div class="day"><span class="day-name">{day.strip()}：</span>{content.strip()}</div>\n'
    else:
        html_lines = "<div class='day'>未偵測到 schedule.txt 課表檔案</div>"
    return html_lines

def generate_html(avg_hr, max_hr, distance):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schedule_html = load_custom_schedule()
    
    if distance == 0:
        status_text = "🟢 賽博修整 / 重力恢復日"
        data_display = "<p style='color: #a0aec0; font-size:14px; margin-top:10px;'>今日無跑步數據。肌肉正在超量恢復，記得加強下肢力量訓練！🏋️‍♂️</p>"
    else:
        status_text = "🏃‍♂️ 實戰跑步訓練"
        data_display = f"""
            <div class="metrics">
                <div class="card"><h3>🏃‍♂️ 距離</h3><p>{distance:.2f} <span>km</span></p></div>
                <div class="card"><h3>💓 平均心率</h3><p>{avg_hr} <span>bpm</span></p></div>
                <div class="card"><h3>🔥 最高心率</h3><p>{max_hr} <span>bpm</span></p></div>
            </div>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kenclaw 賽博跑步儀表板</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a202c; color: #fff; padding: 20px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4fd1c5; text-align: center; font-size: 24px; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #718096; font-size: 12px; margin-bottom: 25px; }}
        .status {{ background: #2d3748; padding: 15px; border-radius: 12px; border-left: 5px solid #4fd1c5; margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 15px; }}
        .card {{ background: #1a202c; padding: 10px; border-radius: 8px; text-align: center; }}
        .card h3 {{ margin: 0; font-size: 11px; color: #a0aec0; }}
        .card p {{ margin: 5px 0 0 0; font-size: 20px; font-weight: bold; color: #f6ad55; }}
        .card p span {{ font-size: 11px; color: #a0aec0; }}
        .schedule {{ background: #2d3748; padding: 20px; border-radius: 12px; }}
        .schedule h2 {{ margin-top: 0; font-size: 18px; color: #4fd1c5; border-bottom: 1px solid #4a5568; padding-bottom: 10px; }}
        .day {{ margin-bottom: 12px; font-size: 14px; line-height: 1.5; border-bottom: 1px dashed #3f4e64; padding-bottom: 8px; }}
        .day:last-child {{ border-bottom: none; }}
        .day-name {{ font-weight: bold; color: #63b3ed; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 KENCLAW 賽博大戰艦</h1>
        <div class="subtitle">更新時間: {current_time}</div>
        
        <div class="status">
            <h3 style="margin:0 0 5px 0; font-size:14px; color:#a0aec0;">今日動態</h3>
            <span style="font-size:18px; font-weight:bold;">{status_text}</span>
            {data_display}
        </div>

        <div class="schedule">
            <h2>📅 指揮官自訂跑步課表</h2>
            {schedule_html}
        </div>
    </div>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🎯 手機網頁 Dashboard (index.html) 更新成功！")

def push_to_github():
    print("🐙 正在同步至 GitHub...")
    try:
        os.chdir(PROJECT_DIR)
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"🛰️ Dashboard Updated - {datetime.date.today().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🎉 【全線通車】手機端網頁已完美同步！")
    except Exception as e:
        print(f"❌ Git 推送失敗: {e}")

if __name__ == "__main__":
    print("--- 🏁 啟動強大相容版手機看板流水線 ---")
    avg_hr, max_hr, distance_km = get_garmin_data()
    generate_html(avg_hr, max_hr, distance_km)
    push_to_github()
    print("--- 🏁 流程執行完畢 ---")
