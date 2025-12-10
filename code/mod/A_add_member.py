import re
from datetime import datetime
import pandas as pd
from mod import O_general as gr
from mod.O_config import MEMBER_SHEET

def validate_email(email: str) -> bool:
    """驗證email格式"""
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(EMAIL_REGEX, email))

def validate_phone(phone: str) -> bool:
    """驗證電話號碼格式"""
    PHONE_REGEX = r"^(09\d{8}|0\d{1,2}\d{7,8})$"
    return bool(re.fullmatch(PHONE_REGEX, phone))

def validate_birthday(birthday: str) -> str | None:
    """驗證生日格式，若正確回傳 YYYY-MM-DD 字串，否則回傳 None"""
    # 嘗試解析多種格式，這裡假設傳入的是字串
    check = pd.to_datetime(birthday, errors='coerce')
    if pd.notna(check):
        return check.strftime("%Y-%m-%d")
    return None

def check_duplicates(df_member: pd.DataFrame, name: str, email: str) -> list[str]:
    """檢查是否有重複會員，回傳重複的會員資訊列表，若無重複回傳空列表"""
    if df_member.empty:
        return []

    mask_name = (df_member["會員姓名"] == name)
    mask_email = (df_member["Email"] == email)
    
    # 只要姓名和Email同時符合就算重複 (根據原本邏輯 check_and_remove_duplicates)
    # 原本邏輯是 merge inner join on name AND email
    
    duplicates = df_member[mask_name & mask_email]
    
    result = []
    if not duplicates.empty:
        for _, row in duplicates.iterrows():
            result.append(f"{row['會員姓名']} | {row['Email']}")
            
    return result

def add_new_member(name: str, email: str, birthday: str, phone: str) -> tuple[bool, str]:
    """
    新增會員的主要函數
    Args:
        name: 會員姓名
        email: 會員Email
        birthday: 會員生日 (字串或 datetime object)
        phone: 會員電話
    Returns:
        (success: bool, message: str)
    """
    # 1. 基本資料驗證
    if not name:
        return False, "會員姓名不能為空"
        
    if not validate_email(email):
        return False, "Email 格式不正確"
        
    formatted_birthday = validate_birthday(birthday)
    if not formatted_birthday:
        return False, "生日格式不正確"
        
    if not validate_phone(phone):
        return False, "電話格式不正確"

    try:
        # 2. 讀取現有會員資料
        df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        
        # 3. 檢查重複
        duplicates = check_duplicates(df_member, name, email)
        if duplicates:
            msg = "以下會員已存在系統中，無法新增：\n" + "\n".join(duplicates)
            return False, msg

        # 4. 準備新增資料
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        new_member_data = {
            "會員姓名": name,
            "Email": email,
            "生日": formatted_birthday,
            "電話": phone,
            "加入日期": today,
            "加入時間": now_time
        }
        
        df_new = pd.DataFrame([new_member_data])
        
        # 5. 合併並存檔
        df_member = pd.concat([df_member, df_new], ignore_index=True)
        
        success, msg = gr.SAVE_TO_SHEET(df=df_member, sheet=MEMBER_SHEET)
        return success, msg

    except Exception as e:
        return False, f"系統錯誤：{str(e)}"
