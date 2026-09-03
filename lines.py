import streamlit as st
import shelve
import random

DB_FILE = "server_bank_db"

TICKET_PRICE = 1000

# Бонус: шанс
TICKET_CHANCES = [
    (0.02, 50),
    (0.05, 35),
    
]


def format_money(value):
    return f"{float(value):,.2f} ₽".replace(",", " ")


def get_user(db, username):
    if username not in db:
        db[username] = {
            "password": "",
            "balance": 1000.0,
            "credit_limit": 60000.0,
            "loans": [],
            "lines_tickets": [],
        }

    user = db[username]

    user.setdefault("balance", 1000.0)
    user.setdefault("credit_limit", 60000.0)
    user.setdefault("loans", [])

    # Новая система билетов
    if "lines_tickets" not in user:
        old_ticket = user.get("lines_ticket")

        if old_ticket:
            user["lines_tickets"] = [old_ticket]
        else:
            user["lines_tickets"] = []

    return user


def generate_ticket():
    values = [item[0] for item in TICKET_CHANCES]
    weights = [item[1] for item in TICKET_CHANCES]

    return random.choices(
        values,
        weights=weights,
        k=1
    )[0]


username = st.session_state.get(
    "nickname",
    ""
).strip()

st.title("〰️ Lines")

if not username:
    st.warning(
        "Сначала войдите или зарегистрируйтесь "
        "во вкладке «Регистрация»."
    )
    st.stop()


db = shelve.open(
    DB_FILE,
    writeback=True
)

try:

    user = get_user(
        db,
        username
    )

    balance = float(
        user.get(
            "balance",
            1000.0
        )
    )

    tickets = user.get(
        "lines_tickets",
        []
    )

    # =========================================================
    # БАЛАНС
    # =========================================================

    st.subheader(
        f"Привет, {username} 👋"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "💰 Ваш баланс",
            format_money(balance)
        )

    with col2:
        unused_count = sum(
            1
            for ticket in tickets
            if not ticket.get("used", False)
        )

        st.metric(
            "🎟️ Билетов",
            unused_count
        )

    st.divider()

    # =========================================================
    # ИНФОРМАЦИЯ
    # =========================================================

    st.subheader("🎟️ Билеты Lines")

    st.write(
        "Каждый билет стоит **1000 ₽**."
    )

    st.write(
        "Билет можно использовать при оформлении "
        "одного кредита."
    )

    st.info(
        "🎲 Каждый билет получает случайный бонус:"
    )

    st.write(
        "• **0.02%** → 50%\n\n"
        "• **0.20%** → 35%\n\n"
        
    )

    st.divider()

    # =========================================================
    # ПОКУПКА
    # =========================================================

    st.subheader("🛒 Купить билет")

    st.write(
        f"Цена одного билета: "
        f"**{format_money(TICKET_PRICE)}**"
    )

    if balance < TICKET_PRICE:

        st.error(
            "❌ Недостаточно денег для покупки билета."
        )

    else:

        if st.button(
            "🎟️ Купить билет за 1000 ₽",
            type="primary",
            use_container_width=True
        ):

            # Проверяем баланс ещё раз
            current_balance = float(
                user.get(
                    "balance",
                    1000.0
                )
            )

            if current_balance < TICKET_PRICE:

                st.error(
                    "❌ Недостаточно средств."
                )

            else:

                ticket_value = generate_ticket()

                new_ticket = {
                    "value": ticket_value,
                    "used": False,
                }

                tickets.append(
                    new_ticket
                )

                user["balance"] = (
                    current_balance
                    - TICKET_PRICE
                )

                user["lines_tickets"] = tickets

                db[username] = user
                db.sync()

                st.session_state.b = (
                    user["balance"]
                )

                st.success(
                    f"🎉 Билет куплен!\n\n"
                    f"Ваш бонус: "
                    f"**{ticket_value:.2f}%**"
                )

                st.rerun()

    # =========================================================
    # МОИ БИЛЕТЫ
    # =========================================================

    st.divider()

    st.subheader("🎟️ Мои билеты")

    if not tickets:

        st.info(
            "У вас пока нет билетов."
        )

    else:

        unused_tickets = [
            (index, ticket)
            for index, ticket in enumerate(tickets)
            if not ticket.get("used", False)
        ]

        used_tickets = [
            (index, ticket)
            for index, ticket in enumerate(tickets)
            if ticket.get("used", False)
        ]

        if unused_tickets:

            st.write(
                f"**Активные билеты: "
                f"{len(unused_tickets)}**"
            )

            for number, (index, ticket) in enumerate(
                unused_tickets,
                start=1
            ):

                value = float(
                    ticket.get(
                        "value",
                        0
                    )
                )

                col1, col2 = st.columns(
                    [3, 1]
                )

                with col1:
                    st.success(
                        f"🎟️ Билет #{number}  "
                        f"→ **−{value:.2f}%**"
                    )

                with col2:
                    st.caption(
                        "Готов к использованию"
                    )

        else:

            st.info(
                "У вас нет неиспользованных билетов."
            )

        # =====================================================
        # ИСПОЛЬЗОВАННЫЕ
        # =====================================================

        if used_tickets:

            st.divider()

            st.write(
                f"Использованные билеты: "
                f"**{len(used_tickets)}**"
            )

            for number, (index, ticket) in enumerate(
                used_tickets,
                start=1
            ):

                value = float(
                    ticket.get(
                        "value",
                        0
                    )
                )

                st.caption(
                    f"✓ Билет использован — "
                    f"бонус −{value:.2f}%"
                )

finally:

    try:
        db.close()
    except:
        pass
