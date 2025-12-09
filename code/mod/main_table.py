import pandas as pd


def get_sum_table(df_event: pd.DataFrame) -> pd.DataFrame:
    df_sum = (df_event.groupby(["會員姓名", "Email", "方案"]).agg(
        剩餘堂數=("堂數", "sum"),
        剩餘預收款項=("方案總金額", "sum"),
        最近交易日期=("交易日期", "last")
    ).reset_index()
    )

    df_sum["平均單堂金額"] = (df_sum["剩餘預收款項"] / df_sum["剩餘堂數"]).round(2)
    new_cols = ['會員姓名', 'Email', '方案', '剩餘堂數', '平均單堂金額', '剩餘預收款項', '最近交易日期']
    df_sum = df_sum[new_cols]

    return df_sum


def get_df_main(df_event: pd.DataFrame, de_member: pd.DataFrame) -> pd.DataFrame:
    df_sum = get_sum_table(df_event=df_event)

    df_member = df_member[['會員姓名', 'Email', '生日', '電話']]

    df_main = df_member.merge(df_sum, how="inner", on=['會員姓名', 'Email'])

    df_main = df_main.sort_values(by="會員姓名", ignore_index=True)

    return df_main
