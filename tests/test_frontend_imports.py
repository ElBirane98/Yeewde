import runpy
import sys
from pathlib import Path


def test_frontend_app_imports_when_launched_as_script():
    project_root = Path(__file__).resolve().parents[1]
    frontend_dir = project_root / "frontend"

    original_sys_path = list(sys.path)
    sys.path[:] = [str(frontend_dir), *[p for p in sys.path if Path(p).resolve() != project_root]]
    try:
        globals_dict = runpy.run_path(str(frontend_dir / "app.py"), run_name="__main__")
    finally:
        sys.path[:] = original_sys_path

    assert "API_BASE_URL" in globals_dict
