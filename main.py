import streamlit as st
import time
import json
import os
import extra_streamlit_components as stx
from streamlit_gsheets import GSheetsConnection
import extra_streamlit_components as stx
conn = st.connection("gsheets", type=GSheetsConnection)
cookie_manager = stx.CookieManager(key="main_cookie_manager")

# 2. Получаем имя и сохраняем его в session_state, чтобы другие страницы его видели
user_name = cookie_manager.get(cookie="user_name")
if user_name:
    st.session_state.user_name = user_name

# Навигация
pg_reg = st.Page("project.py", title="Регистрация")
pg_home = st.Page("page_2.py", title="Главная")
pg_kredits = st.Page("kredits.py", title="Кредиты")

pg = st.navigation([pg_reg, pg_home, pg_kredits])
pg.run()





