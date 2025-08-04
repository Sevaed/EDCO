from edco.data import get_data

import subprocess
import os
import sys
import json

CONFIG_PATH = get_data("path")
EDITOR = str(os.environ.get("EDITOR", "nvim"))
ASCII_CODES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[36m",
    "YELLOW": "\033[33m",
    "GREEN": "\033[32m",
}

data = get_data("data")

def list_names():
    names = data.keys()
    print(" ".join(names))
    sys.exit(0)

def rewrite():
    with open(CONFIG_PATH, "w") as config:
        json.dump(data, config)


def is_enough(args, numb=0):
    if len(args) >= numb:
        return True
    else:
        help()
        exit("Not enough elements")


def edit_config(*args):
    is_enough(args, 1)
    if args[0] not in data:
        name_not_found()
    else:
        path = get_path(args[0])
        subprocess.call([EDITOR, path])
        if "command" in data[args[0]]:
            subprocess.call(data[args[0]]["command"])


def name_not_found():
    exit("Name not found")


def get_path(name=""):
    return data[name]["path"]


def path(*args):
    is_enough(args, 1)
    name = args[0]
    if name in data:
        print(get_path(name))
    else:
        name_not_found()


def cat(*args):
    is_enough(args, 1)
    name = args[0]
    with open(get_path(name), "r") as config:
        print(config.read())


def add_element(*args):
    is_enough(args, 2)
    conf = len(args)
    name = args[0]
    path = args[1]
    if name in data:
        print("This name already taken")
        exit(1)
    if 2 < conf < 5:
        if "=" not in args[2] or (conf > 3 and "=" not in args[3]) or conf > 4:
            help()
    if conf == 3:
        k, v = args[2].split("=", 1)
        data[name] = {"path": path, k: v}
    elif conf == 4:
        k, v = args[2].split("=", 1)
        val3 = args[3].split("=", 1)[1]
        if k == "group":
            data[name] = {"path": path, "group": v, "command": val3}
        else:
            data[name] = {"path": path, "group": val3, "command": v}
    else:
        data[name] = {"path": path}
    rewrite()
    print(f"{path} was saved as {name}")


def del_smth(*args):
    is_enough(args, 2)
    if args[0] == "name" and args[1] in data:
        print(data[args[1]]["path"] + " was removed")
        data.pop(args[1])
        rewrite()
    elif args[0] == "group":
        group = args[1]
        to_remove = []
        for i in data:
            if group == data[i].get("group"):
                to_remove.append(i)
                print(i + " will be removed")
        while True:
            ask = input(f"Remove all files in group {group}? y/N")
            if ask in ["y", "Y", "yes", "Yes", "YES"]:
                for i in to_remove:
                    data.pop(i)
                rewrite()
                exit(0)
            elif ask in ["", "n", "N", "no", "No", "NO"]:
                exit(0)
    else:
        help()


def names(*args):
    groups = {}
    no_group = []
    C = ASCII_CODES
    COLOR_GROUP = f"{C['BOLD']}{C['CYAN']}"
    COLOR_CONFIG = C["GREEN"]
    COLOR_FIELD = C["DIM"]
    RESET = C["RESET"]

    for name, config in data.items():
        group = config.get("group")
        if group is None:
            no_group.append((name, config))
        else:
            groups.setdefault(group, []).append((name, config))

    for name, cfg in sorted(no_group):
        print(f"{COLOR_CONFIG}• {name}{RESET}")

    for group in sorted(groups):
        print(f"{COLOR_GROUP}▼ {group}{RESET}")
        items = groups[group]
        for i, (name, cfg) in enumerate(sorted(items)):
            branch = "└──" if i == len(items) - 1 else "├──"
            print(f"  {COLOR_CONFIG}{branch} {name}{RESET}")


def help(*args):
    C = ASCII_CODES

    print(f"""
{C['BOLD']}Config Manager{C['RESET']} — manage named edco files with optional groups and commands

{C['BOLD']}Usage:{C['RESET']}
  {C['CYAN']}edco <name>{C['RESET']}               {C['DIM']}Open config in $EDITOR{C['RESET']}
  {C['CYAN']}edco -p <name>{C['RESET']}            {C['DIM']}Print path to config{C['RESET']}
  {C['CYAN']}edco -c <name>{C['RESET']}            {C['DIM']}Print contents of config file{C['RESET']}
  {C['CYAN']}edco -a <name> <path>{C['RESET']}     {C['DIM']}Add new config{C['RESET']}
      [key=value ...]      {C['DIM']}(e.g. group=shells command=\"echo done\"){C['RESET']}

  {C['CYAN']}edco -d name <name>{C['RESET']}       {C['DIM']}Delete config by name{C['RESET']}
  {C['CYAN']}edco -d group <group>{C['RESET']}     {C['DIM']}Delete all configs in group (with confirm){C['RESET']}

  {C['CYAN']}edco -n{C['RESET']}                   {C['DIM']}Show all configs (grouped){C['RESET']}
  {C['CYAN']}edco -h{C['RESET']}                   {C['DIM']}Show this help message{C['RESET']}

{C['BOLD']}Examples:{C['RESET']}
  {C['GREEN']}edco -a kitty ~/.config/kitty/kitty.conf command=\"kill -SIGUSR1 $(pgrep kitty)\"{C['RESET']}
  {C['GREEN']}edco fish{C['RESET']}                      {C['DIM']}Opens config named 'fish' in your editor{C['RESET']}
  {C['GREEN']}edco -d group shells{C['RESET']}           {C['DIM']}Prompts before deleting all configs in 'shells'{C['RESET']}
""")
    exit(0)
