from datetime import datetime

import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET
from mod.O_general import CancelOperation, InputError, check_cancel


def check_name_purchase(name: str, df_event: pd.DataFrame) -> bool:
    mask = (df_event["會員姓名"] == name)
    check_name = df_event[mask]

    if len(check_name) == 0:
        print("查無購買紀錄，請確認會員姓名是否正確")
        return False

    return True


def input_name(df_event: pd.DataFrame):
    name = input("請輸入上課會員姓名：")
    check_cancel(check=name)

    if check_name_purchase(name=name, df_event=df_event):
        return True, name
    else:
        return False, None


def check_email_purchase(name: str, email: str, df_event: pd.DataFrame) -> bool:
    mask1 = (df_event["會員姓名"] == name)
    mask2 = (df_event["Email"] == email)
    check_mail = df_event[mask1 & mask2]

    if len(check_mail) == 0:
        print("查無信箱購買紀錄，請確認會員Email是否正確")
        return False

    return True


def input_email(name: str, df_event: pd.DataFrame):
    email = input("請輸入上課會員的Email：")
    check_cancel(check=email)

    if check_email_purchase(name=name, email=email, df_event=df_event):
        return True, email
    else:
        return False, None


def input_plan():
    while True:
        plan = input("請輸入購買方案：（A.一對一/B.一對二/C.團體）")
        check_cancel(check=plan)

        if plan in ["A", "a", "一對一"]:
            return "A"
        elif plan in ["B", "b", "一對二"]:
            return "B"
        elif plan in ["C", "c", "團體", "團課", "團體課程"]:
            return "C"
        else:
            print("輸入錯誤，請重新輸入")


def calculate_sum(df_event: pd.DataFrame):
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


def search_result(df_sum: pd.DataFrame, name: str, email: str, plan: str) -> pd.DataFrame:
    mask1 = (df_sum["會員姓名"] == name)
    mask2 = (df_sum["Email"] == email)
    mask3 = (df_sum["方案"] == plan)
    df_result = df_sum[mask1 & mask2 & mask3]

    return df_result


def check_stock(df_result: pd.DataFrame) -> bool:
    if len(df_result) > 0 and (df_result["剩餘堂數"] > 0).any():
        return True
    else:
        return False


def input_consume_record(name: str, email: str, plan: str, df_result: pd.DataFrame) -> dict:
    price = float(df_result["平均單堂金額"].iloc[0])
    today = datetime.now().date().strftime("%Y-%m-%d")
    now_time = datetime.now().time().strftime("%H:%M:%S")

    consume_info = {
        "會員姓名": name,
        "Email": email,
        "方案": plan,
        "堂數": -1,
        "單堂金額": price,
        "方案總金額": (price*(-1)),
        "付款方式": "上課",
        "匯款末五碼": "無",
        "交易日期": today,
        "交易時間": now_time
    }

    return consume_info


def keep_order_or_not():
    """確認是否繼續建立訂單"""
    while True:
        keep_or_not = input("是否繼續新增購買訂單？[Y/n]").lower()
        if keep_or_not in ["n", ""]:
            return False
        elif keep_or_not == "y":
            return True
        else:
            print("輸入錯誤，請重新輸入")


def build_consume_record(df_event: pd.DataFrame, df_sum: pd.DataFrame):
    check, name = input_name(df_event=df_event)

    if not check:
        raise InputError("")

    check, email = input_email(name=name, df_event=df_event)

    if not check:
        raise InputError("")

    plan = input_plan()

    df_result = search_result(df_sum=df_sum, name=name, email=email, plan=plan)

    if not check_stock(df_result=df_result):
        raise InputError("該會員該方案已無剩餘堂數，請確認後重新輸入")

    consume_record = input_consume_record(
        name=name, email=email, plan=plan, df_result=df_result)

    return consume_record


def build_consume_list():
    df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)
    df_sum = calculate_sum(df_event=df_event)

    consume_list = []

    while True:
        try:
            consume_record = build_consume_record(
                df_event=df_event, df_sum=df_sum)
            consume_list.append(consume_record)

            keep = keep_order_or_not()
            if not keep:
                return consume_list

        except CancelOperation as e:
            print(f"{e}")
            return consume_list

        except InputError as e:
            print(f"{e}")
            return consume_list


def C_consume_course():
    # 讀取會員表
    df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)

    # 輸入消費資料，建立列表
    consume_list = build_consume_list()

    # 組成暫時df
    df_temp = pd.DataFrame(consume_list)

    # 與主表合併
    df_event = pd.concat([df_event, df_temp], ignore_index=True)

    # 存檔
    gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

    # 更新主表
    mt.D_update_main_data()
    print("新增上課紀錄，資料已儲存！")
