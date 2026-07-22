from . import commands
from . import data
import curses
from curses import wrapper


UP = [curses.KEY_UP, ord("k"), ord("w")]
DOWN = [curses.KEY_DOWN, ord("j"), ord("s")]
RIGHT = [curses.KEY_RIGHT, ord("l"), ord("d")]
LEFT = [curses.KEY_LEFT, ord("h"), ord("a")]
ENTER = [curses.KEY_ENTER, 10, 13, ord(" ")]
EXIT = [ord("q"), 27]

MAX_NAME_LENGTH = 15
X_MARGIN, Y_MARGIN = 2, 2

SEPARATOR = "-"

COLORS = {"groups": 1, "NoGroup": 3, "apps": 2, "NoGroup_apps": 4}


apps_data = data.get_apps_data()
backup_config = data.get_backup_config()

debug = []

app_name = ""


def generate_groups(apps_data: dict) -> dict:
    groups = {}
    for app_name, app in apps_data.items():
        group = app.get("group", "NoGroup")
        if group not in groups:
            groups[group] = []
        groups[group].append(app_name)
    pre_sorted_groups = dict(
        sorted(groups.items(), key=lambda element: len(element[1]), reverse=True)
    )
    if list(pre_sorted_groups.keys())[0] != "NoGroup":
        pre_sorted_groups["NoGroup"] = pre_sorted_groups.pop("NoGroup")
    groups = pre_sorted_groups
    for group in groups.items():
        groups[group[0]] = sorted(group[1], key=lambda el: len(el), reverse=True)
    for group_name, group in groups.items():
        for index, app_name in enumerate(group):
            if len(app_name) > MAX_NAME_LENGTH + 3:
                groups[group_name][index] = app_name[:MAX_NAME_LENGTH] + "..."
    return groups


def generate_lines(groups: dict, size: tuple[int, int]) -> list[dict]:
    max_y, max_x = size
    lines = [{"length": X_MARGIN * 2, "height": Y_MARGIN, "groups": []}]
    for group_name, group in groups.items():
        length = max(len(group_name) + 2, len(group[0]) + 4)
        height = len(group) + 1
        if length > max_x + X_MARGIN * 2:
            exit("Screen is not big enough")
        if lines[-1]["length"] + length <= max_x:  # ty: ignore[unsupported-operator]
            lines[-1]["length"] += length + 1  # ty: ignore[unsupported-operator]
            if lines[-1]["height"] < height:  # ty: ignore[unsupported-operator]
                lines[-1]["height"] = height
            lines[-1]["groups"].append(group_name)  # ty: ignore[unresolved-attribute]
        else:
            lines.append(
                {
                    "length": X_MARGIN * 2 + length,
                    "height": height,
                    "groups": [group_name],
                }
            )
    return lines


def calculate_menu(current_choice: list[int], groups: dict, size: tuple[int, int]):
    # global debug  # DEBUG
    max_y, max_x = size
    lines = generate_lines(groups, size)
    pad_height = 10
    groups_per_line = []
    for line in lines:
        height = line["height"]
        groups_per_line.append(line["groups"])
        pad_height += height
    drawable_items = []
    y = Y_MARGIN
    # active = current_choice  # DEBUG
    # debug.append(current_choice)  # DEBUG
    for line_index, line_groups in enumerate(groups_per_line):
        x = X_MARGIN
        for group_index, group in enumerate(line_groups):
            if group == "NoGroup":
                color = COLORS["NoGroup"]
            else:
                color = COLORS["groups"]
            drawable_items.append((y, x, "▼ " + group, color))
            group_length = 2 + len(group)
            group_y = y
            for app_index, app in enumerate(groups[group]):
                if current_choice[0] >= len(groups_per_line):
                    current_choice[0] = 0
                elif current_choice[0] < 0:
                    current_choice[0] = len(groups_per_line) - 1
                if current_choice[0] == line_index:
                    if current_choice[1] >= len(line_groups):
                        current_choice[1] = 0
                    elif current_choice[1] < 0:
                        current_choice[1] = len(line_groups) - 1
                    if current_choice[1] == group_index:
                        if current_choice[2] >= len(groups[group]):
                            current_choice[2] = 0
                        elif current_choice[2] < 0:
                            current_choice[2] = len(groups[group]) - 1
                coords = [line_index, group_index, app_index]
                if coords == current_choice:
                    color = curses.A_REVERSE
                    active = {
                        "app": {app: apps_data[app]},
                        "group": groups[group],
                        "line": lines[line_index],
                        "lines": lines,
                    }
                    if "group" not in active["app"][app].keys():
                        active["app"][app]["group"] = "NoGroup"
                elif group == "NoGroup":
                    color = COLORS["NoGroup_apps"]
                else:
                    color = COLORS["apps"]
                if app_index == len(groups[group]) - 1:
                    app_name = "└── " + app
                else:
                    app_name = "├── " + app
                group_y += 1
                drawable_items.append((group_y, x, app_name, color))
                if group_length < len(app_name):
                    group_length = len(app_name)
            x += group_length + 1
        y += lines[line_index]["height"]
        if len(lines) != 1:
            drawable_items.append((y, X_MARGIN, SEPARATOR * (max_x - 4), 0))
        y += 1
    return pad_height, drawable_items, active


