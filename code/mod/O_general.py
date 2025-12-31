import pandas as pd
from mod.O_config import COACH, MEMBER_SHEET
from mod import O_connect_to_gsheet as gs


class InputError(Exception):
    """查無會員姓名或信箱時的錯誤訊息"""
    pass


def GET_DF_FROM_DB(sheet: str):
    """
    從 Google Sheet 讀取資料並轉換為 DataFrame
    """
    try:
        df = gs.read_sheet_as_df(sheet)
        
        # 強制轉換特定欄位為字串，避免自動轉型
        col_types = {
            '電話': str,
            '匯款末五碼': str,
            '會員編號': str,
            '備註': str
        }
        
        for col, dtype in col_types.items():
            if col in df.columns:
                # fillna("") 確保空值轉字串後不會變成 "nan"
                df[col] = df[col].fillna("").astype(dtype)
                # 針對字串欄位，移除可能的 ".0" 結尾 (源自 float 轉 str)
                if dtype == str:
                    df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
                
        return df
    except Exception as e:
        # 若是第一次讀取或連線失敗，可能需要拋出錯誤讓上層處理
        raise FileNotFoundError(f"讀取 Sheet {sheet} 失敗: {str(e)}")


def SAVE_TO_SHEET(df: pd.DataFrame, sheet: str):
    """
    將 DataFrame 寫回 Google Sheet
    """
    try:
        gs.update_sheet(sheet_name=sheet, updated_df=df)
        return True, "資料儲存成功！"

    except Exception as e:
        return False, f"發生錯誤：{str(e)}"


def get_coach_id(coach: str, df_coach: pd.DataFrame = None) -> tuple[str, str]:
    if df_coach is None:
        df_coach = GET_DF_FROM_DB(sheet=COACH)

    mask = (df_coach["姓名"] == coach)
    if df_coach[mask].empty:
        raise ValueError(f"查無教練資料: {coach}")

    coach_id = df_coach[mask]["教練編號"].iloc[0]
    coach_str = df_coach[mask]["會員編號"].iloc[0]
    return coach_id, coach_str


def get_member_name(member_id: str, df_member: pd.DataFrame = None) -> str:
    if df_member is None:
        df_member = GET_DF_FROM_DB(sheet=MEMBER_SHEET)

    mask = (df_member["會員編號"] == member_id)
    if df_member[mask].empty:
        raise InputError("查無此會員資料")
    member_name = df_member[mask]["會員姓名"].iloc[0]
    return member_name
