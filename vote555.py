import streamlit as st
import time

# ==================== 【設定專區】 ====================
ADMIN_PASSWORD = "nhshsa2026"  # 👈 主席控制台解鎖密碼

# 自動產生內湖高中 101~119, 201~219, 301~319 的真實班級名單
REPRESENTATIVES = []
for grade in:
    for className in range(1, 20):  # 1到19班
        REPRESENTATIVES.append(f"{grade}{className:02d} 班代")
# ====================================================

# 🌟【終極救星：建立全場數據廣播器】🌟
@st.cache_resource
def get_global_state():
    return {
        "voting_active": False,  # 全場投票狀態
        "votes": {}              # 全場記名票數
    }

global_state = get_global_state()

st.set_page_config(layout="wide")

# 【左側中文防呆切換中心】
with st.sidebar:
    st.header("⚙️ 議事切換中心")
    role_option = st.radio("請選擇你的身份：", ["📱 班代表投票端", "👑 主席/大螢幕控制台"])
    
    is_admin = False
    if role_option == "👑 主席/大螢幕控制台":
        pwd_input = st.text_input("🔑 請輸入安全密碼：", type="password")
        if pwd_input == ADMIN_PASSWORD:
            is_admin = True
            st.success("密碼正確！已解鎖主席權限。")
        elif pwd_input != "":
            st.error("密碼錯誤！")

st.title("🏛️ 內湖高中學生代表大會 - 即時電子記名表決系統")

# ==================== 【👑 主席 / 大螢幕控制台介面】 ====================
if is_admin:
    st.header("🎮 議事中央控制台 (大螢幕投影專用)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 開啟現場即時表決 (全場手機亮燈)", use_container_width=True):
            global_state["voting_active"] = True
            global_state["votes"] = {}  # 清空上一輪
            st.success("📢 已向全場班代手機發射投票訊號！")
            time.sleep(0.5)
            st.rerun()
            
    with col2:
        if st.button("🔴 截止投票並清空 (準備下一動議)", use_container_width=True):
            global_state["voting_active"] = False
            st.success("🛑 投票已終止！")
            time.sleep(0.5)
            st.rerun()

    status = "📢 【表決中】請代表們開始按鍵..." if global_state["voting_active"] else "🛑 【截止】等待主席發動議"
    st.subheader(status)

    st.divider()
    st.write("### 📊 內中班代表記名投票看板 (立法院風格)")
    
    # 顯示全校 57 個班級的即時亮燈看板
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
        
        if global_state["voting_active"]:
            st.write("### 🚨 主席已發起表決，請按鍵：")
            
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
                    
            current_choice = global_state["votes"].get(my_identity, "尚未按鍵")
            st.info(f"你目前的投票紀錄：【{current_choice}】（在截止前都可以重新按鈕修改）")
            
        else:
            st.warning("⏳ 目前沒有正在進行的表決。請聆聽議場討論，等待主席開啟按鈕。")
            
    time.sleep(1)
    st.rerun()
