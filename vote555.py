import streamlit as st
import time

# 1. 初始化議場狀態與班代名冊（你可以自己修改這份名單）
if 'voting_active' not in st.session_state:
    st.session_state.voting_active = False # 預設表決關閉
if 'votes' not in st.session_state:
    st.session_state.votes = {} # 儲存開票結果

# 這裡填入當天有出席的班代清冊
REPRESENTATIVES = [
    "101 班代", "102 班代", "103 班代", "104 班代", "105 班代",
    "201 班代", "202 班代", "203 班代", "204 班代", "205 班代",
    "301 班代", "302 班代", "303 班代", "304 班代", "305 班代"
]

st.set_page_config(layout="wide")
st.title("🏛️ 內湖高中學生代表大會 - 即時電子記名表決系統")

# 用網址參數來區分是「控台大螢幕」還是「班代手機」
# 網址後面加上 ?role=admin 就是控台
query_params = st.query_params
is_admin = query_params.get("role") == "admin"

# ==================== 【主席 / 控台大螢幕介面】 ====================
if is_admin:
    st.header("🎮 議事中央控制台 (大螢幕投影)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 開啟現場即時表決 (全場手機亮燈)", use_container_width=True):
            st.session_state.voting_active = True
            st.session_state.votes = {} # 清空上一題的票數
            st.rerun()
            
    with col2:
        if st.button("🔴 截止投票並清空 (準備下一動議)", use_container_width=True):
            st.session_state.voting_active = False
            st.rerun()

    # 顯示目前投票狀態
    status = "📢 【表決中】請代表們開始按鍵..." if st.session_state.voting_active else "🛑 【截止】等待主席發起動議"
    st.subheader(status)

    # 顯示立法院風格的電子記名看板
    st.divider()
    st.write("### 📊 班代表記名投票看板")
    
    # 用表格把所有人排出來
    cols = st.columns(5) # 一排顯示5個人
    for idx, rep in enumerate(REPRESENTATIVES):
        with cols[idx % 5]:
            voted_ballot = st.session_state.votes.get(rep, "⏳ 未投票")
            if voted_ballot == "赞成":
                st.success(f"{rep}: 🟩 贊成")
            elif voted_ballot == "反对":
                st.error(f"{rep}: 🟥 反對")
            elif voted_ballot == "弃权":
                st.warning(f"{rep}: 🟨 棄權")
            else:
                st.info(f"{rep}: ⏳ 未投票")

    # 即時計算總票數
    total_yes = list(st.session_state.votes.values()).count("赞成")
    total_no = list(st.session_state.votes.values()).count("反对")
    total_abstain = list(st.session_state.votes.values()).count("弃权")
    
    st.divider()
    st.write(f"### 🧮 目前票數統計： 贊成 {total_yes} 票 | 反對 {total_no} 票 | 棄權 {total_abstain} 票")
    
    # 每秒自動刷新大螢幕看開票進度
    time.sleep(1)
    st.rerun()

# ==================== 【班代表手機投票介面】 ====================
else:
    st.header("📱 班代表電子表決按鈕")
    
    # 讓代表選自己的身份（防止冒用，現場點名核對）
    my_identity = st.selectbox("請選擇你的班級身份：", ["--- 請選擇 ---"] + REPRESENTATIVES)
    
    if my_identity != "--- 請選擇 ---":
        st.write(f"當前登入：**{my_identity}**")
        
        # 判斷控台有沒有啟動表決
        if st.session_state.voting_active:
            st.write("### 🚨 主席已發起表決，請按鍵：")
            
            # 投票按鈕
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 贊成", use_container_width=True):
                    st.session_state.votes[my_identity] = "赞成"
                    st.toast("投票成功：贊成")
            with c2:
                if st.button("🟥 反對", use_container_width=True):
                    st.session_state.votes[my_identity] = "反对"
                    st.toast("投票成功：反對")
            with c3:
                if st.button("🟨 棄權", use_container_width=True):
                    st.session_state.votes[my_identity] = "弃权"
                    st.toast("投票成功：棄權")
                    
            # 顯示自己目前的投票意向
            current_choice = st.session_state.votes.get(my_identity, "尚未按鍵")
            st.info(f"你目前的投票紀錄：【{current_choice}】（在截止前都可以重新按鈕修改）")
            
        else:
            st.warning("⏳ 目前沒有正在進行的表決。請聆聽議場討論，等待主席開啟按鈕。")
            
    # 手機端每2秒檢查一次主席有沒有開題
    time.sleep(2)
    st.rerun()
