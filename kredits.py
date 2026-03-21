import streamlit as st
import extra_streamlit_components as stx
import json
import time
import os  # Добавили импорт!
from datetime import date, datetime, timedelta

# 1. Менеджер создается ТОЛЬКО ОДИН РАЗ в самом верху
if 'cookie_manager' not in st.session_state:
    st.session_state.cookie_manager = stx.CookieManager(key="bank_mngr")

cookie_manager = st.session_state.cookie_manager

# Файловые функции
DB_FILE_1 = "data.json"
def load_data():
    if not os.path.exists(DB_FILE_1):
        initial_data = {"balance": 60000}
        with open(DB_FILE_1, "w") as f:
            json.dump(initial_data, f)
        return initial_data
    with open(DB_FILE_1, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE_1, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
balance = data["balance"]

# Получаем данные пользователя
user_name = cookie_manager.get(cookie="user_name")

procen = {
    "Январь": 31, "Февраль": 28, "Март": 31, "Апрель": 30, "Май": 31, "Июнь": 30,
    "Июль": 31, "Август": 31, "Сентябрь": 30, "Октябрь": 31, "Ноябрь": 30, "Декабрь": 31
}

month_to_num = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
    "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
}

st.title("Кредит")
st.warning(f"Доступно {balance}")

kredit = st.number_input("Выберете сумму кредита", min_value=300, max_value=60000)

col1, col2 = st.columns(2)
with col1:
    month = st.selectbox("Выбери месяц начала", list(procen.keys()))
with col2:
    days = st.selectbox("Выбери день начала", list(range(1, procen[month] + 1)))

col3, col4 = st.columns(2)
with col3:
    month_finish = st.selectbox("Выбери месяц конца", list(procen.keys()))
with col4:
    days_finish = st.selectbox("Выбери день конца", list(range(1, procen[month_finish] + 1)))

d_start = date(2026, month_to_num[month], days)
d_end = date(2026, month_to_num[month_finish], days_finish)
delta = d_end - d_start
loan_days = delta.days

if loan_days <= 0:
    st.error("Ошибка: Дата конца должна быть позже даты начала!")
else:
    total_interest = kredit * (0.05 / 30) * loan_days
    st.metric(label="Переплата", value=f"{round(total_interest, 2)} ₽")
    
    @st.dialog("Кредитный договор")
    def show_popup():
        new_loan = st.text_input("Введите название кредита")
        c1 = st.checkbox("Обязуюсь оплатить")
        c2 = st.checkbox("Оставляю залог")
        c3 = st.checkbox("Согласен на изъятие")
        c4 = st.checkbox("Срок 1 месяц")
        c5 = st.checkbox("Согласен на штрафы")
        
        if st.button("Подтвердить и взять кредит"):
            if all([c1, c2, c3, c4, c5]) and user_name:
                # Читаем старые куки
                current_raw = cookie_manager.get(cookie="kredits_cookies")
                
                try:
                    if current_raw:
                        loans_list = json.loads(current_raw) if isinstance(current_raw, str) else current_raw
                    else:
                        loans_list = []
                except:
                    loans_list = []

                # Добавляем новый
                new_entry = {
                    "name": new_loan if new_loan else "Без названия",
                    "amount": kredit,
                    "date_end": str(d_end),
                    "repayment": round(kredit + total_interest, 2),
                    "stats": "+"
                }
                loans_list.append(new_entry)

                # Сохраняем
                cookie_manager.set(
                    "kredits_cookies", 
                    json.dumps(loans_list), 
                    key=f"save_{time.time()}"
                )
                
                # Уменьшаем баланс в файле (банка)
                data["balance"] -= kredit
                save_data(data)
                
                st.success("Готово!")
                time.sleep(2)
                st.rerun()
            elif not user_name:
                st.error("Войдите в аккаунт!")
            else:
                st.warning("Отметьте все пункты!")

    if st.button("Оформить кредит"):
        show_popup()
