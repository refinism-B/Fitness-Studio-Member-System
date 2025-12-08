import pandas as pd
from datetime import datetime
import re


class CancelOperation(Exception):
    """使用者手動取消操作"""
    pass


def check_cancel(check: str):
    """輸入「*」可強制中止並取消當前操作"""
    if check == "*":
        raise CancelOperation("使用者取消")


def input_name():
    """輸入會員姓名"""
    name = input("請輸入會員姓名：")
    check_cancel(check=name)

    return name


def input_email():
    """輸入並驗證email"""
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    while True:
        email = input("請輸入E-mail：")
        check_cancel(check=email)

        if re.fullmatch(EMAIL_REGEX, email):
            return email
        else:
            print("輸入信箱不正確，請重新輸入")


def input_birthday():
    """輸入並驗證生日"""
    while True:
        birthday = input("請輸入會員生日：")
        check_cancel(check=birthday)

        check = pd.to_datetime(birthday, errors='coerce')
        if pd.notna(check):
            birthday_data = check.strftime("%Y-%m-%d")
            return birthday_data
        else:
            print("輸入日期或格式不正確，請重新輸入")


def input_phone():
    """輸入並驗證電話號碼"""
    PHONE_REGEX = r"^(09\d{8}|0\d{1,2}\d{7,8})$"

    while True:
        phone = input("請輸入會員電話：")
        check_cancel(check=phone)

        if re.fullmatch(PHONE_REGEX, phone):
            return phone
        else:
            print("輸入電話格式不正確，請重新輸入")


def input_new_member_data():
    """輸入會員資料以建立會員"""
    # 新增會員
    member_data = {}

    # 輸入會員資料
    # 輸入姓名
    name = input_name()
    member_data["會員姓名"] = name

    # 輸入信箱
    email = input_email()
    member_data["Email"] = email

    # 輸入生日
    birthday = input_birthday()
    member_data["生日"] = birthday

    # 輸入電話
    phone = input_phone()
    member_data["電話"] = phone

    # 設定加入日期及時間
    today = datetime.now().date().strftime("%Y-%m-%d")
    now_time = datetime.now().time().strftime("%H:%M:%S")

    member_data["加入日期"] = today
    member_data["加入時間"] = now_time

    return member_data


def keep_add_or_not():
    """詢問是否繼續新增"""
    while True:
        keep_or_not = input("是否繼續新增會員？[Y/n]").lower()
        if keep_or_not in ["n", ""]:
            return False
        elif keep_or_not == "y":
            return True
        else:
            print("輸入錯誤，請重新輸入")


def build_member():
    """將輸入的資料建立會員"""
    member_list = []

    while True:
        try:
            member_data = input_new_member_data()
            member_list.append(member_data)

            keep = keep_add_or_not()
            if not keep:
                return member_list

        except CancelOperation as e:
            print(f"{e}")
            return member_list


def check_and_remove_duplicates(df_member: pd.DataFrame, df_temp: pd.DataFrame) -> pd.DataFrame:
    """確認是否有重複加入的情形"""
    subset = ["會員姓名", "Email", "生日"]

    df_check = df_temp.merge(df_member[subset], how="inner", on=subset)

    if len(df_check) > 0:
        print("⚠️  以下會員已存在系統中，將不會新增：")
        print("=" * 60)
        for idx, row in df_check.iterrows():
            print(f"• {row['會員姓名']} | {row['Email']} | {row['生日']}")
        print("=" * 60)
        print(f"已去除 {len(df_check)} 筆重複資料\n")

        # 去除重複資料
        df_temp_clean = df_temp.drop(df_check.index)
        return df_temp_clean

    else:
        return df_temp
