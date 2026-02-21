import streamlit as st
import extra_streamlit_components as stx
import time
from datetime  import date
import json
import os
from project import *
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) # Загрузка базы в начале каждого файла

cookie_manager = stx.CookieManager()
user_name = cookie_manager.get(cookie="user_name") # Определение юзера в каждом файле



DB_FILE_1 = "data.json"
def load_data():
    if not os.path.exists(DB_FILE_1):
        # Начальные данные, если файла еще нет
        initial_data = {"balance": 60000}
        with open(DB_FILE_1, "w") as f:
            json.dump(initial_data, f)
        return initial_data
    
    with open(DB_FILE_1, "r") as f:
        return json.load(f)

# Функция для сохранения данных
def save_data(data):
    with open(DB_FILE_1, "w") as f:
        json.dump(data, f, indent=4)


# Загружаем актуальное состояние
data = load_data()
balance = data["balance"]



cookie_manager = stx.CookieManager()

# Нужно также загрузить базу пользователей, чтобы было куда записывать кредит
def load_db():
    if os.path.exists("users_stats.json"): # Убедись, что имя файла совпадает с тем, где юзеры
        with open("users_stats.json", "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open("users_stats.json", "w") as f:
        json.dump(data, f, indent=4)

db = load_db()
user_name = cookie_manager.get(cookie="user_name")


procen = {
    "Январь": 31,
    "Февраль": 28, # В високосный год 29
    "Март": 31,
    "Апрель": 30,
    "Май": 31,
    "Июнь": 30,  # Исправил порядок и дни
    "Июль": 31,
    "Август": 31,
    "Сентябрь": 30, # Добавил значение (было пусто)
    "Октябрь": 31,
    "Ноябрь": 30,
    "Декабрь": 31
}

month_to_num = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
    "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
}

st.title("Кредит")

st.warning(f"Доступно {balance}")
kredit = st.number_input("Выберете сумму кредита", min_value=300, max_value=60000)
st.write(" ")

col1, col2  = st.columns(2)

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
        st.write("Проставьте все галочки для подтверждения:")
        c1 = st.checkbox("я обязуюсь оплатить кредит с комиссией")
        c2 = st.checkbox("я оставляю под залог")
        c3 = st.checkbox("согласен на изъятие залога при неуплате")
        c4 = st.checkbox("согласен на срок 1 месяц для закрытия")
        c5 = st.checkbox("согласен на начисление штрафных процентов")
        
        if st.button("Подтвердить и взять кредит"):
            # Проверяем, все ли галочки стоят и авторизован ли юзер
            if all([c1, c2, c3, c4, c5]) and user_name:
                if data["balance"] >= kredit:
                    # 1. Снимаем деньги из банка
                    data["balance"] -= kredit
                    save_data(data)
                    
                    
                    if user_name in db:
                        
                        if "loans" not in db[user_name]:
                            db[user_name]["loans"] = []
                        
                        # Добавляем данные о новом кредите
                        new_loan = {
                            "amount": kredit,
                            "date_start": str(d_start),
                            "date_end": str(d_end),
                            "days": loan_days,
                            "repayment": round(kredit + total_interest, 2)
                        }
                        db[user_name]["loans"].append(new_loan)
                        

                        save_db(db)
                        
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

    

