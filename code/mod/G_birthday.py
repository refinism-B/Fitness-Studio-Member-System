from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MEMBER_SHEET
from datetime import datetime
import pandas as pd


def get_birthday_member(df_event: pd.DataFrame = None, df_member: pd.DataFrame = None):
    if df_event is None:
        df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
    if df_member is None:
        df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)
    df_member["生日"] = pd.to_datetime(df_member["生日"])

    month = datetime.now().month
    mask = (df_member["生日"].dt.month == month)
    df_birthday = df_member[mask]

    df_main = mt.get_df_main(df_event=df_event, df_member=df_member)

    df_birthday = df_birthday.merge(df_main, how="inner", on=[
                                    "會員編號", "會員姓名", "生日", "電話"])
    df_birthday["生日"] = df_birthday["生日"].dt.date
    new_cols = ['會員編號', '會員姓名', '生日', '電話', '教練', '方案',
                '剩餘堂數', '平均單堂金額', '剩餘預收款項', '最近交易日期', '加入日期', '加入時間']

    df_birthday = df_birthday[new_cols]

    return df_birthday
