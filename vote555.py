import streamlit as st
import time
import os
import json

# ==================== 【松山高中學生議會設定區：手動打死名冊與代碼】 ====================
TOKEN_MAP = {
    # 高一 (101~120)
    "SS101": "101 班代", "SS102": "102 班代", "SS103": "103 班代", "SS104": "104 班代", "SS105": "105 班代",
    "SS106": "106 班代", "SS107": "107 班代", "SS108": "108 班代", "SS109": "109 班代", "SS110": "110 班代",
    "SS111": "111 班代", "SS112": "112 班代", "SS113": "113 班代", "SS114": "114 班代", "SS115": "115 班代",
    "SS116": "116 班代", "SS117": "117 班代", "SS118": "118 班代", "SS119": "119 班代", "SS120": "120 班代",
    
    # 高二 (201~220)
    "SS201": "201 班代", "SS202": "202 班代", "SS203": "203 班代", "SS204": "204 班代", "SS205": "205 班代",
    "SS206": "206 班代", "SS207": "207 班代", "SS208": "208 班代", "SS209": "209 班代", "SS210": "210 班代",
    "SS211": "211 班代", "SS212": "212 班代", "SS213": "213 班代", "SS214": "214 班代", "SS215": "215 班代",
    "SS216": "216 班代", "SS217": "217 班代", "SS218": "218 班代", "SS219": "219 班代", "SS220": "220 班代",
    
    # 高三 (301~320)
    "SS301": "301 班代", "SS302": "302 班代", "SS303": "303 班代", "SS304": "304 班代", "SS305": "305 班代",
    "SS306": "306 班代", "SS307": "307 班代", "SS308": "308 班代", "SS309": "309 班代", "SS310": "310 班代",
    "SS311": "311 班代", "SS312": "312 班代", "SS313": "313 班代", "SS314": "314 班代", "SS315": "315 班代",
    "SS316": "316 班代", "SS317": "317 班代", "SS318": "318 班代", "SS319": "319 班代", "SS320": "320 班代"
}

CHAIRMAN_IDENTITY = "203 班代"  # 👈 輸入 SS203 直接登入變身主席！
# ====================================================================

REPRESENTATIVES = list(TOKEN_MAP.values())
STATUS_FILE = "status.txt"
VOTE_FILE = "votes.txt"
TITLE_FILE = "title.txt"
HISTORY_FILE = "history_votes.json"  # 💾 儲存歷史紀錄的 JSON 檔案
TIMER_FILE = "timer.txt"  # ⏱️ 儲存截止時間戳的檔案

# --- 基礎資料存取函數 ---
def get_voting_active():
    if not os.path.exists(STATUS_FILE): return False
    # 檢查是否因時間到而自動過期
    if os.path.exists(TIMER_FILE):
        try:
            with open(TIMER_FILE, "r") as f:
                end_time = float(f.read().strip())
            if time.time() >= end_time:
                set_voting_active(False)
                if os.path.exists(TIMER_FILE): os.remove(TIMER_FILE)
                return False
        except:
            pass
    with open(STATUS_FILE, "r") as f: return f.read().strip() == "active"

def set_voting_active(active, duration_minutes=0):
    with open(STATUS_FILE, "w") as f: f.write("active" if active else "stop")
    if active and duration_minutes > 0:
        end_time = time.time() + (duration_minutes * 60)
        with open(TIMER_FILE, "w") as f: f.write(str(end_time))
    else:
        if os.path.exists(TIMER_FILE): os.remove(TIMER_FILE)

def get_remaining_time():
    if not os.path.exists(TIMER_FILE): return 0
    try:
        with open(TIMER_FILE, "r") as f:
            end_time = float(f.read().strip())
        remaining = int(end_time - time.time())
        return remaining if remaining > 0 else 0
    except:
        return 0

def get_meeting_title():
    if not os.path.exists(TITLE_FILE): return "歡迎蒞臨松山高中學生议會大會"
    with open(TITLE_FILE, "r", encoding="utf-8") as f: return f.read().strip()

def set_meeting_title(title):
    with open(TITLE_FILE, "w", encoding="utf-8") as f: f.write(title)

def get_all_votes():
    votes = {}
    if os.path.exists(VOTE_FILE):
        with open(VOTE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "," in line:
                    rep, b = line.strip().split(",")
                    votes[rep] = b
    return votes

def save_vote(rep, ballot):
    votes = get_all_votes()
    votes[rep] = ballot
    with open(VOTE_FILE, "w", encoding="utf-8") as f:
        for r, b in votes.items(): f.write(f"{r},{b}\n")

def clear_all_votes():
    if os.path.exists(VOTE_FILE): os.remove(VOTE_FILE)

# --- 📜 歷史投票紀錄存取函數 ---
def get_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except:
        return []

def save_to_history(title, votes):
    history = get_history()
    total_yes = list(votes.values()).count("贊成")
    total_no = list(votes.values()).count("反對")
    total_abstain = list(votes.values()).count("棄權")
    
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "title": title,
        "summary": f"贊成 {total_yes} | 反對 {total_no} | 棄權 {total_abstain}",
        "details": votes
    }
    history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def delete_history_item(index):
    history = get_history()
    if 0 <= index < len(history):
        history.pop(index)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