def draw_menu(pad: curses.window, drawable_items):
    for item in drawable_items:
        y, x, name, color = item
        if color != curses.A_REVERSE:
            color = curses.color_pair(color)
        pad.addstr(y, x, name, color)


def open_editor(stdscr: curses.window, app_name: str) -> None:
    curses.def_prog_mode()
    curses.endwin()

    try:
        commands.edit_app_config(app_name)
    finally:
        curses.reset_prog_mode()
        curses.curs_set(0)

        stdscr.clear()
        stdscr.clearok(True)
        stdscr.touchwin()
        stdscr.refresh()


def main(stdscr: curses.window, mode):
    global debug  # DEBUG
    global app_name
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    current_choice = [0, 0, 0]
    groups = generate_groups(apps_data)
    pad = curses.newpad(1, 1)
    pad_y = 0
    while True:
        max_y, max_x = stdscr.getmaxyx()
        pad_height, drawable_items, active = calculate_menu(
            current_choice, groups, stdscr.getmaxyx()
        )
        current_line_id, current_group_id, current_app_id = current_choice
        pad.resize(pad_height, max_x)
        pad.erase()
        stdscr.erase()
        draw_menu(pad, drawable_items)
        stdscr.refresh()
        pad.refresh(pad_y, 0, 0, 0, max_y - 1, max_x - 1)
        key = stdscr.getch()
        if key in EXIT:
            exit(0)
        if key in UP:
            if current_app_id == 0:
                if current_line_id == 0:
                    current_choice[0] = -1
                    current_choice[2] = -1
                else:
                    current_choice[0] += 1
                    current_choice[2] = -1
            else:
                current_choice[2] -= 1
        if key in DOWN:
            if current_app_id == len(active["group"]) - 1:
                if current_line_id == len(active["lines"]) - 1:
                    current_choice[0] = 0
                    current_choice[2] = 0
                else:
                    current_choice[0] -= 1
                    current_choice[2] = 0
            else:
                current_choice[2] += 1
        if key in RIGHT:
            if len(active["line"]["groups"]) > 1:
                if current_group_id == len(active["line"]["groups"]) - 1:
                    next_group_id = 0
                else:
                    next_group_id = current_group_id + 1
                if current_app_id >= len(
                    groups[active["line"]["groups"][next_group_id]]
                ):
                    current_choice[2] = -1
                current_choice[1] += 1
            else:
                if len(active["lines"]) > 1 and current_choice[0] != 0:
                    current_choice[0] -= 1
                    current_choice[1] += 1
                    current_choice[2] = -1
        if key in LEFT:
            if len(active["line"]["groups"]) > 1:
                if current_group_id == 0:
                    next_group_id = -1
                else:
                    next_group_id = current_group_id - 1
                if current_app_id >= len(
                    groups[active["line"]["groups"][next_group_id]]
                ):
                    current_choice[2] = -1
                current_choice[1] -= 1
        if key in ENTER:
            for i in active["app"].keys():
                app_name = i
            if mode in ["cat", "path"]:
                return
            else:
                if mode == "regular":
                    commands.edit_app_config(app_name)
                    exit(0)
                elif mode == "infinite":
                    open_editor(stdscr, app_name)
                    pad = curses.newpad(1, 1)
                    stdscr.clearok(True)


def run_tui(mode="infinite"):
    wrapper(main, mode)
    if mode == "cat":
        commands.cat(app_name)
    elif mode == "path":
        commands.path(app_name)
