from datetime import datetime
import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET


def get_member_stock(member_id: str, plan: str) -> pd.DataFrame:
    """取得特定會員特定方案的庫存狀況"""
    df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
    # 使用 D_main_table 的邏輯計算剩餘堂數
    df_sum = mt.get_sum_table(df_event)

    mask1 = (df_sum["會員編號"] == member_id)
    mask2 = (df_sum["方案"] == plan)

    return df_sum[mask1 & mask2]


def validate_consume_record(member_id: str, plan: str, coach: str) -> tuple[bool, str, dict]:
    """
    驗證上課(扣堂)紀錄
    Returns:
        (success: bool, message: str, data_dict: dict)
    """
    try:
        # 1. 檢查是否有庫存
        df_result = get_member_stock(member_id, plan)

        if df_result.empty:
            return False, "查無此會員該方案的購買紀錄或庫存", {}

        remaining_count = df_result["剩餘堂數"].iloc[0]
        if remaining_count <= 0:
            return False, f"該會員方案已無剩餘堂數 (剩餘: {remaining_count})", {}

        # 2. 準備扣堂資料
        avg_price = float(df_result["平均單堂金額"].iloc[0])
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")
        coach_id, _ = gr.get_coach_id(coach)
        member_name = gr.get_member_name(member_id)

        consume_info = {
            "會員編號": member_id,
            "會員姓名": member_name,
            "方案": plan,
            "堂數": -1,
            "單堂金額": avg_price,
            "方案總金額": (avg_price * -1),
            "教練": coach_id,
            "付款方式": "上課",
            "匯款末五碼": "無",
            "交易日期": today,
            "交易時間": now_time
        }
        
        return True, "驗證成功", consume_info

    except Exception as e:
        return False, f"系統錯誤：{str(e)}", {}


def execute_consume_record(data: dict) -> tuple[bool, str]:
    """
    執行新增上課(扣堂)紀錄
    """
    try:
        # 3. 存檔
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame([data])
        df_event = pd.concat([df_event, df_new], ignore_index=True)

        success, msg = gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

        if success:
            # 4. 更新主表
            try:
                mt.D_update_main_data()
            except Exception as e:
                return True, f"上課紀錄儲存成功，但主表更新失敗: {e}"

            return True, "新增上課紀錄成功！"
        else:
            return False, msg

    except Exception as e:
        return False, f"系統錯誤：{str(e)}"
