import streamlit as st
import extra_streamlit_components as stx
from streamlit_gsheets import GSheetsConnection

# Подключение к таблице
conn = st.connection("gsheets", type=GSheetsConnection)

# ОСТАВЬ ТОЛЬКО ОДНУ СТРОКУ СОЗДАНИЯ МЕНЕДЖЕРА!
cookie_manager = stx.CookieManager(key="very_new_unique_key_123")

# Получаем имя и передаем в другие файлы через session_state
user_name = cookie_manager.get(cookie="user_name")
st.session_state["user_name"] = user_name
st.session_state["cookie_manager"] = cookie_manager

# Навигация
pg_reg = st.Page("project.py", title="Регистрация")
pg_home = st.Page("page_2.py", title="Главная")
pg_kredits = st.Page("kredits.py", title="Кредиты")

pg = st.navigation([pg_reg, pg_home, pg_kredits])
pg.run()






