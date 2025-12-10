import streamlit as st
import pandas as pd
import sys
import os

# Add 'code' directory to sys.path to allow importing 'mod'
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from mod import A_add_member
from mod import B_purchase
from mod import C_consume
from mod import D_main_table
from mod import O_general as gr
from mod.O_config import MAIN_SHEET, MEMBER_SHEET, EVENT_SHEET

st.set_page_config(page_title="沛力訓練會員系統", layout="wide")

# Sidebar Navigation
st.sidebar.title("功能選單")
page = st.sidebar.radio(
    "請選擇操作：",
    ["首頁總覽", "新增會員", "購買課程", "會員上課", "手動更新"]
)

def show_main_table():
    try:
        df = gr.GET_DF_FROM_DB(MAIN_SHEET)
        st.subheader("會員總覽")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"讀取資料失敗: {e}")

# --- Page: 首頁總覽 ---
if page == "首頁總覽":
    st.title("📊 首頁總覽")
    show_main_table()

# --- Page: 新增會員 ---
elif page == "新增會員":
    st.title("👤 新增會員")
    
    with st.form("add_member_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("會員姓名")
            phone = st.text_input("電話")
        with col2:
            email = st.text_input("Email")
            birthday = st.date_input("生日")
            
        submitted = st.form_submit_button("確認送出")
        
        if submitted:
            # Convert date to string
            birthday_str = birthday.strftime("%Y-%m-%d")
            success, msg = A_add_member.add_new_member(name, email, birthday_str, phone)
            
            if success:
                st.success(msg)
                # Refresh data
                st.cache_data.clear()
            else:
                st.error(msg)
    
    st.divider()
    st.subheader("會員列表")
    try:
        df_member = gr.GET_DF_FROM_DB(MEMBER_SHEET)
        st.dataframe(df_member, use_container_width=True)
    except Exception as e:
        st.error(f"讀取會員表失敗: {e}")

# --- Page: 購買課程 ---
elif page == "購買課程":
    st.title("💰 購買課程")
    
    with st.form("purchase_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("會員姓名")
            plan = st.selectbox("購買方案", ["A", "B", "C"], format_func=lambda x: f"{x} 方案")
            payment = st.selectbox("付款方式", ["現金", "匯款", "其他"])
        with col2:
            email = st.text_input("Email")
            count_selection = st.selectbox("購買堂數", ["4", "8", "16"])
            account_id = st.text_input("匯款末五碼 (若非匯款請留空)")
            
        submitted = st.form_submit_button("確認送出")
        
        if submitted:
            success, msg = B_purchase.add_purchase_record(
                name, email, plan, count_selection, payment, account_id
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
            name = st.text_input("會員姓名")
            plan = st.selectbox("上課方案", ["A", "B", "C"], format_func=lambda x: f"{x} 方案")
        with col2:
            email = st.text_input("Email")
            
        submitted = st.form_submit_button("確認送出")
        
        if submitted:
            success, msg = C_consume.add_consume_record(name, email, plan)
            
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
