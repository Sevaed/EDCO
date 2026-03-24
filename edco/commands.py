from os.path import abspath
from edco.data import get_apps_data
from edco.data import PATH_TO_CONFIG

import subprocess
import os
import sys
import json

EDITOR = str(os.environ.get("EDITOR", "nvim"))
ASCII_CODES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[36m",
    "YELLOW": "\033[33m",
    "GREEN": "\033[32m",
}

apps_data = get_apps_data()


def list_apps_print_names():
    names = apps_data.keys()
    print(" ".join(names))
    sys.exit(0)


def rewrite_config_file():
    with open(PATH_TO_CONFIG, "w") as config:
        json.dump(apps_data, config)


def is_enough_args(args, numb=0):
    if len(args) >= numb:
        return True
    else:
        help()
        exit("Not enough elements")


def edit_app_config(*args):
    is_enough_args(args, 1)
    name = args[0]
    if len(args) == 2:
        editor = args[1]
    else:
        editor = EDITOR
    if name not in apps_data:
        name_not_found()
    else:
        path = get_app_path(name)
        subprocess.call([editor, path])


def name_not_found():
    exit("Name not found")


def get_app_path(name):
    return apps_data[name]["path"]


def path(name):
    if name in apps_data:
        print(get_app_path(name))
    else:
        name_not_found()


def cat(name):
    with open(get_app_path(name), "r") as config:
        print(config.read())


def add_app(*args):
    is_enough_args(args, 2)
    name = args[0]
    path = args[1]
    if len(args) == 3:
        group = args[2]
    else:
        group = None

    if name in apps_data:
        exit("This name already taken")
    if not group:
        apps_data[name] = {"path": os.path.abspath(path)}
    else:
        apps_data[name] = {"path": os.path.abspath(path), "group": group}
    rewrite_config_file()
    print(f"{path} was saved as {name}")


def del_elements(type_of_element, name_of_element):
    if type_of_element == "name" and name_of_element in apps_data:
        print(
            f"{name_of_element}({apps_data[name_of_element]['path']}) was removed from apps list"
        )
        apps_data.pop(name_of_element)
        rewrite_config_file()
    elif type_of_element == "group":
        group = name_of_element
        to_remove = []
        for i in apps_data:
            if group == apps_data[i].get("group"):
                to_remove.append(i)
                print(i + " will be removed from apps list")
        if not to_remove:
            exit("This group is not exist")
        while True:
            ask = input(f"Remove all files in group {group}? y/N\n")
            if ask in ["y", "Y", "yes", "Yes", "YES"]:
                for i in to_remove:
                    apps_data.pop(i)
                rewrite_config_file()
                exit(0)
            elif ask in ["", "n", "N", "no", "No", "NO"]:
                exit(0)
    else:
        help()


def print_names():
    groups = {}
    no_group = []
    C = ASCII_CODES
    COLOR_GROUP = f"{C['BOLD']}{C['CYAN']}"
    COLOR_CONFIG = C["GREEN"]
    RESET = C["RESET"]

    for name, config in apps_data.items():
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


# TODO redo
# def help(*args):
#     C = ASCII_CODES
#
#     print(f"""
# {C['BOLD']}Config Manager{C['RESET']} — manage named edco files with optional groups and commands
#
# {C['BOLD']}Usage:{C['RESET']}
#   {C['CYAN']}edco <name>{C['RESET']}               {C['DIM']}Open config in $EDITOR{C['RESET']}
#   {C['CYAN']}edco -p <name>{C['RESET']}            {C['DIM']}Print path to config{C['RESET']}
#   {C['CYAN']}edco -c <name>{C['RESET']}            {C['DIM']}Print contents of config file{C['RESET']}
#   {C['CYAN']}edco -a <name> <path>{C['RESET']}     {C['DIM']}Add new config{C['RESET']}
#       [key=value ...]      {C['DIM']}(e.g. group=shells command=\"echo done\"){C['RESET']}
#
#   {C['CYAN']}edco -d name <name>{C['RESET']}       {C['DIM']}Delete config by name{C['RESET']}
#   {C['CYAN']}edco -d group <group>{C['RESET']}     {C['DIM']}Delete all configs in group (with confirm){C['RESET']}
#
#   {C['CYAN']}edco -n{C['RESET']}                   {C['DIM']}Show all configs (grouped){C['RESET']}
#   {C['CYAN']}edco -h{C['RESET']}                   {C['DIM']}Show this help message{C['RESET']}
#
# {C['BOLD']}Examples:{C['RESET']}
#   {C['GREEN']}edco -a kitty ~/.config/kitty/kitty.conf command=\"kill -SIGUSR1 $(pgrep kitty)\"{C['RESET']}
#   {C['GREEN']}edco fish{C['RESET']}                      {C['DIM']}Opens config named 'fish' in your editor{C['RESET']}
#   {C['GREEN']}edco -d group shells{C['RESET']}           {C['DIM']}Prompts before deleting all configs in 'shells'{C['RESET']}
# """)
#     exit(0)
