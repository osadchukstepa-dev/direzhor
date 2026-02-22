import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Подключение к базе
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

def save_cloud_data(updated_df):
    conn.update(data=updated_df)
    st.cache_data.clear()

# 2. ЗАБИРАЕМ данные из "общего ящика" (session_state)
user_name = st.session_state.get("user_name")
cookie_manager = st.session_state.get("cookie_manager")

st.title("Личный кабинет")

# Если пользователь авторизован
if user_name:
    user_row = df[df['name'] == user_name]
    
    if not user_row.empty:
        st.write(f"С возвращением, **{user_name}**!")
        # Исправил вывод баланса (используем .iloc[0])
        st.write(f"Ваш баланс: {user_row.iloc[0]['balance']} ₽")
    else:
        st.warning("Аккаунт не найден в таблице.")
        if st.button("Выйти"):
            cookie_manager.delete("user_name") # Работает, т.к. мы взяли его из session_state
            st.rerun()

else:
    # 3. Регистрация
    st.subheader("Авторизация")
    nickname = st.text_input("Как тебя зовут?", key="reg_name")
    password = st.number_input("Введите пароль", value=0, step=1, key="reg_pass")
    
    if st.button("Войти или Создать аккаунт", key="reg_btn"):
        if nickname:
            if nickname not in df['name'].values:
                new_user = pd.DataFrame([{
                    "name": nickname, "password": password, "balance": 60000, "loans": "[]"
                }])
                df = pd.concat([df, new_user], ignore_index=True)
                save_cloud_data(df)
                st.success(f"Аккаунт {nickname} создан!")
            
            # Сохраняем куку через менеджер из main.py
            cookie_manager.set("user_name", nickname, key="save_user_cookie")
            st.info("Готово! Переключите страницу или обновите её.")
        else:
            st.error("Введите имя!")
