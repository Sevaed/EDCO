import json
import os

from .pydantic_class import config

CONFIG_FOLDER = os.getenv("XDG_CONFIG_HOME", "~/.config")
PATH_TO_CONFIG = os.path.join(os.path.expanduser(CONFIG_FOLDER), "EDCO.test.jsonc")
EXAMPLE_CONFIG = {
    "apps": {
        "EDCO": {"path": PATH_TO_CONFIG},
    },
    "backup": {
        "type": "none",
        "configs": {
            "script": {"path": "<path_to_executable_to_call_after_any_changes>"}
        },
    },
}
BACKUP_TYPES = ["none", "script"]


def write_default_config():
    with open(PATH_TO_CONFIG, "w") as file:
        json.dump(EXAMPLE_CONFIG, file, indent=4)


def check_config(path):
    if not os.path.exists(path):
        write_default_config()
        return (True, "")
    else:
        with open(path, "r") as file:
            if file.read() == "":
                file.close()
                write_default_config()
                return (True, "")
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                pass

    if data in [[], {}]:
        write_default_config()
        return (True, "")


def get_data() -> dict:
    path = PATH_TO_CONFIG
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump(EXAMPLE_CONFIG, file, sort_keys=True, indent=4)
        print(f"File {PATH_TO_CONFIG} was created.")
    with open(path) as file:
        data = json.load(file)
    return data


def get_apps_data() -> dict:
    data = get_data()
    return data["apps"]


def get_backup_config() -> dict:
    data = get_data()
    return data["backup"]
