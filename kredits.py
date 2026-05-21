import streamlit as st
import time
from datetime import date
import shelve
from project import *  # Предполагается, что этот файл существует у вас

# --- ПОДКЛЮЧЕНИЕ ГЛОБАЛЬНОЙ БАЗЫ ДЛЯ АДМИНА ---
@st.cache_resource
def get_global_db():
    return {}
global_db = get_global_db()

# Получаем имя текущего пользователя
user_name = st.session_state.get("nickname", "").strip()

# --- БЕЗОПАСНОЕ ЧТЕНИЕ ДАННЫХ ИЗ БАЗЫ СЕРВЕРА ---
db_server = shelve.open("server_bank_db", writeback=True)

# Инициализируем дефолтный баланс, если базы еще нет
if "bank_balance" not in db_server:
    db_server["bank_balance"] = 60000.0
bank_balance = db_server["bank_balance"]

loans_list = []
if user_name:
    if user_name not in db_server:
        db_server[user_name] = {"loans": []}
    loans_list = db_server[user_name]["loans"]

# Считаем сумму активных долгов пользователя
total_active_credit = sum(loan.get("amount", 0) for loan in loans_list)

# Закрываем базу сразу после чтения основных данных страницы
db_server.close()

# Синхронизируем данные с админкой
if user_name:
    global_db[user_name] = {
        "balance": st.session_state.get("b", 1000),
        "credit_limit": st.session_state.get("n", 60000),
        "credit_taken": total_active_credit
    }

st.title("Кредит")

# Показываем список текущих взятых кредитов пользователя, если они есть
if loans_list:
    st.subheader("📋 Ваши активные кредиты:")
    for loan in loans_list:
        st.info(f"**{loan['name_kredite']}**: {loan['amount']} ₽ (Вернуть: {loan['repayment']} ₽ до {loan['date_end']})")

st.warning(f"Доступно в банке: {bank_balance} ₽")

kredit = st.number_input("Выберете сумму кредита", min_value=300, max_value=60000)

st.write("---")
st.subheader("🗓️ Выбор дат кредитования")

# Использование st.date_input для выбора диапазона дат
today = date.today()
selected_dates = st.date_input(
    "Выберите дату начала и конца кредита",
    value=(today, today),
    min_value=today
)

# Проверяем, выбрал ли пользователь обе даты
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    d_start, d_end = selected_dates
    delta = d_end - d_start
    loan_days = delta.days

    if loan_days <= 0:
        st.error("Ошибка: Срок кредита должен быть минимум 1 день!")
        total_interest = 0.0
    else:
        # Автоматическое определение периода на основе количества дней
        if loan_days <= 14:  # До двух недель считается недельным тарифом
            period_name = "Недельный тариф"
            daily_rate = 0.015  # Самая высокая ставка (0.5% в день)
            st.warning(f"⏳ Распознан период: **Неделя** ({loan_days} дн.). Включена повышенная ставка переплаты!")
        elif loan_days <= 90:  # От 15 до 90 дней считается месячным тарифом
            period_name = "Месячный тариф"
            daily_rate = 0.002  # Средняя ставка (0.2% в день)
            st.info(f"📅 Распознан период: **Месяц** ({loan_days} дн.). Ставка стандартная.")
        else:  # Все что больше 90 дней — годовой тариф
            period_name = "Годовой тариф"
            daily_rate = 0.0006  # Самая низкая ставка (0.06% в день)
            st.success(f"📈 Распознан период: **Год** ({loan_days} дн.). Ставка снижена.")

        # Расчет переплаты
        total_interest = kredit * daily_rate * loan_days
        st.metric(label="Переплата", value=f"{round(total_interest, 2)} ₽")
else:
    st.info("Пожалуйста, выберите вторую дату (дату окончания кредита) в календаре.")
    loan_days = 0
    total_interest = 0.0

# --- ИСПРАВЛЕННЫЙ ДИАЛОГ КРЕДИТА ---
@st.dialog("Кредитный договор")
def show_popup():
    new_loan = st.text_input("введите название кредита")
    st.write("Проставьте все галочки для подтверждения:")
    c1 = st.checkbox("я обязуюсь оплатить кредит с комиссией")
    c2 = st.checkbox("я оставляю под залог")
    c3 = st.checkbox("согласен на изъятие залога при неуплате")
    c4 = st.checkbox("согласен на выбранный срок для закрытия")
    c5 = st.checkbox("согласен на начисление штрафных процентов")
    
    if st.button("Подтвердить и взять кредит"):
        if all([c1, c2, c3, c4, c5]) and user_name:
            # ОТКРЫВАЕМ БАЗУ ДАННЫХ ЗАНОВО ВНУТРИ ДИАЛОГА ДЛЯ ПРОВЕРКИ И ЗАПИСИ
            db_write = shelve.open("server_bank_db", writeback=True)
            
            if db_write["bank_balance"] >= kredit:
                # 1. Снимаем деньги из банка
                db_write["bank_balance"] -= kredit
                
                # 2. Формируем данные кредита
                loan_details = {
                    "name_kredite": new_loan if new_loan else "Без названия",
                    "amount": kredit,
                    "date_start": str(d_start),
                    "date_end": str(d_end),
                    "repayment": round(kredit + total_interest, 2)
                }
                
                # 3. Записываем в базу данных сервера
                if user_name not in db_write:
                    db_write[user_name] = {"loans": []}
                
                db_write[user_name]["loans"].append(loan_details)
                db_write.sync()
                
                # 4. Моментально обновляем данные для admin
                global_db[user_name] = {
                    "balance": st.session_state.get("b", 1000),
                    "credit_limit": st.session_state.get("n", 60000),
                    "credit_taken": sum(l.get("amount", 0) for l in db_write[user_name]["loans"])
                }
                db_write.close()
                
                st.success(f"Кредит на {kredit} ₽ оформлен!")
                time.sleep(1)
                st.rerun()
            else:
                db_write.close()
                st.error("В банке недостаточно средств!")
        elif not user_name:
            st.error("Ошибка: вы не авторизованы!")
        else:
            st.warning("Нужно отметить все пункты!")

if st.button("Оформить кредит"):
    if not user_name:
        st.error("Ошибка: авторизуйтесь перед оформлением кредита!")
    elif loan_days <= 0:
        st.error("Ошибка: Выберите корректный диапазон дат!")
    else:
        show_popup()
