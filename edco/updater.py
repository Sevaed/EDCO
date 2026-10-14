import json
from sys import exit

from .data import PATH_TO_CONFIG, check_config, get_data

prev_format = {
    "apps": {
        "name": {"path": "<path>"},
        "another": {"path": "<path>", "group": "group_name"},
    },
    "backup": {"type": "<type>", "configs": {"<type>": {"config": {"arg": "val"}}}},
}

curr_format = {
    "apps": {
        "name": {"path": "<path>"},
        "another": {"path": "<path>", "group": "group_name"},
    },
    "backup": {"type": "<type>", "configs": {"<type>": {"arg": "val"}}},
}


def update():
    path = PATH_TO_CONFIG
    current_config = get_data()
    if "path" in current_config["backup"]["configs"]["script"]:
        return True
    if not check_config(path):
        exit("TODO: handling errors in config")
    new_config = {
        "apps": current_config["apps"],
        "backup": {
            "type": current_config["backup"]["type"],
            "configs": {
                "script": {
                    "path": current_config["backup"]["configs"]["script"]["config"][
                        "path"
                    ]
                }
            },
        },
    }
    with open(PATH_TO_CONFIG, "w") as file:
        json.dump(new_config, file, indent=4)
