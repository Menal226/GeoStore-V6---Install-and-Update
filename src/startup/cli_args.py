from dataclasses import dataclass
from getopt import GetoptError, getopt
import sys


@dataclass(frozen=True)
class StartupArgs:
    username: str = ""
    password: str = ""
    selection: str = ""


def parse_startup_args(args: list[str] | None = None) -> StartupArgs:
    if args is None:
        args = sys.argv[1:]

    user_name = ""
    password = ""
    selection = ""

    try:
        parsed_args, _ = getopt(args, "u:p:s:", ["jmeno=", "heslo=", "vyber="])
    except GetoptError:
        return StartupArgs()

    for arg, val in parsed_args:
        if arg in ("-u", "--jmeno"):
            user_name = val
        elif arg in ("-p", "--heslo"):
            password = val
        elif arg in ("-s", "--vyber"):
            selection = val

    return StartupArgs(user_name, password, selection)