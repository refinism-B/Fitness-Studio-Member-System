from pathlib import Path
from mod import O_general as gr
from datetime import datetime
import shutil
from mod.O_config import DATABASE


class BackupManager:
    def __init__(self, backup_dir, max_files=50):
        self.backup_dir = Path(backup_dir)
        self.max_files = max_files

        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, source, prefix="backup"):
        source_path = Path(source)

        # 若檔案不存在則報錯
        if not source_path.exists():
            raise FileNotFoundError(f"來源檔案不存在: {source}")

        # 產生時間字串命名檔案
        time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{prefix}_{time}.xlsx"
        backup_path = self.backup_dir / file_name

        # 確認檔案及路徑，將檔案複製
        if source_path.is_file():
            shutil.copy2(source_path, backup_path)
        else:
            shutil.copytree(source_path, backup_path)

        # 備份完畢後，如檔案數量超過則清理舊檔案
        self._clean_old_file(prefix)

        return (f"{time}檔案備份完成！")

    def _clean_old_file(self, prefix):
        # 列出備份路徑中的所有檔案名，並按修改時間排序
        backup_files = sorted(
            self.backup_dir.glob(f"{prefix}_*"),
            key=lambda x: x.stat().st_mtime
        )

        # 當檔案數超過設定最大值，每次刪除一個檔案，直到數量小於設定值
        while len(backup_files) > self.max_files:
            old_file = backup_files.pop(0)
            try:
                if old_file.is_dir():
                    shutil.rmtree(old_file)
                else:
                    old_file.unlink()
                print("已刪除舊備份")
            except Exception as e:
                print(f"刪除舊備份失敗：{e}")


def backup_flow():
    # 定位根目錄及備份路徑
    root = gr.get_project_root()
    backup_dir = Path(root) / "backup"

    # 定位原檔路徑（資料庫路徑）
    search_result = gr.search_db(root=root, db_name=DATABASE)
    db_path = gr.get_db_path(search_result=search_result)

    # 建立備份器
    backup_manager = BackupManager(backup_dir=backup_dir, max_files=50)

    # 執行備份
    try:
        result = backup_manager.backup_file(source=db_path, prefix="backup")
        return True, result
    except Exception as e:
        return False, f"備份失敗：{e}"
