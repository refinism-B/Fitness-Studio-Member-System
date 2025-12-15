import sys
import os

# Add 'code' directory to sys.path to allow importing 'mod'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'code'))

from mod import A_add_member
from mod import B_purchase
from mod import C_consume
from mod import D_main_table
from mod import E_customized_course
from mod import O_general as gr
from mod.O_config import MAIN_SHEET, MEMBER_SHEET, EVENT_SHEET, COACH, MENU, ADMIN_PASSWORD
import streamlit as st
import pandas as pd
from datetime import datetime


st.set_page_config(page_title="沛力訓練會員系統", layout="wide")

# Sidebar Navigation
st.sidebar.title("功能選單")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "首頁總覽"

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False


def set_page(page_name):
    st.session_state.page = page_name


# Button style navigation
if st.sidebar.button("📊 首頁總覽", use_container_width=True):
    set_page("首頁總覽")

if st.sidebar.button("👤 新增會員", use_container_width=True):
    set_page("新增會員")

if st.sidebar.button("💰 購買課程", use_container_width=True):
    set_page("購買課程")

if st.sidebar.button("🏋️ 會員上課", use_container_width=True):
    set_page("會員上課")

if st.sidebar.button("🔄 手動更新", use_container_width=True):
    set_page("手動更新")

page = st.session_state.page


def show_main_table():
    if not st.session_state.is_admin:
        return

    try:
        df = gr.GET_DF_FROM_DB(MAIN_SHEET)
        st.subheader("會員總覽")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"讀取資料失敗: {e}")


def get_coach_list(coach_sheet: str = COACH) -> list[str]:
    df_coach = gr.GET_DF_FROM_DB(sheet=coach_sheet)
    return df_coach["姓名"].tolist()


coach_list = get_coach_list(COACH)


def get_plan_list(menu_sheet: str = MENU) -> list[str]:
    df_menu = gr.GET_DF_FROM_DB(sheet=menu_sheet)
    return set(df_menu["name"].tolist())


plan_list = get_plan_list(MENU)
consume_list = list(plan_list)
consume_list.append("特殊課程")

# --- Page: 首頁總覽 ---
if page == "首頁總覽":
    st.title("📊 首頁總覽")

    if not st.session_state.is_admin:
        password = st.text_input("請輸入管理員密碼以查看資料", type="password")
        if password:
            if password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("輸入錯誤，請重新輸入")

    if st.session_state.is_admin:
        if st.button("登出管理員"):
            st.session_state.is_admin = False
            st.rerun()
        show_main_table()

# --- Page: 新增會員 ---
elif page == "新增會員":
    st.title("👤 新增會員")

    min_date = datetime(1900, 1, 1)
    max_date = datetime.now()

    with st.form("add_member_form"):
        col1, col2 = st.columns(2)
        with col1:
            member_id = st.text_input("會員編號", placeholder='請輸入二至三位數編號（不含教練編號）')
            phone = st.text_input("電話", placeholder='請輸入十位數電話號碼')
            coach = st.selectbox(
                "負責教練", coach_list,
                format_func=lambda x: f"{x}",
                index=None,
                placeholder='請選擇教練')
        with col2:
            name = st.text_input("會員姓名", placeholder='請輸入會員姓名，中英文不限')
            birthday = st.date_input(
                "生日", min_value=min_date, max_value=max_date)

        submitted = st.form_submit_button("確認送出")

        if submitted:
            # Convert date to string
            birthday_str = birthday.strftime("%Y-%m-%d")
            success, msg = A_add_member.add_new_member(
                member_id, name, birthday_str, phone, coach)

            if success:
                st.success(msg)
                # Refresh data
                st.cache_data.clear()
            else:
                st.error(msg)

    st.divider()
    st.subheader("會員列表")
    if st.session_state.is_admin:
        try:
            df_member = gr.GET_DF_FROM_DB(MEMBER_SHEET)
            st.dataframe(df_member, use_container_width=True)
        except Exception as e:
            st.error(f"讀取會員表失敗: {e}")
    else:
        st.info("請先至首頁驗證管理員身份以查看會員列表")

