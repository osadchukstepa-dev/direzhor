import streamlit as st
import time
import extra_streamlit_components as stx
import json

# В начале файла
@st.cache_data(ttl=2)
def get_updated_db():
    try:
        with open("users_stats.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

db = get_updated_db()

cookie_manager = stx.CookieManager(key="mngr_page2")
current_user = cookie_manager.get("user_name")

# Инициализация session_state
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "b" not in st.session_state:
    st.session_state.b = 0
if "reg" not in st.session_state:
    st.session_state.reg = True

def messege():
    if st.session_state.reg:
        st.toast("✅ Вы успешно зарегистрировались")
        time.sleep(1)
        st.session_state.reg = False

akk, birz = st.tabs(["Аккаунт", "Биржа"])

if not st.session_state.nickname:
    saved_name = cookie_manager.get("user_name")
    if saved_name:
        st.session_state.nickname = saved_name

if not st.session_state.nickname:
    st.write("К сожалению, у вас нет аккаунта, войдите для дальнейшего использования")
else:
    with akk:
        st.title(f"Ваш баланс: {st.session_state.b}")

        if st.button("Очистить куки и выйти"):
            cookie_manager.delete("user_name")
            st.session_state.nickname = ""
            st.switch_page("project.py")
        
        messege()
        
        if st.button("Перейти к кредитам"):
            st.switch_page("kredits.py")

    with birz:
        st.subheader("Список ваших кредитов")

        # 1. Сначала создаем пустые значения на случай, если данных нет
        user_stats = []
        plus = 0
        minus = 0
        
        # 2. Проверяем, есть ли пользователь в нашей базе db
        if current_user in db:
            # Достаем список кредитов
            user_loans = db[current_user].get("loans", [])
            
            # Собираем все статусы
            user_stats = [l.get("stats") for l in user_loans]
            
            # Считаем
            plus = user_stats.count("+")
            minus = user_stats.count("_")
            
            # Логика статуса
            if plus > minus:
                st.write("Статус: :green[Оплачено]")
                st.write("Ваша кредитная история: :green[хорошая]")
            elif plus == minus and plus > 0:
                st.write("Статус: :orange[В процессе]")
                st.write("Ваша кредитная история: :orange[сомнительная]")
            else:
                st.write("Статус: :red[Должник]")
                st.write("Ваша кредитная история: :red[Плохая]")

            # Вывод списка кредитов
            if user_loans:
                for loan in user_loans:
                    with st.expander(f"📌 {loan.get('name kredite', 'Кредит')}"):
                        st.write(f"Сумма: {loan.get('amount', 0)} ₽")
                        st.write(f"К возврату: {loan.get('repayment', 0)} ₽")
                        st.caption(f"Срок: {loan.get('date_end', 'не указан')}")
            else:
                st.info("У вас нет активных кредитов")
        else:
            st.info("У вас пока нет истории кредитов")