# ==================== Streamlit 介面渲染 ====================
st.set_page_config(layout="wide")

voting_active = get_voting_active()
current_votes = get_all_votes()
meeting_title = get_meeting_title()

# 頂部大標題與當前議題
st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>🏛️ 臺北市立松山高級中學學生議會</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; background-color: #F0F2F6; padding: 10px; border-radius: 5px; color: #333333;'>📌 當前議題：{meeting_title}</h2>", unsafe_allow_html=True)

# ⏱️ 局部動態倒數計時區（使用 Fragment 避免整個網頁被重整卡死）
@st.fragment(run_every=1)
def render_timer():
    if get_voting_active():
        rem = get_remaining_time()
        if rem > 0:
            mins, secs = divmod(rem, 60)
            st.markdown(f"<h3 style='text-align: center; color: #dc3545; background-color: #f8d7da; padding: 5px; border-radius: 5px;'>⏳ 投票倒數計時：{mins:02d} 分 {secs:02d} 秒 (時間到自動截止)</h3>", unsafe_allow_html=True)
        else:
            if os.path.exists(TIMER_FILE):
                st.rerun()

render_timer()

user_token = st.text_input("🔑 請輸入你的 5 位數專屬投票驗證碼：", type="password").strip()

if user_token in TOKEN_MAP:
    my_identity = TOKEN_MAP[user_token]
    
    # 👑【主席控制台介面】👑
    if my_identity == CHAIRMAN_IDENTITY:
        st.success(f"👑 歡迎主席（{CHAIRMAN_IDENTITY}）登入中央控制台！")
        
        new_title = st.text_input("✍️ 請輸入本次表決的法案/動議標題：", value=meeting_title)
        if new_title != meeting_title:
            set_meeting_title(new_title)
            st.rerun()
        
        # ⏱️ 計時器設定
        duration = st.number_input("⏱️ 設定投票限時（分鐘，輸入 0 代表不限時）：", min_value=0, max_value=60, value=0, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 開啟現場即時表決 (全場手機亮燈)", use_container_width=True):
                set_voting_active(True, duration_minutes=duration)
                clear_all_votes()
                st.rerun()
        with col2:
            if st.button("🔴 截止投票並存入歷史紀錄 (準備下一動議)", use_container_width=True):
                if voting_active and current_votes:
                    save_to_history(meeting_title, current_votes)  # 💾 截止時自動存入歷史
                set_voting_active(False)
                st.rerun()
                
        status = "📢 【表決中】請代表們開始按鍵..." if voting_active else "🛑 【截止】等待主席發動議"
        st.subheader(status)
        
        # 主席兼代表表決區
        if voting_active:
            st.write(f"### 🗳️ 主席兼代表表決")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 投 贊成", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "贊成")
                    st.rerun()
            with c2:
                if st.button("🟥 投 反對", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "反對")
                    st.rerun()
            with c3:
                if st.button("🟨 投 棄權", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "棄權")
                    st.rerun()

        st.divider()
        st.write("### 📊 代表表決看板 (正宗立法院邊框亮燈風格)")
        
        cols = st.columns(5)
        for idx, rep in enumerate(REPRESENTATIVES):
            with cols[idx % 5]:
                voted_ballot = current_votes.get(rep, "未投")
                if voted_ballot == "贊成":
                    st.markdown(f"<div style='border: 3px solid #28a745; padding:8px; border-radius:5px; text-align:center; color:#28a745; font-weight:bold; margin-bottom:5px;'>🟩 {rep}</div>", unsafe_allow_html=True)
                elif voted_ballot == "反對":
                    st.markdown(f"<div style='border: 3px solid #dc3545; padding:8px; border-radius:5px; text-align:center; color:#dc3545; font-weight:bold; margin-bottom:5px;'>🟥 {rep}</div>", unsafe_allow_html=True)
                elif voted_ballot == "棄權":
                    st.markdown(f"<div style='border: 3px solid #ffc107; padding:8px; border-radius:5px; text-align:center; color:#ffc107; font-weight:bold; margin-bottom:5px;'>🟨 {rep}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='border: 1px solid #CCCCCC; padding:8px; border-radius:5px; text-align:center; color:#888888; margin-bottom:5px;'>{rep}</div>", unsafe_allow_html=True)

        total_yes = list(current_votes.values()).count("贊成")
        total_no = list(current_votes.values()).count("反對")
        total_abstain = list(current_votes.values()).count("棄權")
        
        st.divider()
