from ctypes import windll
from pathlib import Path
import sys


def ensure_admin_on_start() -> None:
    try:
        is_admin = windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        entry_script = Path(sys.argv[0]).resolve()
        entry_args = " ".join([f'"{arg}"' for arg in sys.argv[1:]])

        pythonw_candidate = Path(sys.executable).with_name("pythonw.exe")
        python_exec = str(pythonw_candidate if pythonw_candidate.exists() else Path(sys.executable))
        parameters = f'"{entry_script}" {entry_args}'.strip()

        ret = windll.shell32.ShellExecuteW(
            None,
            "runas",
            python_exec,
            parameters,
            str(entry_script.parent),
            0,
        )

        if int(ret) > 32:
            sys.exit(0)

        print("Spusťte program jako administrátor!")
        sys.exit(1)