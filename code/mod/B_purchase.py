import re
from datetime import datetime

import pandas as pd
from mod import D_main_table as mt
from mod import O_general as gr
from mod.O_config import EVENT_SHEET, MEMBER_SHEET, MENU
from mod.O_general import CancelOperation, InputError, check_cancel

df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)


def check_name_in_member(name: str, df_member: pd.DataFrame) -> bool:
    """驗證姓名是否已是會員"""
    mask1 = (df_member["會員姓名"] == name)
    check_name = df_member[mask1]

    if len(check_name) == 0:
        print("查無此會員姓名，請確認對方是否已加入會員")
        return False

    return True


def check_email_and_name_in_member(email: str, name: str, df_member: pd.DataFrame) -> bool:
    """驗證姓明與信箱是否已是會員"""
    mask1 = (df_member["會員姓名"] == name)
    mask2 = (df_member["Email"] == email)
    check_mail = df_member[mask1 & mask2]

    if len(check_mail) == 0:
        print("查無此會員信箱，請確認是否輸入正確Email或對方已加入會員")
        return False
    elif len(check_mail) > 1:
        print("找到多筆會員資料，請刪除重複資料再繼續")
        return False

    return True


def input_name(df_member: pd.DataFrame):
    """輸入並驗證會員姓名"""
    name = input("請輸入購買會員姓名：")
    check_cancel(check=name)

    if check_name_in_member(name=name, df_member=df_member):
        return True, name
    else:
        return False, None


def input_email(name: str, df_member: pd.DataFrame):
    """輸入並驗證信箱"""
    email = input("請輸入購買會員Email：")
    check_cancel(check=email)

    if check_email_and_name_in_member(email=email, name=name, df_member=df_member):
        return True, email
    else:
        return False, None


def input_plan():
    """選擇購課方案"""
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


def input_count(plan: str):
    """選擇購買堂數"""
    while True:
        count = input("請輸入購買堂數：（A.四堂/B.八堂/C.十六堂（團體方案不適用））")
        check_cancel(check=count)

        if count in ["A", "a", "四堂", "四", "4", 4]:
            return 4
        elif count in ["B", "b", "八堂", "八", "8", 8]:
            return 8
        elif count in ["C", "c", "十六堂", "十六", "16", 16]:
            if plan == "C":
                print("團體課程單次購買上限為八堂，請重新輸入")
            else:
                return 17
        else:
            print("輸入錯誤，請重新輸入")


def input_price(plan: str, count: int):
    """根據方案與堂數取得單價與總價"""
    df_menu = gr.GET_DF_FROM_DB(sheet=MENU)
    df_menu["price"] = df_menu["price"].astype(float)
    # df_menu["total"] = df_menu["total"].astype(int)

    mask1 = (df_menu["plan"] == plan)
    mask2 = (df_menu["count"] == count)
    price = df_menu[mask1 & mask2]["price"].iloc[0]
    # total = df_menu[mask1 & mask2]["total"].iloc[0]
    total = int(price * count)

    return price, total


def input_payment():
    """選擇付款方式"""
    payment = input("請輸入付款方式：（A.現金/B.匯款/C.其他）")
    check_cancel(check=payment)

    if payment in ["A", "a", "現金", "付現"]:
        return "現金"
    elif payment in ["B", "b", "轉帳", "匯款"]:
        return "匯款"
    elif payment in ["C", "c", "其他"]:
        return "其他"


def input_account_id(payment: str):
    """匯款帳號末五碼（僅匯款方式，若其他付款方式則無）"""
    if payment == "現金":
        return "無"
    else:
        while True:
            account_id = input("請輸入付款帳號末五碼：")
            check_cancel(check=account_id)

            ACCOUNT_ID = r"^[0-9]{5}$"
            if re.fullmatch(ACCOUNT_ID, account_id):
                return account_id
            else:
                print("輸入格式錯誤，請重新輸入帳號末五碼")


def purchase_plan(df_member: pd.DataFrame):
    """建立購買訂單"""
    purchase_info = {}

    check, name = input_name(df_member=df_member)
    purchase_info["會員姓名"] = name

    if not check:
        raise InputError("")

    check, email = input_email(name=name, df_member=df_member)
    purchase_info["Email"] = email

    if not check:
        raise InputError("")

    plan = input_plan()
    purchase_info["方案"] = plan

    count = input_count(plan=plan)
    purchase_info["堂數"] = count

    price, total = input_price(plan=plan, count=count)
    purchase_info["單堂金額"] = price
    purchase_info["方案總金額"] = total

    payment = input_payment()
    purchase_info["付款方式"] = payment

    account_id = input_account_id(payment=payment)
    purchase_info["匯款末五碼"] = account_id

    today = datetime.now().date().strftime("%Y-%m-%d")
    now_time = datetime.now().time().strftime("%H:%M:%S")

    purchase_info["交易日期"] = today
    purchase_info["交易時間"] = now_time

    return purchase_info


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


def build_order():
    """建立輸入的訂單資訊"""
    df_member = gr.GET_DF_FROM_DB(sheet=MEMBER_SHEET)

    order_list = []

    while True:
        try:
            purchase_info = purchase_plan(df_member=df_member)
            order_list.append(purchase_info)

            keep = keep_order_or_not()
            if not keep:
                return order_list

        except CancelOperation as e:
            print(f"{e}")
            return order_list

        except InputError as e:
            print(f"{e}")
            return order_list


def B_buy_course_plan():
    # 讀取事件紀錄表
    df_event = gr.GET_DF_FROM_DB(sheet=EVENT_SHEET)

    # 建立訂單列表
    order_list = build_order()

    # 將訂單列表轉換成df
    df_temp = pd.DataFrame(order_list)

    # 將新增訂單與原表合併
    df_event = pd.concat([df_event, df_temp], ignore_index=True)

    # 存檔
    gr.SAVE_TO_SHEET(df=df_event, sheet=EVENT_SHEET)

    # 更新主表
    mt.D_update_main_data()
    print("新增課程購買紀錄，資料已儲存！")
