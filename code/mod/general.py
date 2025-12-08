import pandas as pd
from mod.config import DATABASE
from mod import general as gr
from pathlib import Path


class CancelOperation(Exception):
    """使用者手動取消操作"""
    pass


def check_cancel(check: str):
    """輸入「*」可強制中止並取消當前操作"""
    if check == "*":
        raise CancelOperation("使用者取消")


def get_project_root():
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent.parent

    return root_path


def search_db(root: str, db_name: str) -> str:
    root = Path(root)
    search = f"**/{db_name}"
    result = list(root.rglob(search))

    return result


def get_db_path(search_result: list[Path]) -> pd.DataFrame:
    if len(search_result) > 1:
        print(f"錯誤！查詢到{len(search_result)}個資料庫")
    if len(search_result) == 0:
        print(f"錯誤！查無資料庫")

    db_path = search_result[0]

    return db_path


def GET_DF_FROM_DB(sheet: str):
    root = gr.get_project_root()
    search_result = search_db(root=root, db_name=DATABASE)
    db_path = get_db_path(search_result=search_result)
    df = pd.read_excel(io=db_path, sheet_name=sheet)

    return df


def SAVE_TO_SHEET(df: pd.DataFrame, sheet: str):
    root = gr.get_project_root()
    search_result = search_db(root=root, db_name=DATABASE)
    db_path = get_db_path(search_result=search_result)

    while True:
        try:
            # 使用 ExcelWriter 的追加模式
            with pd.ExcelWriter(
                db_path,
                engine="openpyxl",
                mode="a",  # 追加模式
                if_sheet_exists="replace"  # 覆蓋該 sheet
            ) as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)

            print(f"資料儲存成功！")
            break

        except PermissionError:
            warning = input("存檔失敗，請確認檔案是否被開啟或使用。關閉後按enter重試。")
            check_cancel(check=warning)

        except CancelOperation as e:
            print(f"{e}")
            break

        except Exception as e:
            print(f"發生錯誤：{e}")
            break
