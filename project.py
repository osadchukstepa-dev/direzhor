import streamlit as st
import extra_streamlit_components as stx
import json
import os

# --- ПОДКЛЮЧЕНИЕ ГЛОБАЛЬНОЙ БАЗЫ ДЛЯ АДМИНА ---
@st.cache_resource
def get_global_db():
    return {}  # Эта память живет на сервере GitHub и видна админу

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
cookie_manager = stx.CookieManager()

# 1. Читаем куки
user_name = cookie_manager.get(cookie="user_name")

if user_name:
    st.session_state.nickname = user_name
    
    # Если пользователь зашел по кукам, синхронизируем его с админкой
    if user_name in db:
        user_data = db[user_name]
        
    # Отправляем актуальные данные в глобальную память для админа
    global_db[user_name] = {
        "balance": st.session_state.get("b", 1000),
        "credit_limit": st.session_state.get("n", 60000),
        "credit_taken": st.session_state.get("credit_taken", 0)
    }
    
    st.success(f"Привет, {user_name}! Вы успешно авторизованы.")

else:
    # 2. Регистрация, если куки нет
    st.subheader("📝 Авторизация в системе")
    nickname = st.text_input("Как тебя зовут?").strip()
    password = st.number_input("Введите пароль", value=0, step=1)
    
    if st.button("Войти или Создать аккаунт"):
        if nickname:
            # Если человека нет в базе — создаем дефолтные значения
            if nickname not in db:
                db[nickname] = {
                    "password": password
                }
                save_db(db)
                st.success("Новый аккаунт создан!")
            else:
                # Если человек есть, проверяем пароль
                if db[nickname]["password"] != password:
                    st.error("Неверный пароль для этого аккаунта!")
                    st.stop()

            # Сохраняем в локальную сессию
            st.session_state.nickname = nickname

            # Передаем данные в глобальную память (чтобы админ сразу увидел)
            global_db[nickname] = {
                "balance": st.session_state.get("b", 1000),
                "credit_limit": st.session_state.get("n", 60000),
                "credit_taken": st.session_state.get("credit_taken", 0)
            }

            # Сохраняем куку
            cookie_manager.set("user_name", nickname, key="set_name")
            st.success("Готово! Обновите страницу для применения изменений.")
            st.rerun()
        else:
            st.error("Введите имя!")
