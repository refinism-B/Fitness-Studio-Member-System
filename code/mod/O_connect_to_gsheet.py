import streamlit as st
from streamlit_gsheets import GSheetsConnection


def conn_to_gsheets():
    """使用st與google sheet建立連線"""
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn


conn = conn_to_gsheets()


def read_sheet_as_df(sheet_name, conn=conn, ttl=0):
    """讀取特定名稱的sheet分頁"""
    df_students = conn.read(worksheet=sheet_name, ttl=ttl)

    return df_students


def read_all_sheets(sheet_list, conn=conn):
    """讀取列表中的所有sheet分頁並存入dict"""
    all_data = {}

    for tab in sheet_list:
        all_data[tab] = conn.read(worksheet=tab, ttl=0)

    return all_data


def update_sheet(sheet_name, updated_df, conn=conn):
    conn.update(
        worksheet=sheet_name,
        data=updated_df
    )
