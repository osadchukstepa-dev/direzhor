import streamlit as st
import extra_streamlit_components as stx
import json
import os
from streamlit_gsheets import GSheetsConnection
import extra_streamlit_components as stx

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0) # Загрузка базы в начале каждого файла

cookie_manager = stx.CookieManager()
cookie_manager = stx.CookieManager(key="cookie_loan") # Определение юзера в каждом файле


DB_FILE_1 = "users_stats.json"

def load_db():
    if os.path.exists(DB_FILE_1):
        with open(DB_FILE_1, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE_1, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()
cookie_manager = stx.CookieManager()

# 1. Читаем куки
user_name = cookie_manager.get(cookie="user_name")

if user_name:

    if user_name in db:
        user_data = db[user_name]

else:
    # 2. Регистрация, если куки нет
    nickname = st.text_input("Как тебя зовут?")
    password = st.number_input("Введите пароль", value=0, step=1)
    
    if st.button("Войти или Создать аккаунт"):
        if nickname:
            # Если человека нет в базе — создаем
            if nickname not in db:
                db[nickname] = {
                    "password": password,
                }
                save_db(db)
                st.success("Новый аккаунт создан!")

            # Сохраняем куку
            cookie_manager.set("user_name", nickname, key="set_name")
            st.success("Готово! Обновите страницу.")
        else:
            st.error("Введите имя!")



