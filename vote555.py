import streamlit as st
import time
import os

# 💡 自動安裝或引入自動重新整理套件（確保跳秒正常運作）
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    os.system("pip install streamlit-autorefresh")
    from streamlit_autorefresh import st_autorefresh

# ==================== 【手動打死名冊與代碼】 ====================
TOKEN_MAP = {}
for i in range(101, 121): TOKEN_MAP[f"SS{i}"] = f"{i} 班代"
for i in range(201, 220): TOKEN_MAP[f"SS{i}"] = f"{i} 班代"  # 跳過220因203為主席
TOKEN_MAP["SS220"] = "220 班代"
for i in range(301, 321): TOKEN_MAP[f"SS{i}"] = f"{i} 班代"

CHAIRMAN_IDENTITY = "203 班代"  # 主主席登入代碼 SS203
TOKEN_MAP["SS203"] = CHAIRMAN_IDENTITY
# ====================================================================

REPRESENTATIVES = list(TOKEN_MAP.values())
STATUS_FILE, VOTE_FILE, TITLE_FILE = "status.txt", "votes.txt", "title.txt"

def get_voting_status():
    if not os.path.exists(STATUS_FILE): return "stop", 0.0
    with open(STATUS_FILE, "r") as f:
        c = f.read().strip().split(",")
        status, end_time = c[0], float(c[1]) if len(c) > 1 else 0.0
        if status == "active" and time.time() > end_time:
            set_voting_status("stop", 0.0)
            return "stop", 0.0
        return status, end_time

def set_voting_status(status, end_time=0.0):
    with open(STATUS_FILE, "w") as f: f.write(f"{status},{end_time}")

def get_meeting_title():
    if not os.path.exists(TITLE_FILE): return "歡迎蒞臨松山高中學生議會大會"
    with open(TITLE_FILE, "r", encoding="utf-8") as f: return f.read().strip()

def set_meeting_title(title):
    with open(TITLE_FILE, "w", encoding="utf-8") as f: f.write(title)

