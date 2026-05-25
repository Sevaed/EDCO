import json
import os

xdg_config_home = os.getenv("XDG_CONFIG_HOME")
home = os.getenv("HOME")
if xdg_config_home:
    PATH_TO_CONFIG = os.path.join(xdg_config_home, "EDCO.json")
elif home:
    PATH_TO_CONFIG = os.path.join(home, ".config/EDCO.json")
else:
    exit("For some reason your system does not have $HOME")


def get_data() -> dict:

    path = os.path.expanduser(PATH_TO_CONFIG)
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump({"EDCO": {"path": path}}, file)
        print(f"File {PATH_TO_CONFIG} was created.")
    with open(path) as file:
        data = json.load(file)
    return data