# --- Page: 購買課程 ---
elif page == "購買課程":
    st.title("💰 購買課程")

    purchase_type = st.radio("課程類型", ["一般課程", "特殊課程"], horizontal=True)

    if purchase_type == "一般課程":
        with st.form("purchase_form"):
            col1, col2 = st.columns(2)
            with col1:
                member_id = st.text_input("會員編號", placeholder='請輸入完整會員編號')
                plan = st.selectbox(
                    "購買方案", plan_list, format_func=lambda x: f"{x}", index=None, placeholder='請選擇購買方案')
                payment = st.selectbox(
                    "付款方式", ["現金", "匯款"], index=None, placeholder='請選擇付款方式')
            with col2:
                coach = st.selectbox(
                    "教練", coach_list,
                    format_func=lambda x: f"{x}",
                    index=None,
                    placeholder='請選擇教練')
                count_selection = st.selectbox(
                    "購買堂數", ["1", "4", "8", "16"], index=None, placeholder='請選擇購買堂數')
                account_id = st.text_input(
                    "匯款末五碼", placeholder='輸入匯款帳號末五碼，若是現金付款請留空')

            submitted = st.form_submit_button("確認送出")

            if submitted:
                success, msg = B_purchase.add_purchase_record(
                    member_id, plan, count_selection, payment, coach, account_id
                )

                if success:
                    st.success(msg)
                    st.cache_data.clear()
                else:
                    st.error(msg)
    
    else:  # 特殊課程
        with st.form("customized_purchase_form"):
            col1, col2 = st.columns(2)
            with col1:
                member_id = st.text_input("會員編號", placeholder='請輸入完整會員編號')
                # 特殊課程不需選擇方案，強制固定
                count_selection = st.number_input("購買堂數", step=1, placeholder="請輸入購買堂數")
                payment = st.selectbox(
                    "付款方式", ["現金", "匯款"], index=None, placeholder='請選擇付款方式')

            with col2:
                coach = st.selectbox(
                    "教練", coach_list,
                    format_func=lambda x: f"{x}",
                    index=None,
                    placeholder='請選擇教練')
                price = st.number_input("單堂金額", step=50, placeholder="請輸入單堂金額")
                account_id = st.text_input(
                    "匯款末五碼", placeholder='輸入匯款帳號末五碼，若是現金付款請留空')

            submitted = st.form_submit_button("確認送出")

            if submitted:
                success, msg = E_customized_course.add_customized_course_record(
                    member_id, count_selection, price, payment, coach, account_id
                )

                if success:
                    st.success(msg)
                    st.cache_data.clear()
                else:
                    st.error(msg)

    st.divider()
    show_main_table()

# --- Page: 會員上課 ---
elif page == "會員上課":
    st.title("🏋️ 會員上課 (扣堂)")

    with st.form("consume_form"):
        col1, col2 = st.columns(2)
        with col1:
            member_id = st.text_input("會員編號", placeholder='請輸入完整會員編號')
            coach = st.selectbox(
                "教練", coach_list,
                format_func=lambda x: f"{x}",
                index=None,
                placeholder='請選擇教練')

        with col2:
            plan = st.selectbox(
                "上課方案", consume_list, format_func=lambda x: f"{x}", index=None, placeholder='請選擇上課方案')

        submitted = st.form_submit_button("確認送出")

        if submitted:
            success, msg = C_consume.add_consume_record(member_id, plan, coach)

            if success:
                st.success(msg)
                st.cache_data.clear()
            else:
                st.error(msg)

    st.divider()
    show_main_table()

# --- Page: 手動更新 ---
elif page == "手動更新":
    st.title("🔄 手動更新主表")
    st.info("此功能會重新計算所有交易紀錄並更新主表。")

    if st.button("執行更新"):
        success, msg = D_main_table.D_update_main_data()
        if success:
            st.success(msg)
            st.cache_data.clear()
            show_main_table()
        else:
            st.error(msg)
