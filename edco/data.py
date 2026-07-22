import json
import os

PATH_TO_CONFIG = os.path.expanduser("~/.config/EDCO.jsonc")
EXAMPLE_CONFIG = {
    "apps": {
        "EDCO": {"path": PATH_TO_CONFIG},
    },
    "backup": {
        "type": "none",
        "configs": {
            "script": {
                "config": {"path": "<path_to_executable_to_call_after_any_changes>"}
            }
        },
    },
}


def get_data() -> dict:
    path = PATH_TO_CONFIG
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump(EXAMPLE_CONFIG, file)
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
