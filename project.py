import streamlit as st
import extra_streamlit_components as stx

# Инициализируем менеджер куки
cookie_manager = stx.CookieManager()



# 1. Читаем куки (например, имя пользователя)
user_name = cookie_manager.get(cookie="user_name")

if user_name:
    st.write(f"С возвращением, {user_name}!")
else:
    # 2. Записываем куки, если их нет
    st.session_state.nickname = st.text_input("Как тебя зовут?")
    if st.button("Сохранить в куки"):
        cookie_manager.set("user_name", st.session_state.nickname, key="set_name")
        st.success("Имя сохранено! Обнови страницу.")
