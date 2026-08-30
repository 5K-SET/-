import streamlit as st
import time
import os

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

def get_voting_status():
    """讀取當前投票狀態與截止時間戳"""
    if not os.path.exists(STATUS_FILE): 
        return "stop", 0.0
    with open(STATUS_FILE, "r") as f: 
        content = f.read().strip().split(",")
        status = content[0]
        end_time = float(content[1]) if len(content) > 1 else 0.0
        
        # 【重要安全機制】如果在讀取時發現時間已經到了，自動在後台改成停止
        if status == "active" and time.time() > end_time:
            set_voting_status("stop", 0.0)
            return "stop", 0.0
            
        return status, end_time

def set_voting_status(status, end_time=0.0):
    """寫入當前投票狀態與截止時間戳"""
    with open(STATUS_FILE, "w") as f: 
        f.write(f"{status},{end_time}")

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

# 設定頁面
st.set_page_config(layout="wide", page_title="松山高中學生議會表決系統")

# 每 1 秒自動刷新畫面（確保倒數計時數字即時更新）
st.fragment(run_every=1.0)(lambda: None)()

# 獲取最新狀態
voting_status, voting_end_time = get_voting_status()
voting_active = (voting_status == "active")
current_votes = get_all_votes()
meeting_title = get_meeting_title()

# 計算剩餘秒數
remaining_seconds = 0
if voting_active:
    remaining_seconds = max(0, int(voting_end_time - time.time()))
    if remaining_seconds == 0:
        voting_active = False  # 畫面上同步更新為截止

# 頂部精美大標題與動態議題投放區
st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>🏛️ 臺北市立松山高級中學學生議會電子表決系統</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; background-color: #F0F2F6; padding: 10px; border-radius: 5px; color: #333333;'>📌 當前議題：{meeting_title}</h2>", unsafe_allow_html=True)

# 顯示全場醒目的倒數計時器
if voting_active:
    mins, secs = divmod(remaining_seconds, 60)
    st.markdown(f"<h2 style='text-align: center; color: #dc3545; background-color: #ffeeba; padding: 10px; border-radius: 5px;'>⏳ 投票剩餘時間：{mins} 分 {secs} 秒</h2>", unsafe_allow_html=True)

user_token = st.text_input("🔑 請輸入你的 5 位數專屬投票驗證碼：", type="password").strip()

if user_token in TOKEN_MAP:
    my_identity = TOKEN_MAP[user_token]
    
    # 👑【主席控制台介面】👑
    if my_identity == CHAIRMAN_IDENTITY:
        st.success(f"👑 歡迎主席（{CHAIRMAN_IDENTITY}）登入中央控制台！")
        
        new_title = st.text_input("✍️ 請輸入本次表決的法案/動議標題（打完字按 Enter 同步大螢幕）：", value=meeting_title)
        if new_title != meeting_title:
            set_meeting_title(new_title)
            st.rerun()
            
        # ⏳ 主席設定倒數時間區（只有在未投票狀態下可以設定）
        st.write("⏱️ **設定本次表決限時：**")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            duration_min = st.number_input("設定分鐘：", min_value=0, max_value=60, value=1, step=1)
        with t_col2:
            duration_sec = st.number_input("設定秒數：", min_value=0, max_value=59, value=0, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 開啟現場即時表決 (全場手機亮燈 + 開始倒數)", use_container_width=True):
                total_duration = (duration_min * 60) + duration_sec
                if total_duration <= 0:
                    st.error("❌ 請設定大於 0 秒的時間！")
                else:
                    end_timestamp = time.time() + total_duration
                    set_voting_status("active", end_timestamp)
                    clear_all_votes()
                    st.rerun()
        with col2:
            if st.button("🔴 強制截止投票並清空 (準備下一動議)", use_container_width=True):
                set_voting_status("stop", 0.0)
                st.rerun()
                
        status = "📢 【表決中】請代表們開始按鍵..." if voting_active else "🛑 【截止】等待主席發動議"
        st.subheader(status)
        
        # 主席兼代表表決區
        if voting_active:
            st.write(f"### 🗳️ 主席兼代表表決")
            my_current_vote = current_votes.get(CHAIRMAN_IDENTITY, "未投")
            st.info(f"您目前的投票狀態：**{my_current_vote}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 投 贊成", key="chair_yes", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "贊成")
                    st.rerun()
            with c2:
                if st.button("🟥 投 反對", key="chair_no", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "反對")
                    st.rerun()
            with c3:
                if st.button("🟨 投 棄權", key="chair_abs", use_container_width=True):
                    save_vote(CHAIRMAN_IDENTITY, "棄權")
                    st.rerun()

        st.divider()
        st.write("### 📊 代表表決看板 (畫面每 1 秒自動更新)")
        
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
        total_voted = total_yes + total_no + total_abstain
        
        st.divider()
        st.markdown(
            f"<h3>🧮 目前票數統計： "
            f"<span style='color:#28a745;'>贊成 {total_yes}</span> 票 | "
            f"<span style='color:#dc3545;'>反對 {total_no}</span> 票 | "
            f"<span style='color:#ffc107;'>棄權 {total_abstain}</span> 票 "
            f"（總投票數：{total_voted} / {len(REPRESENTATIVES)}）</h3>", 
            unsafe_allow_html=True
        )

    # 📱【一般議員/代表表決介面】📱
    else:
        st.success(f"👋 歡迎 {my_identity} 登入系統")
        
        if voting_active:
            st.write("### 🗳️ 請選擇您的表決立場：")
            my_current_vote = current_votes.get(my_identity, "未投")
            
            if my_current_vote != "未投":
                st.info(f"您已成功提交表決！當前紀錄為：**{my_current_vote}**（在截止前您仍可修改投票）")
            else:
                st.warning("⚠️ 您尚未投票，請選擇下方按鈕提交。")
                
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 贊成 (Approve)", key="rep_yes", use_container_width=True):
                    save_vote(my_identity, "贊成")
                    st.rerun()
            with c2:
                if st.button("🟥 反對 (Reject)", key="rep_no", use_container_width=True):
                    save_vote(my_identity, "反對")
                    st.rerun()
            with c3:
                if st.button("🟨 棄權 (Abstain)", key="rep_abs", use_container_width=True):
                    save_vote(my_identity, "棄權")
                    st.rerun()
        else:
            st.info("🛑 目前未開放表決，或主席已截止本次投票。請靜候主席發起下一案。")

elif user_token != "":
    st.error("❌ 驗證碼錯誤，請重新輸入！")
