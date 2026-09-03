import streamlit as st
import shelve


# =========================================================
# НАСТРОЙКИ
# =========================================================

st.set_page_config(
    page_title="Rasino",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


DB_FILE = "server_bank_db"

# Код администратора
ADMIN_CODE = "248769794510455"


# =========================================================
# ГЛОБАЛЬНАЯ БАЗА ДЛЯ АДМИНКИ
# =========================================================

@st.cache_resource
def get_global_db():
    return {}


global_db = get_global_db()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "n": 60000.0,
    "b": 1000.0,
    "nickname": "",
    "credit_taken": 0.0,
    "is_admin": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# СИНХРОНИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ С БАЗОЙ
# =========================================================

nickname = st.session_state.get("nickname", "").strip()

if nickname:

    try:
        db = shelve.open(DB_FILE, writeback=True)

        if nickname in db:

            user = db[nickname]

            # Если каких-то полей нет — добавляем
            if "balance" not in user:
                user["balance"] = 1000.0

            if "credit_limit" not in user:
                user["credit_limit"] = 60000.0

            if "loans" not in user:
                user["loans"] = []

            if "lines_ticket" not in user:
                user["lines_ticket"] = None

            db[nickname] = user
            db.sync()

            # Загружаем настоящий баланс
            st.session_state.b = float(
                user.get("balance", 1000.0)
            )

            st.session_state.n = float(
                user.get("credit_limit", 60000.0)
            )

            loans = user.get("loans", [])

            st.session_state.credit_taken = sum(
                float(loan.get("amount", 0))
                for loan in loans
            )

            global_db[nickname] = {
                "balance": st.session_state.b,
                "credit_limit": st.session_state.n,
                "credit_taken": st.session_state.credit_taken,
            }

        db.close()

    except Exception as e:
        st.error(f"Ошибка базы данных: {e}")


# =========================================================
# ДИЗАЙН
# =========================================================

st.markdown(
    """
    <style>

    /* ===== ОСНОВНОЙ ФОН ===== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(120, 80, 255, 0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(0, 180, 255, 0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(255, 80, 180, 0.25),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #090914,
                #111329,
                #0b1022
            );

        background-attachment: fixed;
    }


    /* ===== УБИРАЕМ ЛИШНИЕ ОТСТУПЫ ===== */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ===== SIDEBAR ===== */

    section[data-testid="stSidebar"] {
        background: rgba(10, 12, 30, 0.72);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border-right: 1px solid rgba(255,255,255,0.10);
    }


    /* ===== ТЕКСТ ===== */

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }


    /* ===== КНОПКИ ===== */

    .stButton > button {
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.15);

        background: rgba(255,255,255,0.08);

        color: white;

        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);

        transition:
            transform 0.15s ease,
            background 0.15s ease,
            border 0.15s ease;
    }

    .stButton > button:hover {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.30);

        transform: translateY(-2px);
    }


    /* ===== INPUT ===== */

    div[data-baseweb="input"] {
        background: rgba(255,255,255,0.07);
        border-radius: 14px;
    }


    /* ===== КАРТОЧКИ ===== */

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);

        border-radius: 20px;

        padding: 20px;

        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }


    /* ===== ALERTS ===== */

    div[data-testid="stAlert"] {
        border-radius: 16px;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
    }


    /* ===== NAVIGATION ===== */

    div[data-testid="stSidebarNav"] {
        padding-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            padding: 10px 5px 20px 5px;
            text-align: center;
        ">
            <div style="
                font-size: 34px;
                font-weight: 800;
            ">
                ✨ Rasino
            </div>

            <div style="
                opacity: 0.65;
                font-size: 13px;
                margin-top: 5px;
            ">
                Финансовая система
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


    # =====================================================
    # ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ
    # =====================================================

    if nickname:

        st.markdown("### 👤 Пользователь")

        st.write(f"**{nickname}**")

        st.metric(
            "Баланс",
            f"{st.session_state.b:,.2f} ₽".replace(",", " ")
        )

        st.divider()


    # =====================================================
    # АДМИНКА
    # =====================================================

    st.markdown("### 🛡️ Администратор")

    if not st.session_state.is_admin:

        admin_password = st.text_input(
            "Код администратора",
            type="password",
            key="admin_password_input",
        )

        if st.button(
            "Войти как админ",
            use_container_width=True,
        ):

            if admin_password == ADMIN_CODE:

                st.session_state.is_admin = True

                st.success("Доступ разрешён!")

                st.rerun()

            else:

                st.error("Неверный код!")

    else:

        st.success("Вы вошли как Администратор")

        if st.button(
            "Выйти из админки",
            use_container_width=True,
        ):

            st.session_state.is_admin = False

            st.rerun()


# =========================================================
# СТРАНИЦЫ
# =========================================================

pg_reg = st.Page(
    "project.py",
    title="Регистрация",
    icon="👤",
)

pg_home = st.Page(
    "page_2.py",
    title="Главная",
    icon="🏠",
    default=True,
)

pg_lines = st.Page(
    "lines.py",
    title="Lines",
    icon="〰️",
)

pg_kredits = st.Page(
    "kredits.py",
    title="Кредиты",
    icon="💳",
)


pages_list = [
    pg_reg,
    pg_home,
    pg_lines,
    pg_kredits,
]


# =========================================================
# АДМИН-СТРАНИЦА
# =========================================================

if st.session_state.is_admin:

    pg_admin = st.Page(
        "admin.py",
        title="Админ-панель",
        icon="🛡️",
    )

    pages_list.append(pg_admin)


# =========================================================
# NAVIGATION
# =========================================================

pg = st.navigation(
    pages_list,
    position="sidebar",
)

pg.run()
