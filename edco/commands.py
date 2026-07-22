# from os.path import abspath
from . import data
import subprocess
import os
import sys
import json

EDITOR = str(os.environ.get("EDITOR", "vim"))
ASCII_CODES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[36m",
    "YELLOW": "\033[33m",
    "GREEN": "\033[32m",
    "RED": "\033[1;31m",
}

apps_data = data.get_apps_data()
backup_config = data.get_backup_config()


def list_apps_print_names():
    names = apps_data.keys()
    print(" ".join(names))
    sys.exit(0)


def rewrite_config_file():
    prev = data.get_data()
    prev["apps"] = apps_data
    with open(data.PATH_TO_CONFIG, "w") as config:
        json.dump(prev, config)


def is_enough_args(args, numb=0):
    if len(args) >= numb:
        return True
    else:
        help()
        exit("Not enough elements")


def do_backup():
    if backup_config["type"] == "none":
        pass
    elif backup_config["type"] == "script":
        path = backup_config["configs"]["script"]["config"]["path"].strip()
        print("Backup started")
        subprocess.run(path.split(" "), check=True)
        print("\nBackup finished")


def edit_app_config(name, editor=EDITOR):
    if name not in apps_data:
        name_not_found()
    else:
        path = get_app_path(name)
        subprocess.call([editor, path])
    if backup_config["type"] != "none":
        do_backup()


def name_not_found():
    exit("Name not found")


def get_app_path(name):
    return os.path.expanduser(apps_data[name]["path"])


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
        if group == "NoGroup":
            exit("Reserved group name")
        apps_data[name] = {"path": os.path.abspath(path), "group": group}
    rewrite_config_file()
    print(f"{path} was saved as {name}")


def del_elements(type_of_element, name_of_element, force=False):
    if type_of_element == "name" and name_of_element in apps_data:
        if force:
            print(
                f"{name_of_element} ({apps_data[name_of_element]['path']}) was removed from apps list"
            )
            apps_data.pop(name_of_element)
            rewrite_config_file()
            exit(0)
        while True:
            ask = input(
                f"\nRemove {ASCII_CODES['RED']}{name_of_element}{ASCII_CODES['RESET']}? [y/N] "
            )
            if ask in ["y", "Y", "yes", "Yes", "YES"]:
                print(
                    f"{name_of_element} ({apps_data[name_of_element]['path']}) was removed from apps list"
                )
                apps_data.pop(name_of_element)
                rewrite_config_file()
                exit(0)
            elif ask in ["", "n", "N", "no", "No", "NO"]:
                exit(0)
    elif type_of_element == "group":
        group = name_of_element
        to_remove = []
        for i in apps_data:
            if group == apps_data[i].get("group"):
                to_remove.append(i)
                if not force:
                    print(
                        f"{ASCII_CODES['RED']}{i}{ASCII_CODES['RESET']}"
                        + " will be removed from apps list"
                    )
                else:
                    print(
                        f"{ASCII_CODES['RED']}{i}{ASCII_CODES['RESET']}"
                        + " is removed from apps list"
                    )
        if not to_remove:
            exit("This group is not exist")
        if force:
            for i in to_remove:
                apps_data.pop(i)
            rewrite_config_file()
            exit(0)

        while True:
            ask = input(f"\nRemove all files in group {group}? [y/N] ")
            if ask in ["y", "Y", "yes", "Yes", "YES"]:
                for i in to_remove:
                    apps_data.pop(i)
                rewrite_config_file()
                exit(0)
            elif ask in ["", "n", "N", "no", "No", "NO"]:
                exit(0)
    else:
        exit(f"{name_of_element}, is not found")


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
            print(f"{COLOR_CONFIG}{branch} {name}{RESET}")
