import streamlit as st
import time
import extra_streamlit_components as stx
from project import *
cookie_manager = stx.CookieManager(key="mngr_page2")


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

        pass
