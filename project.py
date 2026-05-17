import streamlit as st

# 1. Подключаем глобальную память прямо на странице регистрации
@st.cache_resource
def get_global_db():
    return {}

global_db = get_global_db()

# ... ваш существующий код ввода никнейма ...
# Допустим, у вас есть кнопка входа:
if st.button("Войти"):
    if nickname_input: # если никнейм введен
        st.session_state.nickname = nickname_input
        
        # 2. Обязательно записываем пользователя в глобальную базу!
        global_db[st.session_state.nickname] = {
            "balance": st.session_state.get("b", 1000),
            "credit_limit": st.session_state.get("n", 60000),
            "credit_taken": st.session_state.get("credit_taken", 0)
        }
        st.success("Вы успешно вошли!")
