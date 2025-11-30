from pathlib import Path


def get_project_root():
    current_path = Path(__file__).resolve()
    root_path = current_path.parent.parent.parent

    return root_path
