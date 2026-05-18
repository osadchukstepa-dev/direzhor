import streamlit as st
import extra_streamlit_components as stx
import json
import os

# --- ГЛОБАЛЬНАЯ БАЗА ДЛЯ АДМИНА ---
@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

DB_FILE_1 = "users_stats.json"

def load_db():
    if os.path.exists(DB_FILE_1):
        with open(DB_FILE_1, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE_1, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

db = load_db()
cookie_manager = stx.CookieManager(key="auth_cookie_manager")

# Получаем имя пользователя из куки
user_name = cookie_manager.get(cookie="user_name")

# Если кука есть в браузере, автоматически авторизуем пользователя
if user_name:
    st.session_state.nickname = user_name
    
    # Передаем актуальные данные админу в оперативную память
    global_db[user_name] = {
        "balance": st.session_state.get("b", 1000),
        "credit_limit": st.session_state.get("n", 60000),
        "credit_taken": st.session_state.get("credit_taken", 0)
    }
    st.success(f"Вы вошли как: **{user_name}**")

# Если куки нет, показываем форму ввода
else:
    st.subheader("📝 Вход или Регистрация")
    nickname = st.text_input("Как тебя зовут?").strip()
    password = st.number_input("Введите пароль", value=0, step=1)
    
    if st.button("Войти / Создать аккаунт"):
        if nickname:
            # Если пользователя нет в базе — регистрируем его
            if nickname not in db:
                db[nickname] = {"password": password}
                save_db(db)
                st.info("Создан новый аккаунт!")
            
            # Если пользователь уже был, проверяем его пароль
            elif db[nickname]["password"] != password:
                st.error("Неверный пароль!")
                st.stop()
            
            # Сохраняем имя в текущую сессию
            st.session_state.nickname = nickname

            # Отправляем данные админу
            global_db[nickname] = {
                "balance": st.session_state.get("b", 1000),
                "credit_limit": st.session_state.get("n", 60000),
                "credit_taken": st.session_state.get("credit_taken", 0)
            }

            # Сохраняем куку в браузер
            cookie_manager.set("user_name", nickname, key="save_user_cookie")
            st.success("Успешный вход! Пожалуйста, перейдите на вкладку 'Главная'.")
        else:
            st.error("Пожалуйста, введите имя!")
