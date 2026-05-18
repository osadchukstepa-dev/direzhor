import streamlit as st
import time
import shelve

st.header("🛡️ Панель администратора", divider="red")

st.markdown("""
    <style>
    .user-card { background-color: #f1f3f7; padding: 15px; border-radius: 12px; border-left: 6px solid #ff4b4b; margin-bottom: 5px; }
    .user-name { font-size: 18px; font-weight: bold; color: #1e293b; }
    .loan-row { background-color: #ffffff; padding: 10px; border-radius: 8px; margin-bottom: 5px; border: 1px solid #e2e8f0; }
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
        loans = data.get("loans", [])
        total_credit = sum(l.get("amount", 0) for l in loans)
        
        with st.container():
            st.markdown(f"""<div class="user-card"><div class="user-name">👤 Пользователь: {nick}</div></div>""", unsafe_allow_html=True)
            
            col_inf1, col_inf2 = st.columns(2)
            with col_inf1: 
                st.metric(label="💰 Последний баланс сессии", value=f"{st.session_state.get('b', 1000)} руб.")
            with col_inf2:
                if total_credit > 0:
                    st.metric(label="🚨 Всего долгов", value=f"{total_credit} руб.", delta=f"-{total_credit} руб.", delta_color="inverse")
                else:
                    st.metric(label="✅ Всего долгов", value="0 руб.")
            
            # Если у пользователя есть кредиты, выводим их поштучно
            if loans:
                st.write("**Список активных кредитов:**")
                
                # Итерируемся по списку кредитов с индексами, чтобы удалять конкретный
                for index, loan in enumerate(loans):
                    loan_name = loan.get("name_kredite", "Без названия")
                    loan_amount = loan.get("amount", 0)
                    loan_repayment = loan.get("repayment", 0)
                    loan_end = loan.get("date_end", "Не указана")
                    
                    # Создаем контейнер для одной строчки кредита
                    with st.container():
                        col_loan_info, col_loan_btn = st.columns([3, 1])
                        
                        with col_loan_info:
                            st.markdown(f"""
                            <div class="loan-row">
                                📌 <b>{loan_name}</b><br>
                                Сумма: {loan_amount} ₽ | К возврату: {loan_repayment} ₽<br>
                                Срок до: {loan_end}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col_loan_btn:
                            # Кнопка удаления конкретного кредита по его уникальному индексу
                            if st.button(f"❌ Удалить", key=f"del_{nick}_{index}", type="primary"):
                                # Удаляем элемент из списка по индексу
                                db_server[nick]["loans"].pop(index)
                                db_server.sync()
                                
                                st.success(f"Кредит '{loan_name}' удален!")
                                time.sleep(0.5)
                                st.rerun()
            else:
                st.caption("Нет активных кредитов")
                
            st.write("")
            st.markdown("---")

# Показываем баланс самого банка
bank_balance = db_server.get("bank_balance", 60000.0)
st.metric("🏦 Остаток капитала в банке", f"{bank_balance} руб.")

db_server.close()
