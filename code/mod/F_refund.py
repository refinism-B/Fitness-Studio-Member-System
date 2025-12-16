from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MEMBER_SHEET
from datetime import datetime
import pandas as pd


df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
df_main = mt.get_df_main(df_event=df_event, df_member=df_member)

member_id = input("請輸入會員id：")
plan = input("請輸入退款方案：")
mask1 = (df_main["會員編號"] == member_id)
mask2 = (df_main["方案"] == plan)
result = df_main[mask1 & mask2]

print(result)

refund = input("是否確認退款？[Y/n]")
if refund in ["Y", "y"]:
    name = result["會員姓名"]
    plan = result["方案"]
    coach_id = gr.get_coach_id(coach=coach)
    today = datetime.now().date().strftime("%Y-%m-%d")
    now_time = datetime.now().time().strftime("%H:%M:%S")

    count = result["剩餘堂數"]
    if count > 0:
        refund_count = count * (-1)

    total = result["剩餘預收款項"]
    if total > 0:
        refund_total = total * (-1)

    price = total / count

    refund_record = [{
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
        '交易時間': now_time
    }]

    df_refund = pd.DataFrame(refund_record)

    df_event = pd.concat([df_event, df_refund], ignore_index=True)
