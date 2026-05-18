import streamlit as st
import time
import shelve

@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

st.header("🛡️ Панель администратора", divider="red")

st.markdown("""
    <style>
    .user-card { background-color: #f1f3f7; padding: 15px; border-radius: 12px; border-left: 6px solid #ff4b4b; margin-bottom: 5px; }
    .user-name { font-size: 18px; font-weight: bold; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.subheader("👥 Пользователи активны на сервере")

current_admin_nick = str(st.session_state.get("nickname", ""))

# ЗАЩИЩЕННАЯ ФИЛЬТРАЦИЯ: принудительно переводим ключи в строку, чтобы .strip() не падал
active_users = {}
for user, data in list(global_db.items()):
    user_str = str(user).strip()
    if user_str != "" and user_str != current_admin_nick.strip():
        active_users[user_str] = data

if not active_users:
    st.info("В данный момент других активных пользователей на сервере нет.")
else:
    for nick, data in list(active_users.items()):
        with st.container():
            st.markdown(f"""<div class="user-card"><div class="user-name">🟢 В сети: {nick}</div></div>""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1: st.metric(label="💰 Баланс", value=f"{data.get('balance', 1000)} руб.")
            with col2: st.metric(label="💳 Лимит", value=f"{data.get('credit_limit', 60000)} руб.")
            with col3:
                credit = data.get("credit_taken", 0)
                if credit > 0:
                    st.metric(label="🚨 Взят кредит", value=f"{credit} руб.", delta=f"-{credit} руб.", delta_color="inverse")
                else:
                    st.metric(label="✅ Взят кредит", value="0 руб.")
            
            if credit > 0:
                if st.button(f"❌ Аннулировать кредит для {nick}", key=f"clr_{nick}", type="primary"):
                    # 1. Сбрасываем в оперативной памяти админки
                    global_db[nick]["credit_taken"] = 0
                    
                    # 2. Удаляем кредит из базы данных сервера shelve
                    try:
                        db_server = shelve.open("server_bank_db", writeback=True)
                        if nick in db_server:
                            db_server[nick]["loans"] = []  # Очищаем список кредитов
                            db_server.sync()
                        db_server.close()
                    except:
                        pass
                            
                    st.success(f"Кредит пользователя {nick} успешно закрыт!")
                    time.sleep(0.8)
                    st.rerun()
            st.write("")
            st.markdown("---")
