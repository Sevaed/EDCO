from . import commands as cmd
from . import tui
from . import data
import sys

def main():
    if len(sys.argv) < 2:
        tui.run_tui()
    elif sys.argv[1] == "--_list-names":
        cmd.list_names()
    else:
        arg = sys.argv[1]
        commands = {"-p":cmd.path, "-c":cmd.cat, "-a":cmd.add_element, "-n":cmd.names,"-h":cmd.help, "--help":cmd.help, "-d":cmd.del_smth}
        if arg in commands:
            commands[arg](*sys.argv[2:])
        elif arg in data.get_data("data"):
            cmd.edit_config(arg)
        else:
            cmd.name_not_found()

