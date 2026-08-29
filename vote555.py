import streamlit as st
import time

# 🌟【終極大絕招：改用最純粹的 Python 全域共享字典】🌟
# 這次保證絕對不會再有語法錯誤
if "GLOBAL_VOTE_DATA" not in globals():
    globals()["GLOBAL_VOTE_DATA"] = {
        "voting_active": False,  # 全場投票狀態
        "votes": {}              # 全場記名票數
    }

# 從全域環境中抓出共享資料
global_state = globals()["GLOBAL_VOTE_DATA"]

# 手動輸入內湖高中真實班級名冊
REPRESENTATIVES = [
    "101 班代", "102 班代", "103 班代", "104 班代", "105 班代", "106 班代", "107 班代", "108 班代", "109 班代", "110 班代", "111 班代", "112 班代", "113 班代", "114 班代", "115 班代", "116 班代", "117 班代", "118 班代", "119 班代",
    "201 班代", "202 班代", "203 班代", "204 班代", "205 班代", "206 班代", "207 班代", "208 班代", "209 班代", "210 班代", "211 班代", "212 班代", "213 班代", "214 班代", "215 班代", "216 班代", "217 班代", "218 班代", "219 班代",
    "301 班代", "302 班代", "303 班代", "304 班代", "305 班代", "306 班代", "307 班代", "308 班代", "309 班代", "310 班代", "311 班代", "312 班代", "313 班代", "314 班代", "315 班代", "316 班代", "317 班代", "318 班代", "319 班代"
]

st.set_page_config(layout="wide")
st.title("🏛️ 內湖高中學生代表大會 - 即時電子記名表決系統")

# 用網址參數來區分是「控台大螢幕」還是「班代手機」
query_params = st.query_params
is_admin = query_params.get("role") == "admin"

# ==================== 【👑 主席 / 控台大螢幕介面】 ====================
if is_admin:
    st.header("🎮 議事中央控制台 (大螢幕投影)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 開啟現場即時表決 (全場手機亮燈)", use_container_width=True):
            global_state["voting_active"] = True
            global_state["votes"] = {} # 清空上一題的票數
            st.success("📢 已成功向全場發射亮燈訊號！")
            time.sleep(0.5)
            st.rerun()
            
    with col2:
        if st.button("🔴 截止投票並清空 (準備下一動議)", use_container_width=True):
            global_state["voting_active"] = False
            st.success("🛑 投票已終止！")
            time.sleep(0.5)
            st.rerun()

    # 顯示目前投票狀態
    status = "📢 【表決中】請代表們開始按鍵..." if global_state["voting_active"] else "🛑 【截止】等待主席發動議"
    st.subheader(status)

    # 顯示立法院風格的電子記名看板
    st.divider()
    st.write("### 📊 內中班代表記名投票看板")
    
    cols = st.columns(6) 
    for idx, rep in enumerate(REPRESENTATIVES):
        with cols[idx % 6]:
            voted_ballot = global_state["votes"].get(rep, "⏳ 未投")
            if voted_ballot == "贊成":
                st.success(f"{rep}: 🟩 贊成")
            elif voted_ballot == "反對":
                st.error(f"{rep}: 🟥 反對")
            elif voted_ballot == "棄權":
                st.warning(f"{rep}: 🟨 棄權")
            else:
                st.text(f"{rep}: ⏳ 未投")

    # 即時計算總票數
    total_yes = list(global_state["votes"].values()).count("贊成")
    total_no = list(global_state["votes"].values()).count("反對")
    total_abstain = list(global_state["votes"].values()).count("棄權")
    
    st.divider()
    st.write(f"### 🧮 目前票數統計： 贊成 {total_yes} 票 | 反對 {total_no} 票 | 棄權 {total_abstain} 票")
    
    time.sleep(1)
    st.rerun()

# ==================== 【📱 班代表手機投票端介面】 ====================
else:
    st.header("📱 班代表電子表決按鈕")
    
    my_identity = st.selectbox("請選擇你的班級身份：", ["--- 請選擇你的班級 ---"] + REPRESENTATIVES)
    
    if my_identity != "--- 請選擇你的班級 ---":
        st.write(f"當前登入代表：**{my_identity}**")
        
        # 判斷控台有沒有啟動表決
        if global_state["voting_active"]:
            st.write("### 🚨 主席已發起表決，請按鍵：")
            
            # 投票按鈕
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🟩 贊成", use_container_width=True):
                    global_state["votes"][my_identity] = "贊成"
                    st.toast("投票成功：贊成")
            with c2:
                if st.button("🟥 反對", use_container_width=True):
                    global_state["votes"][my_identity] = "反對"
                    st.toast("投票成功：反對")
            with c3:
                if st.button("🟨 棄權", use_container_width=True):
                    global_state["votes"][my_identity] = "棄權"
                    st.toast("投票成功：棄權")
                    
            # 顯示自己目前的投票意向
            current_choice = global_state["votes"].get(my_identity, "尚未按鍵")
            st.info(f"你目前的投票紀錄：【{current_choice}】（在截止前都可以重新按鈕修改）")
            
        else:
            st.warning("⏳ 目前沒有正在進行的表決。請聆聽議場討論，等待主席開啟按鈕。")
            
    time.sleep(1)
    st.rerun()
