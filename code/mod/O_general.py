from pathlib import Path
import pandas as pd
from mod.O_config import DATABASE, COACH, MEMBER_SHEET


class InputError(Exception):
    """查無會員姓名或信箱時的錯誤訊息"""
    pass


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
        # 這裡可以改為拋出異常或記錄 log，但在 web app 中 print 看不到
        pass
    if len(search_result) == 0:
        raise FileNotFoundError(f"錯誤！查無資料庫: {DATABASE}")

    db_path = search_result[0]

    return db_path


def GET_DF_FROM_DB(sheet: str):
    root = get_project_root()
    search_result = search_db(root=root, db_name=DATABASE)
    db_path = get_db_path(search_result=search_result)

    # 檢查檔案是否存在
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}")

    df_temp = pd.read_excel(io=db_path, sheet_name=sheet)

    dtype_dict = {}
    if '電話' in df_temp.columns:
        dtype_dict['電話'] = str
    if '匯款末五碼' in df_temp.columns:
        dtype_dict['匯款末五碼'] = str
    if '會員編號' in df_temp.columns:
        dtype_dict['會員編號'] = str

    df = pd.read_excel(io=db_path, sheet_name=sheet, dtype=dtype_dict)

    return df


def SAVE_TO_SHEET(df: pd.DataFrame, sheet: str):
    root = get_project_root()
    search_result = search_db(root=root, db_name=DATABASE)
    db_path = get_db_path(search_result=search_result)

    try:
        # 使用 ExcelWriter 的追加模式
        with pd.ExcelWriter(
            db_path,
            engine="openpyxl",
            mode="a",  # 追加模式
            if_sheet_exists="replace"  # 覆蓋該 sheet
        ) as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)

        return True, "資料儲存成功！"

    except PermissionError:
        return False, "存檔失敗：檔案可能被開啟，請關閉 Excel 後重試。"

    except Exception as e:
        return False, f"發生錯誤：{str(e)}"


def get_coach_id(coach: str) -> str:
    df_coach = GET_DF_FROM_DB(sheet=COACH)
    mask = (df_coach["姓名"] == coach)
    coach_id = df_coach[mask]["教練編號"].iloc[0]
    coach_str = df_coach[mask]["會員編號"].iloc[0]
    return coach_id, coach_str


def get_member_name(member_id: str) -> str:
    df_member = GET_DF_FROM_DB(sheet=MEMBER_SHEET)
    mask = (df_member["會員編號"] == member_id)
    if df_member[mask].empty:
        raise InputError("查無此會員資料")
    member_name = df_member[mask]["會員姓名"].iloc[0]
    return member_name
