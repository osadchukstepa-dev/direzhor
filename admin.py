import streamlit as st
import time

# Подключаемся к глобальной оперативной памяти сервера
@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

# --- НАСТРОЙКА И СТИЛИЗАЦИЯ СТРАНИЦЫ ---
st.header("🛡️ Панель администратора", divider="red")

st.markdown("""
    <style>
    .user-card {
        background-color: #f1f3f7;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 5px;
    }
    .user-name {
        font-size: 18px;
        font-weight: bold;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

st.subheader("👥 Пользователи активны на сервере")

# Фильтруем список: берем всех активных пользователей, ИСКЛЮЧАЯ текущего админа
current_admin_nick = st.session_state.get("nickname", "")
active_users = {
    user: data for user, data in global_db.items() 
    if user.strip() != "" and user != current_admin_nick
}

if not active_users:
    st.info("В данный момент других активных пользователей на сервере нет.")
else:
    # Отображаем только обычных пользователей
    for nick, data in list(active_users.items()):
        with st.container():
            st.markdown(f"""
                <div class="user-card">
                    <div class="user-name">🟢 В сети: {nick}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="💰 Баланс", value=f"{data['balance']} руб.")
            with col2:
                st.metric(label="💳 Лимит кредита", value=f"{data['credit_limit']} руб.")
            with col3:
                credit = data.get("credit_taken", 0)
                if credit > 0:
                    st.metric(label="🚨 Взят кредит", value=f"{credit} руб.", delta=f"-{credit} руб.", delta_color="inverse")
                else:
                    st.metric(label="✅ Взят кредит", value="0 руб.")
            
            # Кнопка закрытия кредита
            if credit > 0:
                if st.button(f"❌ Закрыть кредит для {nick}", key=f"clr_{nick}", type="primary"):
                    global_db[nick]["credit_taken"] = 0
                    st.success(f"Кредит пользователя {nick} успешно закрыт!")
                    time.sleep(0.8)
                    st.rerun()
            
            st.write("")
            st.markdown("---")

    # Секция общей аналитики
    st.subheader("📊 Общая статистика сервера")
    c1, c2 = st.columns(2)
    c1.metric("Других пользователей на GitHub", len(active_users))
    c2.metric("Сумма их кредитов", f"{sum(d.get('credit_taken', 0) for d in active_users.values())} руб.")
