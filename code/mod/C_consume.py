from datetime import datetime
import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET

def get_member_stock(name: str, email: str, plan: str) -> pd.DataFrame:
    """取得特定會員特定方案的庫存狀況"""
    df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
    # 使用 D_main_table 的邏輯計算剩餘堂數
    df_sum = mt.get_sum_table(df_event)
    
    mask1 = (df_sum["會員姓名"] == name)
    mask2 = (df_sum["Email"] == email)
    mask3 = (df_sum["方案"] == plan)
    
    return df_sum[mask1 & mask2 & mask3]

def add_consume_record(name: str, email: str, plan: str) -> tuple[bool, str]:
    """
    新增上課(扣堂)紀錄
    Args:
        name: 會員姓名
        email: 會員Email
        plan: 方案 (A/B/C)
    """
    try:
        # 1. 檢查是否有庫存
        df_result = get_member_stock(name, email, plan)
        
        if df_result.empty:
            return False, "查無此會員該方案的購買紀錄或庫存"
            
        remaining_count = df_result["剩餘堂數"].iloc[0]
        if remaining_count <= 0:
            return False, f"該會員方案已無剩餘堂數 (剩餘: {remaining_count})"
            
        # 2. 準備扣堂資料
        avg_price = float(df_result["平均單堂金額"].iloc[0])
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        consume_info = {
            "會員姓名": name,
            "Email": email,
            "方案": plan,
            "堂數": -1,
            "單堂金額": avg_price,
            "方案總金額": (avg_price * -1),
            "付款方式": "上課",
            "匯款末五碼": "無",
            "交易日期": today,
            "交易時間": now_time
        }

        # 3. 存檔
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame([consume_info])
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
