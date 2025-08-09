import json
import os


PATH_TO_CONFIG = "~/.config/EDCO.json"


def get_data() -> dict:

    path = os.path.expanduser(PATH_TO_CONFIG)
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump({"EDCO": {"path": path}}, file)
        print(f"File {PATH_TO_CONFIG} was created.")
    with open(path) as file:
        data = json.load(file)
    return data
