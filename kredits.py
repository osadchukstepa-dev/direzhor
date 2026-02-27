import streamlit as st
import extra_streamlit_components as stx
import time
from datetime import date
import json
import os
import base64
from github import Github # Не забудь добавить PyGithub в requirements.txt

# --- НАСТРОЙКИ GITHUB (Берутся из Secrets) ---
token = st.secrets["GITHUB_TOKEN"]
repo_name = st.secrets["REPO_NAME"] 

g = Github(token)
repo = g.get_repo(repo_name)

# --- ФУНКЦИИ БАЗЫ ДАННЫХ (Теперь через GitHub) ---

def load_db():
    try:
        contents = repo.get_contents("users_stats.json")
        return json.loads(base64.b64decode(contents.content).decode('utf-8'))
    except:
        return {}

def save_db(data_to_save):
    contents = repo.get_contents("users_stats.json")
    new_json = json.dumps(data_to_save, indent=4, ensure_ascii=False)
    repo.update_file(contents.path, "Update loans", new_json, contents.sha)

# Функции для баланса банка (data.json) - тоже через GitHub
def load_data():
    try:
        contents = repo.get_contents("data.json")
        return json.loads(base64.b64decode(contents.content).decode('utf-8'))
    except:
        return {"balance": 60000}

def save_data(data_to_save):
    contents = repo.get_contents("data.json")
    new_json = json.dumps(data_to_save, indent=4, ensure_ascii=False)
    repo.update_file(contents.path, "Update bank balance", new_json, contents.sha)

# --- ТВОЯ ЛОГИКА (БЕЗ ИЗМЕНЕНИЙ) ---

data = load_data()
balance = data["balance"]
db = load_db()

cookie_manager = stx.CookieManager()
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

st.title(f"{month}, {days} --- {month_finish}, {days_finish}")

d_start = date(2026, month_to_num[month], days)
d_end = date(2026, month_to_num[month_finish], days_finish)
delta = d_end - d_start
loan_days = delta.days

if loan_days <= 0:
    st.error("Ошибка даты!")
else:
    base_rate = 0.05
    total_interest = kredit * (base_rate / 30) * loan_days
    st.metric(label="Переплата", value=f"{round(total_interest, 2)} ₽")
    
    @st.dialog("Кредитный договор")
    def show_popup():
        loan_title = st.text_input("Название кредита")
        c1 = st.checkbox("обязуюсь оплатить")
        c2 = st.checkbox("оставляю залог")
        c3 = st.checkbox("согласен на изъятие")
        c4 = st.checkbox("срок 1 месяц")
        c5 = st.checkbox("согласен на штрафы")
        
        if st.button("Подтвердить"):
            if all([c1, c2, c3, c4, c5]) and user_name:
                if data["balance"] >= kredit:
                    data["balance"] -= kredit
                    save_data(data) # Сохранит на GitHub
                    
                    if user_name in db:
                        if "loans" not in db[user_name]:
                            db[user_name]["loans"] = []
                        
                        db[user_name]["loans"].append({
                            "name kredite": loan_title,
                            "amount": kredit,
                            "date_start": str(d_start),
                            "date_end": str(d_end),
                            "days": loan_days,
                            "repayment": round(kredit + total_interest, 2),
                            "stats": "_"
                        })
                        save_db(db) # Сохранит на GitHub
                        
                    st.success(f"Кредит на {kredit} ₽ оформлен!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("В банке нет денег!")
            else:
                st.warning("Заполните всё!")

    if st.button("Оформить кредит"):
        show_popup()
