import streamlit as st
import time
import json
import os
import extra_streamlit_components as stx



if 'n' not in st.session_state:
    st.session_state.n = 60000  # Лимит кредита
if 'b' not in st.session_state:
    st.session_state.b = 1000   # Баланс
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
pg_reg = st.Page("project.py", title="Регистрация")
pg_home = st.Page("page_2.py", title="Главная")
pg_kredits = st.Page("kredits.py", title="Кредиты")

pg = st.navigation([pg_reg, pg_home, pg_kredits])

pg.run()
