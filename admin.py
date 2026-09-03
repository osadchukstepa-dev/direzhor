import streamlit as st
import shelve
from datetime import date

DB_FILE = "server_bank_db"
CREDIT_REWARD = 500.0

st.title("🛡️ Админ-панель")

# Проверка доступа
if not st.session_state.get("is_admin", False):
    st.error("⛔ Доступ запрещён.")
    st.stop()


def money(value):
    return f"{float(value):,.2f} ₽".replace(",", " ")


def prepare_user(user):
    if not isinstance(user, dict):
        user = {}

    user.setdefault("password", "")
    user.setdefault("balance", 1000.0)
    user.setdefault("credit_limit", 60000.0)
    user.setdefault("loans", [])
    user.setdefault("lines_tickets", [])

    # Поддержка старого билета Lines
    if not user["lines_tickets"]:
        old_ticket = user.get("lines_ticket")

        if old_ticket:
            user["lines_tickets"] = [old_ticket]

    return user


db = shelve.open(DB_FILE, writeback=True)

try:

    # =========================================================
    # ПОЛУЧАЕМ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
    # =========================================================

    all_users = []

    for key in db.keys():

        # Служебные записи не показываем
        if key in [
            "bank_balance",
            "admin",
            "__admin__"
        ]:
            continue

        try:
            value = db[key]

            if isinstance(value, dict):
                all_users.append(str(key))

        except Exception:
            pass

    all_users = sorted(set(all_users))

    # =========================================================
    # СТАТИСТИКА
    # =========================================================

    total_active = 0
    total_closed = 0
    total_rewards = 0.0

    for username in all_users:

        user = prepare_user(db[username])

        for loan in user.get("loans", []):

            if loan.get("status") == "closed":
                total_closed += 1

                total_rewards += float(
                    loan.get(
                        "reward",
                        CREDIT_REWARD
                    )
                )
            else:
                total_active += 1

    st.subheader("📊 Статистика")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "👥 Пользователей",
            len(all_users)
        )

    with c2:
        st.metric(
            "💳 Активных кредитов",
            total_active
        )

    with c3:
        st.metric(
            "✅ Закрытых кредитов",
            total_closed
        )

    st.divider()

    # =========================================================
    # ПОЛЬЗОВАТЕЛИ
    # =========================================================

    st.subheader("👥 Пользователи")

    if not all_users:

        st.warning(
            "Пользователей пока нет в server_bank_db."
        )

        st.write(
            "Создай аккаунт через вкладку "
            "«Регистрация», после этого пользователь "
            "появится здесь."
        )

        st.stop()

    # =========================================================
    # ВЫБОР ПОЛЬЗОВАТЕЛЯ
    # =========================================================

    selected_user = st.selectbox(
        "Выберите пользователя",
        all_users,
        key="admin_selected_user"
    )

    user = prepare_user(
        db[selected_user]
    )

    db[selected_user] = user
    db.sync()

    # =========================================================
    # ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
    # =========================================================

    balance = float(
        user.get("balance", 1000.0)
    )

    credit_limit = float(
        user.get("credit_limit", 60000.0)
    )

    loans = user.get("loans", [])

    active_loans = [
        loan for loan in loans
        if loan.get("status", "active") != "closed"
    ]

    closed_loans = [
        loan for loan in loans
        if loan.get("status") == "closed"
    ]

    credit_taken = sum(
        float(loan.get("amount", 0))
        for loan in active_loans
    )

    # =========================================================
    # ИНФОРМАЦИЯ
    # =========================================================

    st.subheader(
        f"👤 Пользователь: {selected_user}"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "💰 Баланс",
            money(balance)
        )

    with c2:
        st.metric(
            "💳 Активных кредитов",
            len(active_loans)
        )

    with c3:
        st.metric(
            "📊 Сумма кредитов",
            money(credit_taken)
        )

    # =========================================================
    # LINES
    # =========================================================

    st.divider()

    st.subheader("〰️ Lines")

    tickets = user.get(
        "lines_tickets",
        []
    )

    unused_tickets = [
        ticket for ticket in tickets
        if not ticket.get("used", False)
    ]

    used_tickets = [
        ticket for ticket in tickets
        if ticket.get("used", False)
    ]

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "🎟️ Неиспользованных",
            len(unused_tickets)
        )

    with c2:
        st.metric(
            "✓ Использованных",
            len(used_tickets)
        )

    if unused_tickets:

        st.write("**Активные билеты:**")

        for number, ticket in enumerate(
            unused_tickets,
            start=1
        ):

            value = float(
                ticket.get("value", 0)
            )

            st.success(
                f"🎟️ Билет #{number} — "
                f"−{value:.2f}%"
            )

    # =========================================================
    # АКТИВНЫЕ КРЕДИТЫ
    # =========================================================

    st.divider()

    st.subheader("💳 Активные кредиты")

    if not active_loans:

        st.info(
            "У пользователя нет активных кредитов."
        )

    else:

        for loan_index, loan in enumerate(
            active_loans
        ):

            loan_name = loan.get(
                "name_kredite",
                loan.get(
                    "name kredite",
                    f"Кредит #{loan_index + 1}"
                )
            )

            amount = float(
                loan.get("amount", 0)
            )

            repayment = float(
                loan.get("repayment", 0)
            )

            with st.expander(
                f"📌 {loan_name} — {money(amount)}"
            ):

                st.write(
                    f"**Сумма:** {money(amount)}"
                )

                st.write(
                    f"**К возврату:** {money(repayment)}"
                )

                st.write(
                    f"**Дата начала:** "
                    f"{loan.get('date_start', 'не указано')}"
                )

                st.write(
                    f"**Дата окончания:** "
                    f"{loan.get('date_end', 'не указано')}"
                )

                st.write(
                    f"**Ставка:** "
                    f"{float(loan.get('daily_rate', 0)):.2f}%"
                )

                lines_discount = float(
                    loan.get(
                        "lines_discount",
                        0
                    )
                )

                if lines_discount > 0:

                    st.write(
                        f"〰️ Lines: "
                        f"−{lines_discount:.2f}%"
                    )

                st.warning(
                    "Этот кредит ещё активен."
                )

                # =================================================
                # ЗАКРЫТИЕ ТОЛЬКО АДМИНОМ
                # =================================================

                if st.button(
                    "✅ Закрыть этот кредит",
                    key=f"close_{selected_user}_{loan_index}",
                    type="primary",
                    use_container_width=True
                ):

                    # Перечитываем базу
                    db.close()

                    db = shelve.open(
                        DB_FILE,
                        writeback=True
                    )

                    current_user = prepare_user(
                        db[selected_user]
                    )

                    current_loans = (
                        current_user.get(
                            "loans",
                            []
                        )
                    )

                    # Ищем кредит
                    target = None

                    for current_loan in current_loans:

                        current_name = current_loan.get(
                            "name_kredite",
                            current_loan.get(
                                "name kredite",
                                ""
                            )
                        )

                        current_amount = float(
                            current_loan.get(
                                "amount",
                                0
                            )
                        )

                        if (
                            current_name == loan_name
                            and
                            current_amount == amount
                            and
                            current_loan.get(
                                "status",
                                "active"
                            ) != "closed"
                        ):

                            target = current_loan
                            break

                    if target is None:

                        st.error(
                            "❌ Кредит не найден."
                        )

                    else:

                        # Закрываем
                        target["status"] = "closed"

                        # Хорошая кредитная история
                        target["stats"] = "+"

                        target["closed_date"] = str(
                            date.today()
                        )

                        # Награда
                        target["reward"] = (
                            CREDIT_REWARD
                        )

                        # +500 пользователю
                        current_balance = float(
                            current_user.get(
                                "balance",
                                1000.0
                            )
                        )

                        current_user["balance"] = (
                            current_balance
                            + CREDIT_REWARD
                        )

                        current_user["loans"] = (
                            current_loans
                        )

                        db[selected_user] = (
                            current_user
                        )

                        db.sync()

                        st.success(
                            f"✅ Кредит закрыт!\n\n"
                            f"Пользователю "
                            f"**{selected_user}** "
                            f"начислено **+500 ₽**."
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
                loan.get(
                    "name kredite",
                    "Кредит"
                )
            )

            amount = float(
                loan.get("amount", 0)
            )

            closed_date = loan.get(
                "closed_date",
                "не указано"
            )

            reward = float(
                loan.get(
                    "reward",
                    CREDIT_REWARD
                )
            )

            with st.expander(
                f"✅ {loan_name} — {money(amount)}"
            ):

                st.write(
                    f"Сумма: **{money(amount)}**"
                )

                st.write(
                    f"Закрыт: **{closed_date}**"
                )

                st.success(
                    f"💰 Начислено: "
                    f"+{money(reward)}"
                )

finally:

    try:
        db.close()
    except:
        pass
