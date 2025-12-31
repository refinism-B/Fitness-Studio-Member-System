import re
from datetime import datetime
import pandas as pd
from mod import O_general as gr
from mod.O_config import MEMBER_SHEET, COACH

# def validate_email(email: str) -> bool:
#     """驗證email格式"""
#     EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return bool(re.fullmatch(EMAIL_REGEX, email))


def validate_member_id(member_id: str) -> bool:
    """驗證會員ID格式"""
    MEMBER_ID_REGEX = r"[0-9]{2,3}"
    return bool(re.fullmatch(MEMBER_ID_REGEX, member_id))


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


# def get_coach_id(coach: str) -> str:
#     df_coach = gr.GET_DF_FROM_DB(sheet=COACH)
#     mask = (df_coach["姓名"] == coach)
#     coach_id = df_coach[mask]["教練編號"].iloc[0]
#     coach_str = df_coach[mask]["會員編號"].iloc[0]
#     return coach_id, coach_str


def check_duplicates(df_member: pd.DataFrame, name: str, birthday: str, member_id: str = None) -> list[str]:
    """檢查是否有重複會員，回傳重複的會員資訊列表，若無重複回傳空列表"""
    if df_member.empty:
        return []

    mask_name = (df_member["會員姓名"] == name)
    mask_birthday = (df_member["生日"] == birthday)

    # 只要姓名和Email同時符合就算重複 (根據原本邏輯 check_and_remove_duplicates)
    # 原本邏輯是 merge inner join on name AND birthday

    duplicates = df_member[mask_name & mask_birthday]

    result = []
    if not duplicates.empty:
        for _, row in duplicates.iterrows():
            result.append(f"{row['會員姓名']} | {row['電話']}")

    # 檢查 id 是否重複
    if member_id:
        mask_id = (df_member["會員編號"] == member_id)
        if not df_member[mask_id].empty:
            result.append(f"會員編號重複 {member_id}")

    return result


def validate_add_member(member_id: str, name: str, birthday: str, phone: str, coach: str, remarks: str = "", df_member: pd.DataFrame = None, df_coach: pd.DataFrame = None) -> tuple[bool, str, dict]:
    """
    驗證新增會員資料
    Returns:
        (success: bool, message: str, data_dict: dict)
    """
    # 1. 基本資料驗證
    if not validate_member_id(member_id):
        return False, "會員編號格式不正確", {}

    if not name:
        return False, "會員姓名不能為空", {}

    formatted_birthday = validate_birthday(birthday)
    if not formatted_birthday:
        return False, "生日格式不正確", {}

    if not validate_phone(phone):
        return False, "電話格式不正確", {}

    try:
        # 2. 讀取現有會員資料
        if df_member is None:
            df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        try:
            coach_id, coach_str = gr.get_coach_id(coach, df_coach=df_coach)
            member_id_formatted = str(coach_str).replace(".0", "") + str(member_id)
        except Exception as e:
            return False, f"取得教練資料失敗: {str(e)}", {}

        # 3. 檢查重複
        duplicates = check_duplicates(df_member, name, formatted_birthday, member_id_formatted)
        if duplicates:
            msg = "無法新增會員資料：\n" + "\n".join(duplicates)
            return False, msg, {}

        # 4. 準備新增資料
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        new_member_data = {
            "會員編號": member_id_formatted,
            "會員姓名": name,
            "生日": formatted_birthday,
            "電話": phone,
            "教練": coach_id,
            "教練": coach_id,
            "加入日期": today,
            "加入時間": now_time,
            "備註": remarks
        }
        
        return True, "驗證成功", new_member_data

    except Exception as e:
        return False, f"系統錯誤：{str(e)}", {}


def execute_add_member(data: dict, df_member: pd.DataFrame = None) -> tuple[bool, str]:
    """
    執行新增會員資料
    """
    try:
        if df_member is None:
            df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        df_new = pd.DataFrame([data])
        
        # 5. 合併並存檔
        df_member = pd.concat([df_member, df_new], ignore_index=True)
        success, msg = gr.SAVE_TO_SHEET(df=df_member, sheet=MEMBER_SHEET)
        return success, msg
    except Exception as e:
        return False, f"儲存失敗：{str(e)}"
