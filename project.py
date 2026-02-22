import streamlit as st
import streamlit as st
import extra_streamlit_components as stx
import json
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Подключаемся к Google Sheets (Облако)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_cloud_data():
    return conn.read(ttl=0).dropna(how="all")

def save_cloud_data(updated_df):
    conn.update(data=updated_df)
    st.cache_data.clear()

# Загружаем таблицу пользователей из облака
df = load_cloud_data()

# 2. Инициализируем куки с УНИКАЛЬНЫМ ключом для этого файла
cookie_manager = stx.CookieManager(key="cookie_project_page")

# !!! ВАЖНО: Получаем имя пользователя из куки, иначе будет ошибка NameError !!!
user_name = cookie_manager.get(cookie="user_name")

st.title("Личный кабинет")

if user_name:
    # Ищем пользователя в облачной таблице (df)
    user_row = df[df['name'] == user_name]
    
    if not user_row.empty:
        st.write(f"С возвращением, **{user_name}**!")
        # Тут можно выводить баланс или кредиты из таблицы
        st.write(f"Ваш баланс: {user_row.iloc[0]['balance']} ₽")
    else:
        st.warning("Вы в системе, но данных в облаке нет. Перезайдите.")
        if st.button("Выйти"):
            cookie_manager.delete("user_name", key="delete_user")
            st.rerun()

else:
    # 3. Регистрация/Вход (теперь сохраняем в Google Sheets, а не в JSON)
    st.subheader("Авторизация")
    nickname = st.text_input("Как тебя зовут?", key="reg_name")
    password = st.number_input("Введите пароль", value=0, step=1, key="reg_pass")
    
    if st.button("Войти или Создать аккаунт", key="reg_btn"):
        if nickname:
            # Проверяем, есть ли человек в ОБЛАЧНОЙ таблице
            if nickname not in df['name'].values:
                # Создаем новую строку для таблицы
                new_user = pd.DataFrame([{
                    "name": nickname,
                    "password": password,
                    "balance": 60000,
                    "loans": "[]"
                }])
                # Объединяем старую таблицу с новым юзером
                df = pd.concat([df, new_user], ignore_index=True)
                # Сохраняем В ОБЛАКО (Google Sheets)
                save_cloud_data(df)
                st.success(f"Аккаунт {nickname} создан в облаке!")
            else:
                st.info("Вход в существующий аккаунт...")

            # Устанавливаем куку
            cookie_manager.set("user_name", nickname, key="set_cookie_name")
            st.info("Нажми еще раз или обнови страницу.")
        else:
            st.error("Введите имя!")
