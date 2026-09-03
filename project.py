import streamlit as st
import shelve


DB_FILE = "server_bank_db"


# -----------------------------
# БАЗА ДАННЫХ
# -----------------------------
def open_db():
    return shelve.open(DB_FILE, writeback=True)


# -----------------------------
# ГЛОБАЛЬНАЯ БАЗА ДЛЯ АДМИНА
# -----------------------------
@st.cache_resource
def get_global_db():
    return {}


global_db = get_global_db()


# -----------------------------
# СОЗДАЁМ SESSION STATE
# -----------------------------
if "nickname" not in st.session_state:
    st.session_state.nickname = ""

if "b" not in st.session_state:
    st.session_state.b = 1000

if "n" not in st.session_state:
    st.session_state.n = 60000

if "credit_taken" not in st.session_state:
    st.session_state.credit_taken = 0


# -----------------------------
# ЕСЛИ УЖЕ ВОШЛИ
# -----------------------------
if st.session_state.nickname:
    st.success(
        f"Вы вошли как: **{st.session_state.nickname}**"
    )

    if st.button("Выйти"):
        st.session_state.nickname = ""
        st.session_state.b = 1000
        st.session_state.n = 60000
        st.session_state.credit_taken = 0
        st.rerun()

    st.stop()


# -----------------------------
# РЕГИСТРАЦИЯ / ВХОД
# -----------------------------
st.title("📝 Вход или регистрация")

nickname = st.text_input(
    "Введите имя пользователя"
).strip()

password = st.text_input(
    "Введите пароль",
    type="password"
)


if st.button("Войти / Создать аккаунт", type="primary"):

    if not nickname:
        st.error("Введите имя пользователя!")
        st.stop()

    if not password:
        st.error("Введите пароль!")
        st.stop()

    db = open_db()

    try:
        # -----------------------------
        # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
        # -----------------------------
        if nickname not in db:

            db[nickname] = {
                "password": password,
                "balance": 1000.0,
                "credit_limit": 60000.0,
                "loans": [],
                "lines_ticket": None
            }

            db.sync()

            st.session_state.nickname = nickname
            st.session_state.b = 1000.0
            st.session_state.n = 60000.0
            st.session_state.credit_taken = 0

            global_db[nickname] = {
                "balance": 1000.0,
                "credit_limit": 60000.0,
                "credit_taken": 0
            }

            st.success("Аккаунт создан! Баланс: 1000 ₽")
            st.rerun()

        # -----------------------------
        # СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ
        # -----------------------------
        else:

            user_data = db[nickname]

            if str(user_data.get("password", "")) != password:
                st.error("Неверный пароль!")
                st.stop()

            # Старым пользователям добавляем недостающие поля
            if "balance" not in user_data:
                user_data["balance"] = 1000.0

            if "credit_limit" not in user_data:
                user_data["credit_limit"] = 60000.0

            if "loans" not in user_data:
                user_data["loans"] = []

            if "lines_ticket" not in user_data:
                user_data["lines_ticket"] = None

            db[nickname] = user_data
            db.sync()

            # Загружаем данные пользователя
            balance = float(user_data.get("balance", 1000.0))
            credit_limit = float(
                user_data.get("credit_limit", 60000.0)
            )

            loans = user_data.get("loans", [])

            credit_taken = sum(
                float(loan.get("amount", 0))
                for loan in loans
            )

            st.session_state.nickname = nickname
            st.session_state.b = balance
            st.session_state.n = credit_limit
            st.session_state.credit_taken = credit_taken

            global_db[nickname] = {
                "balance": balance,
                "credit_limit": credit_limit,
                "credit_taken": credit_taken
            }

            st.success("Успешный вход!")
            st.rerun()

    finally:
        db.close()
