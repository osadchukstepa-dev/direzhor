import streamlit as st
import time
from datetime import date
import shelve
from project import *

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ SHELVE (ВМЕСТО JSON И КУКИ) ---
# shelve автоматически создаст файл базы данных на сервере
db_server = shelve.open("server_bank_db", writeback=True)

# Инициализируем баланс банка, если его еще нет
if "bank_balance" not in db_server:
    db_server["bank_balance"] = 60000.0

# --- ПОДКЛЮЧЕНИЕ ГЛОБАЛЬНОЙ БАЗЫ ДЛЯ АДМИНА ---
@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

# Получаем имя текущего пользователя
user_name = st.session_state.get("nickname", "").strip()

# Если пользователь авторизован, загружаем его кредиты из базы сервера
loans_list = []
if user_name:
    if user_name not in db_server:
        db_server[user_name] = {"loans": []}
    loans_list = db_server[user_name]["loans"]

# Считаем сумму активных долгов пользователя
total_active_credit = sum(loan.get("amount", 0) for loan in loans_list)

# Синхронизируем данные с админкой
if user_name:
    global_db[user_name] = {
        "balance": st.session_state.get("b", 1000),
        "credit_limit": st.session_state.get("n", 60000),
        "credit_taken": total_active_credit
    }

procen = {
    "Январь": 31, "Февраль": 28, "Март": 31, "Апрель": 30, "Май": 31, "Июнь": 30,
    "Июль": 31, "Август": 31, "Сентябрь": 30, "Октябрь": 31, "Ноябрь": 30, "Декабрь": 31
}

month_to_num = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
    "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
}

st.title("Кредит")

# Показываем список текущих взятых кредитов пользователя, если они есть
if loans_list:
    st.subheader("📋 Ваши активные кредиты:")
    for loan in loans_list:
        st.info(f"**{loan['name_kredite']}**: {loan['amount']} ₽ (Вернуть: {loan['repayment']} ₽ до {loan['date_end']})")

bank_balance = db_server["bank_balance"]
st.warning(f"Доступно в банке: {bank_balance} ₽")
kredit = st.number_input("Выберете сумму кредита", min_value=300, max_value=60000)
st.write(" ")

col1, col2 = st.columns(2)
with col1:
    month = st.selectbox("Выбери месяц начала кредита", list(procen.keys()))
with col2:
    max_days = procen[month]
    days = st.selectbox("Выбери день начала кредита", list(range(1, max_days + 1)))

st.write(" ")

col3, col4 = st.columns(2)
with col3:
    month_finish = st.selectbox("Выбери месяц конца кредита", list(procen.keys()))
with col4:
    max_days_finish = procen[month_finish]
    days_finish = st.selectbox("Выбери день конца кредита", list(range(1, max_days_finish + 1)))

st.title(f"{month}, {days} ------ {month_finish}, {days_finish}")

d_start = date(2026, month_to_num[month], days)
d_end = date(2026, month_to_num[month_finish], days_finish)

delta = d_end - d_start
loan_days = delta.days

if loan_days <= 0:
    st.error("Ошибка: Дата конца должна быть позже даты начала!")
else:
    base_rate = 0.05
    total_interest = kredit * (base_rate / 30) * loan_days
    st.metric(label="Переплата", value=f"{round(total_interest, 2)} ₽")
    
    @st.dialog("Кредитный договор")
    def show_popup():
        new_loan = st.text_input("введите название кредита")
        st.write("Проставьте все галочки для подтверждения:")
        c1 = st.checkbox("я обязуюсь оплатить кредит с комиссией")
        c2 = st.checkbox("я оставляю под залог")
        c3 = st.checkbox("согласен на изъятие залога при неуплате")
        c4 = st.checkbox("согласен на срок 1 месяц для закрытия")
        c5 = st.checkbox("согласен на начисление штрафных процентов")
        
        if st.button("Подтвердить и взять кредит"):
            if all([c1, c2, c3, c4, c5]) and user_name:
                if db_server["bank_balance"] >= kredit:
                    # 1. Снимаем деньги из банка
                    db_server["bank_balance"] -= kredit
                    
                    # 2. Формируем данные кредита
                    loan_details = {
                        "name_kredite": new_loan,
                        "amount": kredit,
                        "date_start": str(d_start),
                        "date_end": str(d_end),
                        "repayment": round(kredit + total_interest, 2)
                    }

                    # 3. Записываем в базу данных сервера
                    db_server[user_name]["loans"].append(loan_details)
                    db_server.sync()  # Принудительно сохраняем на диск

                    # 4. Моментально обновляем данные для админа
                    global_db[user_name] = {
                        "balance": st.session_state.get("b", 1000),
                        "credit_limit": st.session_state.get("n", 60000),
                        "credit_taken": sum(l.get("amount", 0) for l in db_server[user_name]["loans"])
                    }

                    st.success(f"Кредит на {kredit} ₽ оформлен!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("В банке недостаточно средств!")
            elif not user_name:
                st.error("Ошибка: вы не авторизованы!")
            else:
                st.warning("Нужно отметить все пункты!")

    if st.button("Оформить кредит"):
        show_popup()

db_server.close()
