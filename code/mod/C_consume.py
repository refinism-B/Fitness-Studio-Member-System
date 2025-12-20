from datetime import datetime
import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET


def get_member_stock(member_id: str, plan: str, df_event: pd.DataFrame = None) -> pd.DataFrame:
    """取得特定會員特定方案的庫存狀況"""
    if df_event is None:
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
    # 使用 D_main_table 的邏輯計算剩餘堂數
    df_sum = mt.get_sum_table(df_event)

    mask1 = (df_sum["會員編號"] == member_id)
    mask2 = (df_sum["方案"] == plan)

    return df_sum[mask1 & mask2]


def validate_consume_record(member_id_list: list[str], plan: str, coach: str, remarks: str = "", df_event: pd.DataFrame = None, df_member: pd.DataFrame = None, df_coach: pd.DataFrame = None) -> tuple[bool, str, dict]:
    """
    驗證上課(扣堂)紀錄 - 支援批次處理
    Args:
        member_id_list: 會員編號列表
        plan: 方案
        coach: 教練
    Returns:
        (success: bool, message: str, data_dict: dict)
    """
    try:
        if not member_id_list:
            return False, "請至少選擇一位會員", {}

        batch_data = []
        error_messages = []

        batch_data = []
        error_messages = []

        # 取得教練ID一次即可
        coach_id, _ = gr.get_coach_id(coach, df_coach=df_coach)
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        for member_id in member_id_list:
            # 1. 檢查是否有庫存
            df_result = get_member_stock(member_id, plan, df_event=df_event)
            try:
                member_name = gr.get_member_name(member_id, df_member=df_member)
            except Exception:
                member_name = "未知會員"

            if df_result.empty:
                error_messages.append(f"{member_id} ({member_name}): 查無該方案購買紀錄")
                continue

            remaining_count = df_result["剩餘堂數"].iloc[0]
            if remaining_count <= 0:
                error_messages.append(f"{member_id} ({member_name}): 剩餘堂數不足 ({remaining_count})")
                continue

            # 2. 準備扣堂資料
            avg_price = float(df_result["平均單堂金額"].iloc[0])
            
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
                "交易時間": now_time,
                "備註": remarks
            }
            batch_data.append(consume_info)

        if error_messages:
            full_msg = "資料存取失敗：\n" + "\n".join(error_messages)
            return False, full_msg, {}

        return True, "驗證成功", {"batch_list": batch_data}

    except Exception as e:
        return False, f"系統錯誤：{str(e)}", {}


def execute_consume_record(data: dict, df_event: pd.DataFrame = None, df_member: pd.DataFrame = None) -> tuple[bool, str]:
    """
    執行新增上課(扣堂)紀錄 - 支援批次
    Args:
        data: 包含 "batch_list" key 的字典，或單一 record (兼容舊格式)
    """
    try:
        # 3. 準備寫入資料
        records = []
        if "batch_list" in data:
            records = data["batch_list"]
        else:
            records = [data]

        if df_event is None:
            df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame(records)
        df_event = pd.concat([df_event, df_new], ignore_index=True)

        success, msg = gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

        if success:
            # 4. 更新主表
            try:
                mt.D_update_main_data(df_event=df_event, df_member=df_member)
            except Exception as e:
                return True, f"上課紀錄儲存成功，但主表更新失敗: {e}"

            count = len(records)
            return True, f"成功新增 {count} 筆上課紀錄！"
        else:
            return False, msg

    except Exception as e:
        return False, f"系統錯誤：{str(e)}"
