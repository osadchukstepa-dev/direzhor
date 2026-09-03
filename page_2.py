import streamlit as st
import shelve


# =========================================================
# НАСТРОЙКИ
# =========================================================

DB_FILE = "server_bank_db"


# =========================================================
# ПОЛЬЗОВАТЕЛЬ
# =========================================================

username = st.session_state.get("nickname", "").strip()


# =========================================================
# ЕСЛИ НЕ АВТОРИЗОВАН
# =========================================================

st.title("🏠 Rasino")

if not username:
    st.warning(
        "У вас нет аккаунта. "
        "Перейдите во вкладку «Регистрация» и войдите."
    )

    if st.button("👤 Перейти к регистрации", type="primary"):
        st.switch_page("project.py")

    st.stop()


# =========================================================
# ОТКРЫВАЕМ БАЗУ
# =========================================================

db = shelve.open(DB_FILE, writeback=True)

try:

    # Если пользователя почему-то нет в базе
    if username not in db:
        db[username] = {
            "password": "",
            "balance": 1000.0,
            "credit_limit": 60000.0,
            "loans": [],
            "lines_ticket": None,
        }

        db.sync()


    user_data = db[username]


    # =====================================================
    # ЗАЩИТА ОТ СТАРЫХ ДАННЫХ
    # =====================================================

    if "balance" not in user_data:
        user_data["balance"] = 1000.0

    if "loans" not in user_data:
        user_data["loans"] = []

    if "lines_ticket" not in user_data:
        user_data["lines_ticket"] = None


    db[username] = user_data
    db.sync()


    # =====================================================
    # ПОЛУЧАЕМ ДАННЫЕ
    # =====================================================

    balance = float(
        user_data.get("balance", 1000.0)
    )

    loans = user_data.get("loans", [])

    st.session_state.b = balance


    # =====================================================
    # КРЕДИТНАЯ ИСТОРИЯ
    # =====================================================

    plus = 0
    minus = 0

    for loan in loans:

        stats = loan.get("stats")

        if stats == "+":
            plus += 1

        elif stats == "-":
            minus += 1


    if plus > minus:
        credit_history = "Хорошая"
    elif plus == minus:
        credit_history = "Сомнительная"
    else:
        credit_history = "Плохая"


    # =====================================================
    # ВКЛАДКИ
    # =====================================================

    account_tab, credits_tab = st.tabs(
        ["👤 Аккаунт", "💳 Кредиты"]
    )


    # =====================================================
    # АККАУНТ
    # =====================================================

    with account_tab:

        st.title(f"Привет, {username} 👋")

        st.metric(
            "💰 Ваш баланс",
            f"{balance:,.2f} ₽".replace(",", " ")
        )

        st.write("Вы вошли как:")
        st.info(username)

        st.divider()

        # ---------------------------------------------
        # БЫСТРЫЕ КНОПКИ
        # ---------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💳 Перейти к кредитам",
                use_container_width=True,
            ):
                st.switch_page("kredits.py")

        with col2:

            if st.button(
                "〰️ Перейти в Lines",
                use_container_width=True,
            ):
                st.switch_page("lines.py")


        st.divider()

        # ---------------------------------------------
        # ВЫХОД
        # ---------------------------------------------

        st.subheader("🚪 Выход")

        if st.button(
            "Выйти из аккаунта",
            use_container_width=True,
        ):

            st.session_state.nickname = ""
            st.session_state.b = 1000.0
            st.session_state.n = 60000.0
            st.session_state.credit_taken = 0.0

            st.rerun()


    # =====================================================
    # КРЕДИТЫ
    # =====================================================

    with credits_tab:

        st.subheader("📋 Ваши кредиты")

        # ---------------------------------------------
        # КРЕДИТНАЯ ИСТОРИЯ
        # ---------------------------------------------

        st.write("Кредитная история:")

        if credit_history == "Хорошая":

            st.success(
                f"🟢 {credit_history}"
            )

        elif credit_history == "Сомнительная":

            st.warning(
                f"🟠 {credit_history}"
            )

        else:

            st.error(
                f"🔴 {credit_history}"
            )


        # ---------------------------------------------
        # СПИСОК КРЕДИТОВ
        # ---------------------------------------------

        if loans:

            st.write(
                f"Активных кредитов: **{len(loans)}**"
            )

            for index, loan in enumerate(loans):

                loan_name = loan.get(
                    "name_kredite",
                    loan.get(
                        "name kredite",
                        "Кредит"
                    )
                )

                amount = float(
                    loan.get("amount", 0)
                )

                repayment = float(
                    loan.get("repayment", 0)
                )

                date_end = loan.get(
                    "date_end",
                    "не указано"
                )

                stats = loan.get("stats", "")


                with st.expander(
                    f"📌 {loan_name}"
                ):

                    st.write(
                        f"**Сумма:** {amount:,.2f} ₽"
                        .replace(",", " ")
                    )

                    st.write(
                        f"**К возврату:** {repayment:,.2f} ₽"
                        .replace(",", " ")
                    )

                    st.caption(
                        f"Срок до: {date_end}"
                    )


                    if stats == "+":

                        st.success(
                            "Кредит погашен вовремя"
                        )

                    elif stats == "-":

                        st.error(
                            "Есть просрочка"
                        )

                    else:

                        st.info(
                            "Кредит активен"
                        )


        else:

            st.info(
                "У вас пока нет кредитов."
            )


        st.divider()


        if st.button(
            "💳 Оформить новый кредит",
            type="primary",
            use_container_width=True,
        ):

            st.switch_page("kredits.py")


finally:

    db.close()
