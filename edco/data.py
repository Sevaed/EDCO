import json
import os
from typing import Union

def get_data(mode)-> Union[dict]:
    path = os.path.expanduser("~/.config/EDCO.json")
    if os.path.exists(path):
        pass
    else:
        with open(path, "w") as file:
            json.dump({"EDCO":{"path":path}}, file)
        print("File ~/.config/EDCO.json was created.")

    if mode == "data":
        with open(path) as file:
            data = json.load(file)
        return data
    elif mode == "path":
        return path
    else:
        exit(0)
        
