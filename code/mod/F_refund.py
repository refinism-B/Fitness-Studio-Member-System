from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MEMBER_SHEET
from datetime import datetime
import pandas as pd


def get_member_stock(member_id: str, plan: str, df_event: pd.DataFrame = None, df_member: pd.DataFrame = None):
    """取得特定會員特定方案的庫存狀況"""
    try:
        if df_event is None:
            df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        if df_member is None:
            df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        df_main = mt.get_df_main(df_event=df_event, df_member=df_member)

        mask1 = (df_main["會員編號"] == member_id)
        mask2 = (df_main["方案"] == plan)
        result = df_main[mask1 & mask2]
        return result
    except Exception as e:
        return pd.DataFrame()


def validate_refund(member_id: str, plan: str, coach_name: str, df_event: pd.DataFrame = None, df_member: pd.DataFrame = None, df_coach: pd.DataFrame = None) -> tuple[bool, str, dict]:
    """
    驗證退款資料
    Args:
        member_id: 會員編號
        plan: 方案
        coach_name: 教練姓名
    """
    try:
        if not member_id or not plan or not coach_name:
            return False, "請完整填寫所有欄位（會員、方案、教練）", {}

        result = get_member_stock(member_id, plan, df_event=df_event, df_member=df_member)

        if result.empty:
            return False, "查無該會員此方案的紀錄", {}

        # 取得基本資料
        name = result["會員姓名"].iloc[0]
        remaining_count = result["剩餘堂數"].iloc[0]
        remaining_total = result["剩餘預收款項"].iloc[0]

        if remaining_count == 0 and remaining_total == 0:
            return False, "該方案已無剩餘堂數與款項，無法退款", {}
        
        if remaining_count < 0 or remaining_total < 0:
             return False, "該方案數據異常（為負數），請先檢查數據", {}

        # 計算退款資料 (全退)
        refund_count = remaining_count * (-1)
        refund_total = remaining_total * (-1)
        
        # 避免除以零
        if remaining_count > 0:
            price = round((remaining_total / remaining_count), 2)
        else:
            price = 0

        coach_id, _ = gr.get_coach_id(coach=coach_name, df_coach=df_coach)
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        refund_data = {
            '會員編號': member_id,
            '會員姓名': name,
            '方案': plan,
            '堂數': refund_count,
            '單堂金額': price,
            '方案總金額': refund_total,
            '教練': coach_id,
            '付款方式': "退款",
            '匯款末五碼': "無",
            '交易日期': today,
            '交易時間': now_time,
            # 前端顯示用
            # '顯示_剩餘堂數': remaining_count,
            # '顯示_剩餘金額': remaining_total,
            # '顯示_教練姓名': coach_name
        }

        return True, "驗證成功，請確認退款資料", refund_data

    except Exception as e:
        return False, f"驗證過程發生錯誤: {str(e)}", {}


def execute_refund(data: dict, df_event: pd.DataFrame = None, df_member: pd.DataFrame = None) -> tuple[bool, str]:
    """
    執行退款寫入
    """
    try:
        # 移除僅供顯示用的欄位
        record = data.copy()
        keys_to_remove = [k for k in record.keys() if k.startswith("顯示_")]
        for k in keys_to_remove:
            del record[k]

        refund_record = [record]
        
        if df_event is None:
            df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_refund = pd.DataFrame(refund_record)
        df_event = pd.concat([df_event, df_refund], ignore_index=True)

        success, msg = gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

        if success:
             # 更新主表
            try:
                mt.D_update_main_data(df_event=df_event, df_member=df_member)
            except Exception as e:
                return True, f"退款紀錄儲存成功，但主表更新失敗: {e}"
            
            return True, "退款成功！已歸零該方案剩餘堂數與款項。"
        else:
            return False, msg

    except Exception as e:
        return False, f"執行失敗: {str(e)}"
