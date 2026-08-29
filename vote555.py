import streamlit as st
import time
import os

# ==================== 【松山高中學生議會設定區：每級20班名冊與代碼】 ====================
TOKEN_MAP = {}
# 自動產生 101~120, 201~220, 301~320 的真實班級名單與預設代碼
# 密碼邏輯：高一為 SS101~SS120，高二為 SS201~SS220，高三為 SS301~SS320
for grade in:
    for className in range(1, 21):  # 1 到 20 班
        token = f"SS{grade}{className:02d}"
        rep_name = f"{grade}{className:02d} 班代"
        TOKEN_MAP[token] = rep_name

CHAIRMAN_IDENTITY = "203 班代"  # 👈 主席身分（輸入對應密碼 SS203 就會變身主席控制台）
# ====================================================================

REPRESENTATIVES = list(TOKEN_MAP.values())
STATUS_FILE = "status.txt"
VOTE_FILE = "votes.txt"
TITLE_FILE = "title.txt"  # 儲存主席輸入的臨時標題

def get_voting_active():
    if not os.path.exists(STATUS_FILE): return False
    with open(STATUS_FILE, "r") as f: return f.read().strip() == "active"

def set_voting_active(active):
    with open(STATUS_FILE, "w") as f: f.write("active" if active else "stop")

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

st.set_page_config(layout="wide")

# 撈取目前全域資料
voting_active = get_voting_active()
current_votes = get_all_votes()
meeting_title = get_meeting_title()

# 顯示動態大標題（全場同步看主席打什麼字）
st.markdown(f"<h1 style='text-align: center; color: #4A90E2;'>🏛️ 臺北市立松山高級中學學生議會</h1>", unsafe_allow_html=True)
st.markdown(f"<h2 style='text-align: center; background-color: #F0F2F6; padding: 10px; border-radius: 5px;'>📌 當前議題：{meeting_title}</h2>", unsafe_allow_html=True)

# 唯一的密碼驗證框
user_token = st.text_input("🔑 請輸入你的 5 位數專屬投票驗證碼：", type="password").strip()

if user_token in TOKEN_MAP:
    my_identity = TOKEN_MAP[user_token]
    
    # 👑【核心判定：主席登入】👑
    if my_identity == CHAIRMAN_IDENTITY:
        st.success(f"👑 歡迎主席（{CHAIRMAN_IDENTITY}）登入中央控制台！")
        
        # 主席打字輸入框（動態變更現場大螢幕標題）
        new_title = st.text_input("✍️ 請輸入本次表決的法案/動議標題（打完字按下 Enter 即可同步大螢幕）：", value=meeting_title)
        if new_title != meeting_title:
            set_meeting_title(new_title)
            st.rerun()
        
        # 議事控制按鈕
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
        
        # 主席專屬記名表決區
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
            my_vote = current_votes.get(CHAIRMAN_IDENTITY, "尚未按鍵")
            st.info(f"主席目前投票紀錄：【{my_vote}】")

        st.divider()
        st.write("### 📊 代表表決看板 (未投票班級不加字隱形)")
        
        # 顯示全校 60 個班級的極簡亮燈看板
        cols = st.columns(5) # 改為一排 5 個班級，完美平分高一到高三的20班
        for idx, rep in enumerate(REPRESENTATIVES):
            with cols[idx % 5]:
                voted_ballot = current_votes.get(rep, "未投")
                if voted_ballot == "贊成": 
                    st.markdown(f"<div style='background-color:#D4EDDA; padding:8px; border-radius:5px; text-align:center; color:#155724; font-weight:bold; margin-bottom:5px;'>🟩 {rep}</div>", unsafe_allow_html=True)
                elif voted_ballot == "反對": 
                    st.markdown(f"<div style='background-color:#F8D7DA; padding:8px; border-radius:5px; text-align:center; color:#721C24; font-weight:bold; margin-bottom:5px;'>🟥 {rep}</div>", unsafe_allow_html=True)
                elif voted_ballot == "棄權": 
                    st.markdown(f"<div style='background-color:#FFF3CD; padding:8px; border-radius:5px; text-align:center; color:#856404; font-weight:bold; margin-bottom:5px;'>🟨 {rep}</div>", unsafe_allow_html=True)
                else: 
                    st.write(rep) # 未投票就只有乾淨的班級名字，沒有任何符號或狀態字眼！

        total_yes = list(current_votes.values()).count("贊成")
        total_no = list(current_votes.values()).count("反對")
        total_abstain = list(current_votes.values()).count("棄權")
        
        st.divider()
        st.markdown(f"<h3>🧮 目前票數統計： <span style='color:green;'>贊成 {total_yes}</span> 票 | <span style='color:red;'>反對 {total_no}</span> 票 | <span style='color:orange;'>棄權 {total_abstain}</span> 票</h3>", unsafe_allow_html=True)
        
        time.sleep(2)
        st.rerun()
        
    # 📱【一般代表登入】📱
    else:
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
            
        time.sleep(2)
        st.rerun()

elif user_token != "":
    st.error("❌ 找不到此投票代碼，請重新輸入或洽詢議事人員。")

