from ctypes import windll
from getopt import getopt
from sys import argv, executable
from requests import Session
from auth import Authenticator
from installer import Installer
from selection import SelectionController


class Updater:
    def __init__(self):
        session = Session()
        self._auth = Authenticator(session)
        self._installer = Installer(session)
        self._selection = SelectionController()
        self._skip_selection = False
        self._user_name = ""
        self._user_pwd = ""

    def start(self):
        self._make_admin()
        self._process_args()
        if not self._auth.login(self._user_name, self._user_pwd):
            print("Přihlášení se nezdařilo, program bude ukončen.")
            return
        if not self._skip_selection:
            self._selection.select_wanted()
        self._installer.start_downloads(self._selection.selected, self._selection.is_install)

    def _process_args(self):
        args, _ = getopt(argv[1:], "u:p:s:", ["jmeno=", "heslo=", "vyber="])
        for arg, val in args:
            if arg in ("-u", "--jmeno"):
                self._user_name = val
            elif arg in ("-p", "--heslo"):
                self._user_pwd = val
            elif arg in ("-s", "--vyber"):
                self._selection.parse_selected(val)
                self._skip_selection = True

    def _make_admin(self):
        try:
            is_admin = windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False

        if not is_admin:
            params = " ".join([f'"{arg}"' for arg in argv])
            
            ret = windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                executable, 
                f"{__file__} {params}", 
                None, 
                1
            )
            
            if int(ret) > 32:
                exit(0)
            else:
                print("Spusťte program jako administrátor!")
                exit(1)

if __name__ == "__main__":
    # this way the admin process starts normally
    from main import main
    main()