import streamlit as st
import extra_streamlit_components as stx
import time
from datetime import date
import json
import os
from project import *

# --- ПОДКЛЮЧЕНИЕ ГЛОБАЛЬНОЙ БАЗЫ ДЛЯ АДМИНА ---
@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

kredits_cookies = cookie_manager.get(cookie="kredits_cookies")

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

cookie_manager = stx.CookieManager()

def load_db():
    if os.path.exists("users_stats.json"):
        with open("users_stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open("users_stats.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

db = load_db()
user_name = cookie_manager.get(cookie="user_name")

# Синхронизируем состояние пользователя с глобальной базой, если он зашел на страницу
if user_name:
    # Считаем общую сумму всех активных кредитов пользователя из базы JSON
    user_loans = db.get(user_name, {}).get("loans", [])
    total_active_credit = sum(loan.get("amount", 0) for loan in user_loans)
    
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
st.warning(f"Доступно в банке: {balance} ₽")
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
                if data["balance"] >= kredit:
                    # 1. Снимаем деньги из банка
                    data["balance"] -= kredit
                    save_data(data)
                    
                    # 2. Формируем данные кредита
                    loan_details = {
                        "name_kredite": new_loan,
                        "amount": kredit,
                        "date_start": str(d_start),
                        "date_end": str(d_end),
                        "repayment": round(kredit + total_interest, 2)
                    }

                    # 3. Сохраняем в JSON базу (users_stats.json)
                    if user_name not in db:
                        db[user_name] = {"password": 0}
                    
                    if "loans" not in db[user_name]:
                        db[user_name]["loans"] = []
                    
                    db[user_name]["loans"].append(loan_details)
                    save_db(db)

                    # 4. ОБНОВЛЯЕМ ОПЕРАТИВНУЮ ПАМЯТЬ ДЛЯ АДМИНА
                    user_loans = db[user_name].get("loans", [])
                    total_active_credit = sum(l.get("amount", 0) for l in user_loans)
                    
                    global_db[user_name] = {
                        "balance": st.session_state.get("b", 1000),
                        "credit_limit": st.session_state.get("n", 60000),
                        "credit_taken": total_active_credit
                    }

                    # 5. Сохраняем в КУКИ
                    current_kredits = cookie_manager.get(cookie="kredits_cookies")
                    if isinstance(current_kredits, str):
                        try:
                            loans_list = json.loads(current_kredits)
                        except:
                            loans_list = []
                    else:
                        loans_list = current_kredits if current_kredits else []

                    loans_list.append(loan_details)
                    cookie_manager.set("kredits_cookies", loans_list, key="save_loans_cookie")

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
