
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

if "nickname" not in st.session_state:
    st.session_state.nickname = ""

cookie_manager = stx.CookieManager(key="mngr_page2")
current_user = cookie_manager.get("user_name")

akk, birz = st.tabs(["Аккаунт", "Кредиты"])

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
        if current_user:
            st.write("Вы вошли, как", current_user)
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
            
            # 1. Получаем данные из кук
            raw_data = cookie_manager.get(cookie="kredits_cookies")
            
            if raw_data is None:
                st.info("Загрузка данных из браузера... (если это длится долго, обновите страницу)")
            else:
                try:
                    # 2. Декодируем список кредитов из куки
                    user_loans = json.loads(raw_data) if isinstance(raw_data, str) else (raw_data if raw_data else [])
                    
                    if user_loans:
                        # Считаем историю (если в кредитах есть поле stats)
                        # Если stats нет, по умолчанию ставим "+"
                        plus = sum(1 for l in user_loans if l.get("stats", "+") == "+")
                        minus = sum(1 for l in user_loans if l.get("stats") == "-")
        
                        if plus > minus:
                            st.write("Ваша кредитная история: :green[хорошая]")
                        elif plus == minus:
                            st.write("Ваша кредитная история: :orange[сомнительная]")
                        else:
                            st.write("Ваша кредитная история: :red[плохая]")
        
                        # 3. Выводим каждый кредит из КУКИ
                        for loan in user_loans:
                            with st.expander(f"📌 {loan.get('name', 'Кредит')}"):
                                st.write(f"Сумма: {loan['amount']} ₽")
                                st.write(f"К возврату: {loan['repayment']} ₽")
                                st.caption(f"Срок: {loan.get('date_end')}")
                                if st.button("Сдать кредит", key=f"pay_{loan['name']}_{time.time()}"):
                                    st.write("Тут будет логика оплаты")
                    else:
                        st.info("У вас нет активных кредитов (куки пусты)")
                        
                except Exception as e:
                    st.error(f"Ошибка чтения кук: {e}")
        
