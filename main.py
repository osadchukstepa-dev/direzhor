import streamlit as st
import time
import json
import os
import extra_streamlit_components as stx

# СОЗДАЕМ ГЛОБАЛЬНУЮ ПАМЯТЬ, СОВМЕСТИМУЮ С GITHUB (вместо JSON)
@st.cache_resource
def get_global_db():
    return {}  # Здесь будут храниться сессии всех пользователей в сети

global_db = get_global_db()

# Стандартная инициализация сессии текущего пользователя
if 'n' not in st.session_state:
    st.session_state.n = 60000  # Лимит кредита
if 'b' not in st.session_state:
    st.session_state.b = 1000   # Баланс
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "credit_taken" not in st.session_state:
    st.session_state.credit_taken = 0  # Сюда должен записываться ваш кредит!

# Синхронизация текущего пользователя с глобальной базой "В сети"
if st.session_state.nickname:
    global_db[st.session_state.nickname] = {
        "balance": st.session_state.b,
        "credit_limit": st.session_state.n,
        "credit_taken": st.session_state.credit_taken
    }

# Инициализация флага авторизации админа
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

pg_reg = st.Page("project.py", title="Регистрация")
pg_home = st.Page("page_2.py", title="Главная")
pg_kredits = st.Page("kredits.py", title="Кредиты")

pages_list = [pg_reg, pg_home, pg_kredits]

with st.sidebar:
    st.markdown("---")
    if not st.session_state.is_admin:
        admin_code = st.text_input("Вход для админа (код)", type="password")
        if st.button("Войти как админ"):
            if admin_code == "1234":
                st.session_state.is_admin = True
                st.success("Доступ разрешен!")
                st.rerun()
            else:
                st.error("Неверный код!")
    else:
        st.write("Вы вошли как Администратор")
        if st.button("Выйти из админки"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.is_admin:
    pg_admin = st.Page("admin.py", title="Админ-панель")
    pages_list.append(pg_admin)

pg = st.navigation(pages_list)
pg.run()
