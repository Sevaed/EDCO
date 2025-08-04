from . import commands as cmd
from . import tui
from . import data
import sys

def main(args: list[str]):
    if len(args) == 0:
        tui.run_tui()
    elif args[0] == "--_list-names":
        cmd.list_names()
    else:
        commands = {"-p":cmd.path, "-c":cmd.cat, "-a":cmd.add_element, "-n":cmd.names,"-h":cmd.help, "--help":cmd.help, "-d":cmd.del_smth}
        if args[0] in commands:
            commands[args[0]](*args[1:])
        elif args[0] in data.get_data():
            cmd.edit_config(args[0])
        elif args[0].startswith("-"):
            cmd.flag_not_found(args[0])
        else:
            cmd.name_not_found()

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
