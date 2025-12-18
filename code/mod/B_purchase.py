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


def get_price_and_total(plan: str, count: int, df_menu: pd.DataFrame = None) -> tuple[float, int]:
    """取得單價與總價"""

    if df_menu is None:
        df_menu = gr.GET_DF_FROM_DB(sheet=MENU)
    df_menu["price"] = df_menu["price"].astype(float)

    # 嘗試直接對應 Plan 與 Count
    mask1 = (df_menu["name"] == plan)
    mask2 = (df_menu["count"] == count)
    result = df_menu[mask1 & mask2]

    # Fallback logic for 17 classes (Buy 16 Get 1 Free)
    if result.empty and count == 17:
        mask2_fallback = (df_menu["count"] == 16)
        result = df_menu[mask1 & mask2_fallback]

    if result.empty:
        raise ValueError(f"找不到對應的價格設定: 方案{plan}, 堂數{count}")

    price = result["price"].iloc[0]
    total = int(price * count)

    return price, total


def validate_purchase_record(member_id: str, plan: str, count_selection: str, payment: str, coach: str, account_id: str = "無", remarks: str = "", df_member: pd.DataFrame = None, df_menu: pd.DataFrame = None, df_coach: pd.DataFrame = None) -> tuple[bool, str, dict]:
    """
    驗證購買紀錄
    Returns:
        (success: bool, message: str, data_dict: dict)
    """
    try:
        # 1. 驗證會員是否存在
        if df_member is None:
            df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        mask_member = (df_member["會員編號"] == member_id)
        if df_member[mask_member].empty:
            return False, "查無此會員資料 (姓名與Email不符或不存在)", {}

        if len(df_member[mask_member]) > 1:
            return False, "系統中存在重複會員資料，請先清理重複會員資料", {}

        # 2. 轉換堂數邏輯
        # count_selection 預期是 "1", "4", "8", "16"
        try:
            count_input = int(count_selection)
        except ValueError:
            return False, "堂數格式錯誤", {}

        final_count = count_input
        if count_input == 16:
            if plan == "C":  # 團體課
                return False, "團體課程單次購買上限為八堂", {}
            else:
                final_count = 17  # 買16送1

        # 3. 驗證付款資訊
        if payment == "匯款" and not validate_account_id(payment, account_id):
            return False, "匯款方式必須輸入正確的末五碼 (5位數字)", {}

        if payment != "匯款":
            account_id = "無"

        # 4. 計算價格
        try:
            price, total = get_price_and_total(plan, final_count, df_menu=df_menu)
        except ValueError as e:
            return False, str(e), {}

        # 5. 準備資料
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")
        coach_id, _ = gr.get_coach_id(coach, df_coach=df_coach)
        member_name = gr.get_member_name(member_id, df_member=df_member)

        purchase_info = {
            "會員編號": member_id,
            "會員姓名": member_name,
            "方案": plan,
            "堂數": final_count,
            "單堂金額": price,
            "方案總金額": total,
            "教練": coach_id,
            "付款方式": payment,
            "匯款末五碼": account_id,
            "交易日期": today,
            "交易時間": now_time,
            "備註": remarks
        }
        
        return True, "驗證成功", purchase_info

    except Exception as e:
        return False, f"系統錯誤：{str(e)}", {}


def execute_purchase_record(data: dict, df_event: pd.DataFrame = None, df_member: pd.DataFrame = None) -> tuple[bool, str]:
    """
    執行新增購買紀錄
    """
    try:
        # 6. 存檔
        if df_event is None:
            df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame([data])
        df_event = pd.concat([df_event, df_new], ignore_index=True)

        success, msg = gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

        if success:
            # 7. 更新主表
            try:
                # Pass updated df_event and (cached or loaded) df_member to update function
                mt.D_update_main_data(df_event=df_event, df_member=df_member)
            except Exception as e:
                return True, f"購買紀錄儲存成功，但主表更新失敗: {e}"

            return True, "新增課程購買紀錄成功！"
        else:
            return False, msg

    except Exception as e:
        return False, f"系統錯誤：{str(e)}"
