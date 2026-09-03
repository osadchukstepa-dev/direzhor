import streamlit as st
import time
from datetime import date, timedelta
import shelve

DB_FILE = "server_bank_db"

user_name = st.session_state.get("nickname", "").strip()

st.title("💳 Кредиты")

if not user_name:
    st.warning("Сначала войдите или зарегистрируйтесь.")
    if st.button("Перейти к регистрации"):
        st.switch_page("project.py")
    st.stop()


def get_user(db, username):
    if username not in db:
        db[username] = {
            "password": "",
            "balance": 1000.0,
            "credit_limit": 60000.0,
            "loans": [],
            "lines_tickets": []
        }

    user = db[username]

    user.setdefault("balance", 1000.0)
    user.setdefault("credit_limit", 60000.0)
    user.setdefault("loans", [])

    # Поддержка старого формата Lines
    if "lines_tickets" not in user:
        old_ticket = user.get("lines_ticket")

        if old_ticket:
            user["lines_tickets"] = [old_ticket]
        else:
            user["lines_tickets"] = []

    return user


def money(value):
    return f"{float(value):,.2f} ₽".replace(",", " ")


db = shelve.open(DB_FILE, writeback=True)

try:
    user = get_user(db, user_name)

    loans_list = user.get("loans", [])

    active_loans = [
        loan for loan in loans_list
        if loan.get("status", "active") != "closed"
    ]

    closed_loans = [
        loan for loan in loans_list
        if loan.get("status") == "closed"
    ]

    balance = float(user.get("balance", 1000.0))
    credit_limit = float(user.get("credit_limit", 60000.0))

    credit_taken = sum(
        float(loan.get("amount", 0))
        for loan in active_loans
    )

    st.session_state.b = balance
    st.session_state.n = credit_limit
    st.session_state.credit_taken = credit_taken

    # =========================================================
    # АКТИВНЫЕ КРЕДИТЫ
    # =========================================================

    st.subheader("📋 Ваши активные кредиты")

    if active_loans:
        for index, loan in enumerate(active_loans):

            loan_name = loan.get(
                "name_kredite",
                loan.get("name kredite", "Кредит")
            )

            amount = float(loan.get("amount", 0))
            repayment = float(loan.get("repayment", 0))

            with st.expander(
                f"📌 {loan_name} — {money(amount)}"
            ):
                st.write(f"Сумма: **{money(amount)}**")
                st.write(f"К возврату: **{money(repayment)}**")
                st.write(
                    f"Дата оформления: "
                    f"{loan.get('date_start', 'не указано')}"
                )
                st.write(
                    f"Срок до: "
                    f"{loan.get('date_end', 'не указано')}"
                )

                st.warning(
                    "🔒 Закрыть кредит может только администратор."
                )
    else:
        st.info("У вас нет активных кредитов.")

    st.divider()

    # =========================================================
    # БАЛАНС БАНКА
    # =========================================================

    bank_balance = float(
        user.get("bank_balance", 60000.0)
    )

    st.metric(
        "🏦 Доступно в банке",
        money(bank_balance)
    )

    # =========================================================
    # LINES — ТОЛЬКО ВЫБОР БИЛЕТА
    # =========================================================

    st.subheader("〰️ Lines")

    tickets = user.get("lines_tickets", [])

    available_tickets = [
        (index, ticket)
        for index, ticket in enumerate(tickets)
        if not ticket.get("used", False)
    ]

    selected_ticket_index = None
    lines_discount = 0.0

    if available_tickets:

        ticket_options = ["Не использовать билет"]

        for number, (ticket_index, ticket) in enumerate(
            available_tickets,
            start=1
        ):
            value = float(ticket.get("value", 0))

            ticket_options.append(
                f"Билет #{number} — −{value:.2f}%"
            )

        selected_ticket = st.selectbox(
            "Выберите билет Lines",
            ticket_options
        )

        if selected_ticket != "Не использовать билет":

            selected_position = (
                ticket_options.index(selected_ticket) - 1
            )

            selected_ticket_index, selected_ticket_data = (
                available_tickets[selected_position]
            )

            lines_discount = float(
                selected_ticket_data.get("value", 0)
            )

            st.success(
                f"Выбран билет: "
                f"**−{lines_discount:.2f}%**"
            )

    else:
        st.info("У вас нет неиспользованных билетов Lines.")

    # =========================================================
    # КРЕДИТ
    # =========================================================

    st.subheader("➕ Оформить кредит")

    kredit = st.number_input(
        "Сумма кредита",
        min_value=300,
        max_value=int(credit_limit),
        value=1000,
        step=100
    )

    # ВАЖНО: выбор дат оставлен
    date_start = st.date_input(
        "Дата начала кредита",
        value=date.today()
    )

    date_end = st.date_input(
        "Дата окончания кредита",
        value=date.today()
    )

    if date_end < date_start:
        st.error("Дата окончания не может быть раньше даты начала.")
        st.stop()

    loan_days = (
        date_end - date_start
    ).days

    # =========================================================
    # СТАВКИ — ОСТАВЛЕНЫ ПРЕЖНИМИ
    # =========================================================

    if loan_days <= 14:
        base_rate = 2.0
    elif loan_days <= 90:
        base_rate = 0.2
    else:
        base_rate = 0.08

    final_rate = max(
        0,
        base_rate - lines_discount
    )

    interest = (
        kredit
        * (final_rate / 100)
        * loan_days
    )

    repayment = kredit + interest

    st.write(
        f"Базовая ставка: **{base_rate:.2f}%**"
    )

    if lines_discount > 0:
        st.write(
            f"〰️ Lines: **−{lines_discount:.2f}%**"
        )

    st.write(
        f"Итоговая ставка: **{final_rate:.2f}%**"
    )

    st.write(
        f"💰 К возврату: **{money(repayment)}**"
    )

    # =========================================================
    # ДОГОВОР — ОСТАВЛЕН
    # =========================================================

    st.subheader("📄 Договор")

    agree1 = st.checkbox(
        "Я ознакомился с условиями кредита."
    )

    agree2 = st.checkbox(
        "Я согласен с суммой кредита."
    )

    agree3 = st.checkbox(
        "Я согласен со сроком кредита."
    )

    agree4 = st.checkbox(
        "Я понимаю сумму, которую нужно вернуть."
    )

    agree5 = st.checkbox(
        "Я согласен с условиями договора."
    )

    all_agreed = (
        agree1
        and agree2
        and agree3
        and agree4
        and agree5
    )

    # =========================================================
    # ОФОРМЛЕНИЕ
    # =========================================================

    if st.button(
        "💳 Оформить кредит",
        type="primary",
        disabled=not all_agreed,
        use_container_width=True
    ):

        # Проверяем лимит
        current_taken = sum(
            float(loan.get("amount", 0))
            for loan in user.get("loans", [])
            if loan.get("status", "active") != "closed"
        )

        if current_taken + kredit > credit_limit:
            st.error(
                "❌ Вы превышаете кредитный лимит."
            )
            st.stop()

        # Проверяем выбранный билет
        if selected_ticket_index is not None:

            if selected_ticket_index >= len(
                user.get("lines_tickets", [])
            ):
                st.error("❌ Билет не найден.")
                st.stop()

            selected_ticket_data = user["lines_tickets"][
                selected_ticket_index
            ]

            if selected_ticket_data.get("used", False):
                st.error(
                    "❌ Этот билет уже использован."
                )
                st.stop()

        # Проверяем деньги банка
        current_bank_balance = float(
            user.get("bank_balance", 60000.0)
        )

        if current_bank_balance < kredit:
            st.error(
                "❌ В банке недостаточно средств "
                "для выдачи этого кредита."
            )
            st.stop()

        # =====================================================
        # СОЗДАЁМ КРЕДИТ
        # =====================================================

        loan_number = len(
            user.get("loans", [])
        ) + 1

        new_loan = {
            "name_kredite": f"Кредит #{loan_number}",
            "amount": float(kredit),

            # ДАТЫ НЕ МЕНЯЕМ
            "date_start": str(date_start),
            "date_end": str(date_end),

            "daily_rate": float(final_rate),
            "base_rate": float(base_rate),
            "lines_discount": float(lines_discount),
            "repayment": float(repayment),

            "status": "active",
            "stats": "",
            "closed_date": None,
            "reward": 0.0,
        }

        user["loans"].append(
            new_loan
        )

        # =====================================================
        # ИСПОЛЬЗУЕМ ИМЕННО ВЫБРАННЫЙ БИЛЕТ
        # =====================================================

        if selected_ticket_index is not None:

            user["lines_tickets"][
                selected_ticket_index
            ]["used"] = True

        # Деньги банка
        user["bank_balance"] = (
            current_bank_balance - kredit
        )

        db[user_name] = user
        db.sync()

        st.session_state.b = float(
            user.get("balance", 1000.0)
        )

        st.session_state.credit_taken = (
            current_taken + kredit
        )

        st.success(
            f"✅ Кредит на {money(kredit)} оформлен!"
        )

        if lines_discount > 0:
            st.success(
                f"〰️ Использован выбранный билет "
                f"−{lines_discount:.2f}%"
            )

        st.rerun()

    # =========================================================
    # ЗАКРЫТЫЕ КРЕДИТЫ
    # =========================================================

    if closed_loans:

        st.divider()
        st.subheader("✅ Закрытые кредиты")

        for loan in closed_loans:

            loan_name = loan.get(
                "name_kredite",
                loan.get("name kredite", "Кредит")
            )

            amount = float(
                loan.get("amount", 0)
            )

            reward = float(
                loan.get("reward", 500)
            )

            with st.expander(
                f"✅ {loan_name} — {money(amount)}"
            ):

                st.write(
                    f"Сумма: **{money(amount)}**"
                )

                st.write(
                    f"Дата закрытия: "
                    f"**{loan.get('closed_date', 'не указано')}**"
                )

                st.success(
                    f"💰 Начислено: **+{money(reward)}**"
                )

finally:
    db.close()