def get_all_votes():
    votes = {}
    if os.path.exists(VOTE_FILE):
        with open(VOTE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "," in line:
                    r, b = line.strip().split(",")
                    votes[r] = b
    return votes

def save_vote(rep, ballot):
    votes = get_all_votes()
    votes[rep] = ballot
    with open(VOTE_FILE, "w", encoding="utf-8") as f:
        for r, b in votes.items(): f.write(f"{r},{b}\n")

def clear_all_votes():
    if os.path.exists(VOTE_FILE): os.remove(VOTE_FILE)

# 🗳️ 【核心優化】精簡投票按鈕渲染函式，避免冗長程式碼被截斷
def render_voting_buttons(identity, prefix):
    c1, c2, c3 = st.columns(3)
    options = [("🟩 投 贊成", "贊成", "yes"), ("🟥 投 反對", "反對", "no"), ("🟨 投 棄權", "棄權", "abs")]
    cols = [c1, c2, c3]
    for col, (label, val, key_suffix) in zip(cols, options):
        with col:
            if st.button(label, key=f"{prefix}_{key_suffix}", use_container_width=True):
                save_vote(identity, val)
                st.rerun()

# 網頁初始化與全自動跳秒刷新
st.set_page_config(layout="wide", page_title="松山高中學生議會表決系統")
st_autorefresh(interval=1000, key="vote_counter_refresh")

voting_status, voting_end_time = get_voting_status()
voting_active = (voting_status == "active")
current_votes, meeting_title = get_all_votes(), get_meeting_title()

remaining_seconds = max(0, int(voting_end_time - time.time())) if voting_active else 0
if voting_active and remaining_seconds <= 0: voting_active = False

st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>🏛️ 臺北市立松山高級中學學生議會電子表決系統</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; background-color: #F0F2F6; padding: 10px; border-radius: 5px; color: #333333;'>📌 當前議題：{meeting_title}</h2>", unsafe_allow_html=True)

if voting_active:
    m, s = divmod(remaining_seconds, 60)
    st.markdown(f"<h2 style='text-align: center; color: #dc3545; background-color: #ffeeba; padding: 10px; border-radius: 5px;'>⏳ 投票剩餘時間：{m:02d} 分 {s:02d} 秒</h2>", unsafe_allow_html=True)
else:
    st.markdown(f"<h2 style='text-align: center; color: #6c757d; background-color: #e2e3e5; padding: 10px; border-radius: 5px;'>🛑 投票目前處於截止或未開放狀態</h2>", unsafe_allow_html=True)

user_token = st.text_input("🔑 請輸入你的 5 位數專屬投票驗證碼：", type="password").strip()

if user_token in TOKEN_MAP:
    my_identity = TOKEN_MAP[user_token]
    
    if my_identity == CHAIRMAN_IDENTITY:
        st.success(f"👑 歡迎主席（{CHAIRMAN_IDENTITY}）登入中央控制台！")
        new_title = st.text_input("✍️ 請輸入本次表決標題（按 Enter 同步）：", value=meeting_title)
        if new_title != meeting_title: set_meeting_title(new_title); st.rerun()
            
        st.write("⏱️ **設定本次表決限時：**")
        t1, t2 = st.columns(2)
        with t1: duration_min = st.number_input("設定分鐘：", min_value=0, max_value=60, value=1, step=1)
        with t2: duration_sec = st.number_input("設定秒數：", min_value=0, max_value=59, value=0, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 開啟現場即時表決並開始倒數", use_container_width=True):
                total_duration = (duration_min * 60) + duration_sec
                if total_duration > 0: set_voting_status("active", time.time() + total_duration); clear_all_votes(); st.rerun()
                else: st.error("❌ 請設定大於 0 秒的時間！")
        with col2:
            if st.button("🔴 強制截止投票並清空", use_container_width=True): set_voting_status("stop", 0.0); st.rerun()
                
        st.subheader("📢 【表決中】請代表們開始按鍵..." if voting_active else "🛑 【截止】等待主席發動議")
        
        if voting_active:
            st.write(f"### 🗳️ 主席兼代表表決 (目前狀態：{current_votes.get(CHAIRMAN_IDENTITY, '未投')})")
            render_voting_buttons(CHAIRMAN_IDENTITY, "chair")

        st.divider()
        st.write("### 📊 代表表決看板 (後台同步即時亮燈)")
        cols = st.columns(5)
        for idx, rep in enumerate(REPRESENTATIVES):
            with cols[idx % 5]:
                v = current_votes.get(rep, "未投")
                if v == "贊成": st.markdown(f"<div style='border: 3px solid #28a745; padding:8px; border-radius:5px; text-align:center; color:#28a745; font-weight:bold; margin-bottom:5px; background-color:#e8f5e9;'>🟩 {rep}</div>", unsafe_allow_html=True)
                elif v == "反對": st.markdown(f"<div style='border: 3px solid #dc3545; padding:8px; border-radius:5px; text-align:center; color:#dc3545; font-weight:bold; margin-bottom:5px; background-color:#fce8e6;'>🟥 {rep}</div>", unsafe_allow_html=True)
                elif v == "棄權": st.markdown(f"<div style='border: 3px solid #ffc107; padding:8px; border-radius:5px; text-align:center; color:#b78103; font-weight:bold; margin-bottom:5px; background-color:#fffde7;'>🟨 {rep}</div>", unsafe_allow_html=True)
                else: st.markdown(f"<div style='border: 1px solid #CCCCCC; padding:8px; border-radius:5px; text-align:center; color:#888888; margin-bottom:5px;'>{rep}</div>", unsafe_allow_html=True)

        y, n, a = list(current_votes.values()).count("贊成"), list(current_votes.values()).count("反對"), list(current_votes.values()).count("棄權")
        st.divider()
        st.markdown(f"<h3>🧮 目前票數統計： <span style='color:#28a745;'>贊成 {y}</span> 票 | <span style='color:#dc3545;'>反對 {n}</span> 票 | <span style='color:#b78103;'>棄權 {a}</span> 票 （總投票數：{y+n+a} / {len(REPRESENTATIVES)}）</h3>", unsafe_allow_html=True)

    else:
        st.success(f"👋 歡迎 {my_identity} 登入系統")
        if voting_active:
            st.write(f"### 🗳️ 請選擇您的表決立場（目前紀錄為：**{current_votes.get(my_identity, '未投')}**）：")
            render_voting_buttons(my_identity, "rep")
        else:
            st.info("🛑 目前未開放表決，或主席已截止本次投票。請靜候主席發起下一案。")
elif user_token != "":
    st.error("❌ 驗證碼錯誤，請重新輸入！")
