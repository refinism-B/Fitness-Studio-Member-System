import re
from datetime import datetime
import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MEMBER_SHEET, MENU


def validate_account_id(payment: str, account_id: str) -> bool:
    """驗證匯款帳號末五碼"""
    if payment == "匯款":
        return bool(re.fullmatch(r"^[0-9]{5}$", account_id))
    return True


def validate_customized_course_record(member_id: str, count_selection: int, price: int, payment: str, coach: str, account_id: str = "無") -> tuple[bool, str, dict]:
    """
    驗證新增購買紀錄
    Returns:
        (success: bool, message: str, data_dict: dict)
    """
    try:
        # 1. 驗證會員是否存在
        df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        mask_member = (df_member["會員編號"] == member_id)
        if df_member[mask_member].empty:
            return False, "查無此會員資料 (姓名與Email不符或不存在)", {}

        if len(df_member[mask_member]) > 1:
            return False, "系統中存在重複會員資料，請先清理重複會員資料", {}

        # 2. 計算堂數與金額
        try:
            count_input = int(count_selection)
            if count_input <= 0:
                raise ValueError
        except ValueError:
            return False, "堂數必須為正整數", {}

        try:
            price_input = int(price)
            if price_input <= 0:
                raise ValueError
        except ValueError:
            return False, "單堂金額必須為正整數", {}

        total = int(count_input * price_input)

        # 3. 驗證付款資訊
        if payment == "匯款" and not validate_account_id(payment, account_id):
            return False, "匯款方式必須輸入正確的末五碼 (5位數字)", {}

        if payment != "匯款":
            account_id = "無"

        # 5. 準備資料
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")
        coach_id, _ = gr.get_coach_id(coach)
        member_name = gr.get_member_name(member_id)

        purchase_info = {
            "會員編號": member_id,
            "會員姓名": member_name,
            "方案": "特殊課程",
            "堂數": count_input,
            "單堂金額": price_input,
            "方案總金額": total,
            "教練": coach_id,
            "付款方式": payment,
            "匯款末五碼": account_id,
            "交易日期": today,
            "交易時間": now_time
        }
        
        return True, "驗證成功", purchase_info

    except Exception as e:
        return False, f"系統錯誤：{str(e)}", {}


def execute_customized_course_record(data: dict) -> tuple[bool, str]:
    """
    執行新增購買紀錄
    """
    try:
        # 6. 存檔
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame([data])
        df_event = pd.concat([df_event, df_new], ignore_index=True)

        success, msg = gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

        if success:
            # 7. 更新主表
            try:
                mt.D_update_main_data()
            except Exception as e:
                return True, f"購買紀錄儲存成功，但主表更新失敗: {e}"

            return True, "新增課程購買紀錄成功！"
        else:
            return False, msg

    except Exception as e:
        return False, f"系統錯誤：{str(e)}"
