import datetime
import os
import subprocess
from garminconnect import Garmin

# ========================================================
# 🛰️ 賽博大戰艦：內建自定義課表 + Garmin 手機看板（單純流）
# ========================================================

# 1. 填入你真實登入 Garmin Connect App 的電郵和密碼
GARMIN_EMAIL = "chonkin@gmail.com"
GARMIN_PASSWORD = "N7vbkech"

# Token 緩存路徑（避免每次重新登入觸發 429 rate limit）
TOKEN_STORE = os.path.expanduser("~/.garmin_tokens.json")

# 2. 🎖️ 指揮官自訂課表輸入區：直接在這裡修改你的每週訓練計劃！
WEEKLY_SCHEDULE = {
    "星期一": "400m (1'28\") R1'30\" + 200m (90%) R5' x 4-5 速度間歇 🏃‍♂️",
    "星期二": "下肢大髀、臀部重力訓練，加強核心力量 🏋️‍♂️",
    "星期三": "5-8 km 穩定配速節奏跑（嚴格控制心率）",
    "星期四": "40-50分鐘 輕鬆有氧恢復跑",
    "星期五": "拉伸、超量恢復休息日（賽博修整）",
    "星期六": "15-18 km 針對性長距離耐力訓練 (LSD)",
    "星期日": "完全放鬆，陪奶奶過夜與休息 ☕"
}

PROJECT_DIR = os.path.expanduser("~/projects/cyber-test")
LOG_FILE = os.path.join(PROJECT_DIR, "activity_log.txt")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")


def get_garmin_client():
    """
    取得 Garmin client。
    優先使用緩存 token（~/.garmin_tokens.json），避免每次登入觸發 429 rate limit。
    若 token 失效或不存在，才重新密碼登入並保存新 token。
    """
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD, is_cn=False)

    # 嘗試用緩存 token 登入（正確方式：login(tokenstore=路徑)）
    if os.path.exists(TOKEN_STORE):
        print("🔑 找到緩存 token，嘗試免密登入...")
        try:
            client.login(tokenstore=TOKEN_STORE)
            print(f"✅ Token 登入成功（用戶: {client.display_name}）")
            return client
        except Exception as e:
            print(f"⚠️ Token 已失效，改用密碼重新登入: {e}")
            try:
                os.remove(TOKEN_STORE)
            except Exception:
                pass

    # Token 不存在或失效，重新密碼登入
    print("🔐 正在使用密碼登入 Garmin...")
    client.login()

    # 保存新 token 以供下次使用
    try:
        client.client.dump(TOKEN_STORE)
        os.chmod(TOKEN_STORE, 0o600)
        print(f"💾 新 token 已保存至 {TOKEN_STORE}")
    except Exception as e:
        print(f"⚠️ Token 保存失敗（不影響本次運行）: {e}")

    return client


def get_garmin_data():
    print("🛰️ 正在連線至 Garmin 國際雲端伺服器...")
    try:
        client = get_garmin_client()

        today_str = datetime.date.today().isoformat()
        summary = client.get_user_summary(today_str)

        avg_hr = summary.get('averageHeartRate', 0) or 0
        max_hr = summary.get('maxHeartRate', 0) or 0
        distance_m = summary.get('totalDistanceInMeters', 0) or 0
        distance_km = distance_m / 1000

        print(f"🎯 數據抓取成功！距離: {distance_km:.2f} km | 平均心率: {avg_hr} bpm")
        return avg_hr, max_hr, distance_km

    except Exception as e:
        print(f"❌ Garmin 數據獲取失敗: {e}")
        # 若懷疑是 token 問題，刪除緩存讓下次重新登入
        if os.path.exists(TOKEN_STORE) and any(
            kw in str(e).lower() for kw in ["401", "403", "token", "unauthorized", "expired"]
        ):
            try:
                os.remove(TOKEN_STORE)
                print("🗑️ 已刪除失效 token，下次將重新登入")
            except Exception:
                pass
        return 0, 0, 0


def build_schedule_html():
    """將程式內輸入的字典直接轉化為網頁 HTML"""
    html_lines = ""
    for day, content in WEEKLY_SCHEDULE.items():
        html_lines += f'<div class="day"><span class="day-name">{day}：</span>{content}</div>\n'
    return html_lines


def generate_html(avg_hr, max_hr, distance):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schedule_html = build_schedule_html()

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
    print("--- 🏁 啟動程式內建課表流水線 ---")
    avg_hr, max_hr, distance_km = get_garmin_data()
    generate_html(avg_hr, max_hr, distance_km)
    push_to_github()
    print("--- 🏁 流程執行完畢 ---")
