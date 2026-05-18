import streamlit as st
import time
import shelve

st.header("🛡️ Панель администратора", divider="red")

st.markdown("""
    <style>
    .user-card { background-color: #f1f3f7; padding: 15px; border-radius: 12px; border-left: 6px solid #ff4b4b; margin-bottom: 5px; }
    .user-name { font-size: 18px; font-weight: bold; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.subheader("👥 Все зарегистрированные пользователи и кредиты")

current_admin_nick = str(st.session_state.get("nickname", "")).strip()

# Читаем данные напрямую из физической базы сервера
db_server = shelve.open("server_bank_db", writeback=True)

# Собираем список реальных пользователей из базы данных
users_in_db = {}
for key in list(db_server.keys()):
    if key != "bank_balance" and str(key).strip() != "" and str(key).strip() != current_admin_nick:
        users_in_db[str(key)] = db_server[key]

if not users_in_db:
    st.info("В базе данных системы пока нет зарегистрированных пользователей.")
else:
    for nick, data in users_in_db.items():
        # Считаем сумму кредитов пользователя напрямую из его истории в базе
        loans = data.get("loans", [])
        credit = sum(l.get("amount", 0) for l in loans)
        
        with st.container():
            st.markdown(f"""<div class="user-card"><div class="user-name">👤 Пользователь: {nick}</div></div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: 
                # Баланс по умолчанию, если у вас в сессии (можно привязать к базе при необходимости)
                st.metric(label="💰 Последний баланс сессии", value=f"{st.session_state.get('b', 1000)} руб.")
            with col2:
                if credit > 0:
                    st.metric(label="🚨 Взят кредит", value=f"{credit} руб.", delta=f"-{credit} руб.", delta_color="inverse")
                else:
                    st.metric(label="✅ Взят кредит", value="0 руб.")
            
            if credit > 0:
                if st.button(f"❌ Аннулировать кредит для {nick}", key=f"clr_{nick}", type="primary"):
                    # Удаляем кредит физически из базы сервера!
                    db_server[nick]["loans"] = []
                    db_server.sync()
                    
                    st.success(f"Кредит пользователя {nick} успешно удален из базы данных!")
                    time.sleep(0.8)
                    st.rerun()
            st.write("")
            st.markdown("---")

# Показываем баланс самого банка
bank_balance = db_server.get("bank_balance", 60000.0)
st.metric("🏦 Остаток капитала в банке", f"{bank_balance} руб.")

db_server.close()
