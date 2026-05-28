import os
import subprocess
from datetime import datetime, date
from string import Template

GARMIN_EMAIL = "chonkin@gmail.com"
GARMIN_PASSWORD = "N7vbkech"
PROJECT_DIR = os.path.expanduser("~/projects/cyber-test")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")
LOG_FILE = os.path.join(PROJECT_DIR, "activity_log.txt")

WEEKLY_SCHEDULE = {
    # 你的周計劃表
}

def generate_html(avg_hr, max_hr, distance_km):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if distance_km == 0:
        status_text = "🟢 赛博修整 / 重力恢复日"
        data_display = "<p style='color: #a0aec0; font-size:14px; margin-top:10px;'>今日无跑步数据。肌肉正在超量恢复，记得加强下肢力量训练！🏋️‍♂️</p>"
    else:
        status_text = "🏃‍♂️ 实战跑步训练"
        data_display = f"""
            <div class="metrics">
                <div class="card">
                    <h3>最大心率: {avg_hr}</h3>
                    <p>{max_hr} BPM</p>
                </div>
                <div class="card">
                    <h3>跑步距离: {distance_km}</h3>
                    <p>{distance_km:.2f} km</p>
                </div>
            </div>
        """
    
    html_content = HTML_TEMPLATE.substitute(
        current_time=current_time,
        status_text=status_text,
        data_display=data_display
    )
    
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

def push_to_github():
    try:
        os.chdir(PROJECT_DIR)
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"🛰️ Dashboard Updated - {date.today().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        print(f"❌ Git 推送失败: {e}")

if __name__ == "__main__":
    avg_hr, max_hr, distance_km = get_garmin_data()
    generate_html(avg_hr, max_hr, distance_km)
    push_to_github()

    print("🎉 【全线路通车】手机端网页已完美同步！")
