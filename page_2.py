import streamlit as st
import time
import extra_streamlit_components as stx
from kredits import db, user_name
import json
# В начале файла page_2.py
@st.cache_data(ttl=2)  # Проверять файл каждые 2 секунды
def get_updated_db():
    with open("users_stats.json", "r") as f:
        return json.load(f)

db = get_updated_db() # Теперь db всегда актуальна


cookie_manager = stx.CookieManager(key="mngr_page2")
current_user = cookie_manager.get("user_name")

akk, birz = st.tabs(["Аккаунт", "Биржа"])

if "reg" not in st.session_state:
    st.session_state.reg = True



def messege():
    if st.session_state.reg:
        st.toast("✅вы успешно заригестрировались")
        time.sleep(1)
        st.session_state.reg = False





if not st.session_state.nickname:
    saved_name = cookie_manager.get("user_name")
    if saved_name:
        st.session_state.nickname = saved_name


if not st.session_state.nickname:
    st.write("К сожалению, у вас нет аккаунта, войдите для дальнейшего использования ")

else:
    with akk:
        st.title(f"Ваш баланс: {st.session_state.b}")

        if st.button("Очистить куки и выйти"):
            cookie_manager.delete("user_name", key="delete_user_name")
            st.session_state.nickname = ""
            time.sleep(1) 
            st.switch_page("project.py") 
            st.rerun()
            st.balloons()
        messege()
        
                
        
        if st.button("Перейти к кредитам"):
            st.switch_page("kredits.py")
        with birz:
            st.subheader("Список ваших кредитов")


зопасный блок:

# 1. Сначала создаем пустые значения на случай, если данных нет
            user_stats = []
            plus = 0
            minus = 0
            
            # 2. Проверяем, есть ли пользователь в нашей базе db
            if current_user in db:
                # Достаем список кредитов (если его нет, будет пустой список [])
                user_loans = db[current_user].get("loans", [])
                
                # Собираем все статусы из списка кредитов
                user_stats = [l.get("stats") for l in user_loans]
                
                # Теперь безопасно считаем
                plus = user_stats.count("+")
                minus = user_stats.count("_")
                
                # Твоя логика цвета (теперь она не упадет)
                if plus > minus:
                    st.write("Статус: :green[Оплачено]")
                elif plus == minus and plus > 0: # Добавил проверку, чтобы не было оранжевого у пустых аккаунтов
                    st.write("Статус: :orange[В процессе]")
                else:
                    st.write("Статус: :red[Должник]")
            else:
                st.info("У вас пока нет истории кредитов")
            
                        if plus > minus:
                            st.write("Ваша кредитаная история: :green[хорошая]")
                        elif plus == minus:
                            st.write("Ваша кредитаная история : :orange[сомнительная]")
                        else:
                            st.write("Ваша кредитаная история: :red[Плохая]")

            if current_user in db:
                    # Получаем список всех кредитов этого юзера
                    user_loans = db[current_user].get("loans", [])
                    
                    if user_loans:
                        # 3. Цикл проходит по ВСЕМ кредитам юзера и выводит их
                        for loan in user_loans:
                            with st.expander(f"📌 {loan.get('name kredite', 'Кредит')}"):
                                st.write(f"Сумма: {loan['amount']} ₽")
                                st.write(f"К возврату: {loan['repayment']} ₽")
                                st.caption(f"Срок: {loan['date_end']}")
                    else:
                        st.info("У вас нет активных кредитов")
               
    with birz:

        pass


