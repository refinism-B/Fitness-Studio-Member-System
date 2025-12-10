from mod import A_add_member as add
from mod import B_purchase as pr
from mod import C_consume as cs
from mod import D_main_table as mt
from mod.O_general import CancelOperation, InputError, check_cancel


def main():
    while True:
        try:
            option = input("請選擇功能：A.新增會員/B.購買課程/C.上課/D.更新主表\n")
            check_cancel(check=option)

            if option in ["A", "a"]:
                add.A_add_new_member()

            elif option in ["B", "b"]:
                pr.B_buy_course_plan()

            elif option in ["C", "c"]:
                cs.C_consume_course()

            elif option in ["D", "d"]:
                mt.D_update_main_data()
                print("已更新主表！")

            else:
                print("輸入錯誤，請重新輸入")

        except CancelOperation as e:
            print(f"{e}")
            break

        except InputError as e:
            print(f"")
            break


if "__main__" == __name__:
    main()
