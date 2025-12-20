import pandas as pd
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MAIN_SHEET, MEMBER_SHEET


def get_sum_table(df_event: pd.DataFrame) -> pd.DataFrame:
    df_sum = (df_event.groupby(["會員編號", "方案"]).agg(
        剩餘堂數=("堂數", "sum"),
        剩餘預收款項=("方案總金額", "sum"),
        最近交易日期=("交易日期", "last")
    ).reset_index()
    )

    # Avoid division by zero
    df_sum["平均單堂金額"] = df_sum.apply(
        lambda x: (x["剩餘預收款項"] / x["剩餘堂數"]) if x["剩餘堂數"] != 0 else 0, axis=1
    ).round(2)
    
    new_cols = ['會員編號', '方案', '剩餘堂數', '平均單堂金額', '剩餘預收款項', '最近交易日期']
    df_sum = df_sum[new_cols]

    return df_sum


def get_df_main(df_event: pd.DataFrame, df_member: pd.DataFrame) -> pd.DataFrame:
    df_sum = get_sum_table(df_event=df_event)

    df_member = df_member[['會員編號', '會員姓名', '生日', '電話']]

    df_main = df_member.merge(df_sum, how="inner", on=['會員編號'])

    df_main = df_main.sort_values(by="會員編號", ignore_index=True)

    return df_main


def D_update_main_data(df_event: pd.DataFrame = None, df_member: pd.DataFrame = None):
    try:
        # 讀入事件紀錄表
        if df_event is None:
            df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)

        # 讀入會員表
        if df_member is None:
            df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)

        # 重新計算main表
        df_main = get_df_main(df_event=df_event, df_member=df_member)

        # 存檔
        success, msg = gr.SAVE_TO_SHEET(df=df_main, sheet=MAIN_SHEET)
        return success, msg

    except Exception as e:
        return False, f"更新主表失敗: {str(e)}"
