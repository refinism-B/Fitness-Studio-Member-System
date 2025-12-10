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

def get_price_and_total(plan: str, count: int) -> tuple[float, int]:
    """取得單價與總價"""
    df_menu = gr.GET_DF_FROM_DB(sheet=MENU)
    df_menu["price"] = df_menu["price"].astype(float)
    
    # 注意：這裡假設 Menu 表中的 count 對應的是實際堂數 (例如 17)
    # 如果 Menu 表中是 16，但這裡傳入 17，會找不到資料。
    # 根據舊代碼邏輯，它傳入的是 input_count 的回傳值 (即 17)。
    # 因此假設 Menu 表中有 17 這個選項，或者舊代碼原本就會報錯。
    # 為了保險起見，若找不到 17，嘗試找 16 (假設是買16送1)
    
    mask1 = (df_menu["plan"] == plan)
    mask2 = (df_menu["count"] == count)
    
    result = df_menu[mask1 & mask2]
    
    if result.empty and count == 17:
        # Fallback logic: try finding 16 and calculate based on that
        mask2_fallback = (df_menu["count"] == 16)
        result = df_menu[mask1 & mask2_fallback]
        
    if result.empty:
        raise ValueError(f"找不到對應的價格設定: 方案{plan}, 堂數{count}")

    price = result["price"].iloc[0]
    # 總價計算：舊代碼是 price * count。如果是買16送1(17堂)，價格應該是 16堂的價格還是 17*單價?
    # 舊代碼: total = int(price * count)
    # 這意味著如果是 17 堂，總價就是 17 * 單價。這表示不是送的，是買 17 堂。
    total = int(price * count)

    return price, total

def add_purchase_record(name: str, email: str, plan: str, count_selection: str, payment: str, account_id: str = "無") -> tuple[bool, str]:
    """
    新增購買紀錄
    Args:
        name: 會員姓名
        email: 會員Email
        plan: 方案 (A/B/C)
        count_selection: 購買堂數選項 ("4", "8", "16")
        payment: 付款方式 (現金/匯款/其他)
        account_id: 匯款末五碼
    """
    try:
        # 1. 驗證會員是否存在
        df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
        mask_member = (df_member["會員姓名"] == name) & (df_member["Email"] == email)
        if df_member[mask_member].empty:
            return False, "查無此會員資料 (姓名與Email不符或不存在)"
        
        if len(df_member[mask_member]) > 1:
            return False, "系統中存在重複會員資料，請先清理資料庫"

        # 2. 轉換堂數邏輯 (保留舊代碼邏輯)
        # count_selection 預期是 "4", "8", "16" (來自前端選單)
        try:
            count_input = int(count_selection)
        except ValueError:
             return False, "堂數格式錯誤"

        final_count = count_input
        if count_input == 16:
            if plan == "C": # 團體課
                return False, "團體課程單次購買上限為八堂"
            else:
                final_count = 17 # 舊代碼邏輯：選16變17

        # 3. 驗證付款資訊
        if payment == "匯款" and not validate_account_id(payment, account_id):
            return False, "匯款方式必須輸入正確的末五碼 (5位數字)"
        
        if payment != "匯款":
            account_id = "無"

        # 4. 計算價格
        try:
            price, total = get_price_and_total(plan, final_count)
        except ValueError as e:
            return False, str(e)

        # 5. 準備資料
        today = datetime.now().date().strftime("%Y-%m-%d")
        now_time = datetime.now().time().strftime("%H:%M:%S")

        purchase_info = {
            "會員姓名": name,
            "Email": email,
            "方案": plan,
            "堂數": final_count,
            "單堂金額": price,
            "方案總金額": total,
            "付款方式": payment,
            "匯款末五碼": account_id,
            "交易日期": today,
            "交易時間": now_time
        }

        # 6. 存檔
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
        df_new = pd.DataFrame([purchase_info])
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
