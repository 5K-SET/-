import streamlit as st
import time
import os

# ==================== 【松山高中學生議會：名冊與 5 碼代碼設定區】 ====================
# 主席可以在這裡自由修改、新增或替換「班代」與「5位數亂碼」的對應表！
# 格式為 "5位數代碼": "班級名稱"
TOKEN_MAP = {
    "SS001": "101 班代", "SS002": "102 班代", "SS003": "103 班代", "SS004": "104 班代", "SS005": "105 班代",
    "SS006": "106 班代", "SS007": "107 班代", "SS008": "108 班代", "SS009": "109 班代", "SS010": "110 班代",
    "SS011": "111 班代", "SS012": "112 班代", "SS013": "113 班代", "SS014": "114 班代", "SS015": "115 班代",
    "SS016": "116 班代", "SS017": "117 班代", "SS018": "118 班代", "SS019": "119 班代",
    
    "SS021": "201 班代", "SS022": "202 班代", "SS023": "203 班代", "SS024": "204 班代", "SS025": "205 班代",
    "SS026": "206 班代", "SS027": "207 班代", "SS028": "208 班代", "SS029": "209 班代", "SS030": "210 班代",
    "SS031": "211 班代", "SS032": "212 班代", "SS033": "213 班代", "SS034": "214 班代", "SS035": "215 班代",
    "SS036": "216 班代", "SS037": "217 班代", "SS038": "218 班代", "SS039": "219 班代",
    
    "SS041": "301 班代", "SS042": "302 班代", "SS043": "303 班代", "SS044": "304 班代", "SS045": "305 班代",
    "SS046": "306 班代", "SS047": "307 班代", "SS048": "308 班代", "SS049": "309 班代", "SS050": "310 班代",
    "SS051": "311 班代", "SS052": "312 班代", "SS053": "313 班代", "SS054": "314 班代", "SS055": "315 班代",
    "SS056": "316 班代", "SS057": "317 班代", "SS058": "318 班代", "SS059": "319 班代"
}

# 這裡由系統自動撈出全體班代清單來做立法院大看板
REPRESENTATIVES = list(TOKEN_MAP.values())

STATUS_FILE = "status.txt"
VOTE_FILE = "votes.txt"

def get_voting_active():
    if not os.path.exists(STATUS_FILE): return False
    with open(STATUS_FILE, "r") as f: return f.read().strip() == "active"

def set_voting_active(active):
    with open(STATUS_FILE, "w") as f: f.write("active" if active else "stop")

def get_all_votes():
    votes = {}
    if os.path.exists(VOTE_FILE):
        with open(VOTE_FILE, "r") as f:
            for line in f:
                if "," in line:
                    rep, b = line.strip().split(",")
                    votes[rep] = b
    return votes

def save_vote(rep, ballot):
    votes = get_all_votes()
    votes[rep] = ballot
    with open(VOTE_FILE, "w") as f:
        for r, b in votes.items(): f.write(f"{r},{b}\n")

def clear_all_votes():
    if os.path.exists(VOTE_FILE): os.remove(VOTE_FILE)

st.set_page_config(layout="wide")
st.title("🏛️ 臺北市立松山高級中學學生議會 - 即時電子記名表決系統")

query_params = st.query_params
is_admin = query_params.get("role") == "admin"

voting_active = get_voting_active()
current_votes = get_all_votes()

# ==================== 【👑 主席 / 控台大螢幕介面】 ====================
if is_admin:
    st.header("🎮 議事中央控制台 (大螢幕投影)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 開啟現場即時表決 (全場手機亮燈)", use_container_width=True):
            set_voting_active(True)
            clear_all_votes()
            st.rerun()
            
    with col2:
        if st.button("🔴 截止投票並清空 (準備下一動議)", use_container_width=True):
            set_voting_active(False)
            st.rerun()

    status = "📢 【表決中】請代表們開始按鍵..." if voting_active else "🛑 【截止】等待主席發動議"
    st.subheader(status)

    st.divider()
    st.write("### 📊 松山高中班代表記名投票看板 (立法院風格)")
    
    cols = st.columns(6) 
    for idx, rep in enumerate(REPRESENTATIVES):
        with cols[idx % 6]:
            voted_ballot = current_votes.get(rep, "⏳ 未投")
            if voted_ballot == "贊成": st.success(f"{rep}: 🟩 贊成")
            elif voted_ballot == "反對": st.error(f"{rep}: 🟥 反對")
            elif voted_ballot == "棄權": st.warning(f"{rep}: 🟨 棄權")
            else: st.text(f"{rep}: ⏳ 未投")

    total_yes = list(current_votes.values()).count("贊成")
    total_no = list(current_votes.values()).count("反對")
    total_abstain = list(current_votes.values()).count("棄權")
    
    st.divider()
    st.write(f"### 🧮 目前票數統計： 贊成 {total_yes} 票 | 反對 {total_no} 票 | 棄權 {total_abstain} 票")
    
    # 稍微延長到2秒更新一次，兼顧即時性又解決狂閃的問題！
    time.sleep(2)
    st.rerun()

# ==================== 【📱 班代表手機投票端介面】 ====================
else:
    st.header("📱 班代表電子表決按鈕")
    
    # 🌟 防弊核心：改用 5 碼專屬代碼輸入框
    user_token = st.text_input("🔑 請輸入你的 5 位數專屬投票驗證碼：", type="password").strip()
    
    if user_token in TOKEN_MAP:
        my_identity = TOKEN_MAP[user_token]
        st.success(f"✅ 身分驗證成功：**{my_identity}**")
        
        if voting_active:
            st.write("### 🚨 主席已發起表決，請按鍵：")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 贊成", use_container_width=True):
                    save_vote(my_identity, "贊成")
                    st.toast("投票成功：贊成")
            with c2:
                if st.button("🟥 反對", use_container_width=True):
                    save_vote(my_identity, "反對")
                    st.toast("投票成功：反對")
            with c3:
                if st.button("🟨 棄權", use_container_width=True):
                    save_vote(my_identity, "棄權")
                    st.toast("投票成功：棄權")
                    
            my_current = current_votes.get(my_identity, "尚未按鍵")
            st.info(f"你目前的投票紀錄：【{my_current}】（在截止前都可以重新按鈕修改）")
            
        else:
            st.warning("⏳ 目前沒有正在進行的表決。請聆聽議場討論，等待主席開啟按鈕。")
            
    elif user_token != "":
        st.error("❌ 找不到此投票代碼，請重新輸入或洽詢議事人員。")
        
    time.sleep(2)
    st.rerun()
