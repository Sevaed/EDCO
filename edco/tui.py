from edco.data import get_data
from edco.commands import edit_config

import curses
from curses import wrapper


UP = [curses.KEY_UP, ord("k"), ord("w")]
DOWN = [curses.KEY_DOWN, ord("j"), ord("s")]
RIGHT = [curses.KEY_RIGHT, ord("l"), ord("d")]
LEFT = [curses.KEY_LEFT, ord("h"), ord("a")]
ENTER = [curses.KEY_ENTER, 10, 13, ord(" ")]
EXIT = [ord("q")]


def configuration_to_app_groups(configuration={}):
    app_groups = {}

    for app_name, app_data in configuration.items():
        app_group_name = app_data.get("group")
        if app_groups.setdefault(app_group_name, [app_name]) != [app_name]:
            app_groups[app_group_name].append(app_name)
    ungroupped = app_groups.pop(None)

    app_groups = dict(
        sorted(app_groups.items(), key=lambda item: len(item[1]), reverse=True)
    )
    app_groups[None] = ungroupped
    for group in app_groups:
        app_groups[group] = list(
            sorted(app_groups[group], key=len, reverse=True))

    return app_groups


def calculate_menu(current_choice: list[int], app_groups: dict[str, list[str]], apps: list) -> tuple[list[tuple[int, int, str, int]], list[tuple[int, int, str, str]]]:
    drawable_app_groups: list[tuple[int, int, str, int]] = []
    drawable_apps: list[tuple[int, int, str, str]] = []
    apps.clear()
    x = 2

    lenght_of_last_collumn = 0
    for app_group_index, app_group_name in enumerate(app_groups.keys()):
        current_maximum_lenght = 0
        x += lenght_of_last_collumn + 1
        y = 2
        if app_group_name is None:
            current_app_group_name = "▼ nogroup"
            drawable_app_groups.append((y, x, current_app_group_name, 3))
            color = 4
        elif app_groups[app_group_name]:
            current_app_group_name = "▼ " + app_group_name
            drawable_app_groups.append((y, x, current_app_group_name, 1))
            color = 2
        else:
            exit()
        for app_index, app_name in enumerate(app_groups[app_group_name]):
            apps.append(([app_group_index, app_index], app_group_name))
            if app_index != len(app_groups[app_group_name]) - 1:
                printable_name = "├── " + app_name
            else:
                printable_name = "└── " + app_name

            if [app_group_index, app_index] == current_choice:
                drawable_apps.append(
                    (y + app_index + 1, x, printable_name, "reverse"))
            else:
                drawable_apps.append(
                    (y + app_index + 1, x, printable_name, f"{color}"))
            if len(printable_name) > current_maximum_lenght:
                current_maximum_lenght = len(printable_name)

        if len(current_app_group_name) > current_maximum_lenght:
            current_maximum_lenght = len(current_app_group_name)

        lenght_of_last_collumn = current_maximum_lenght
    return drawable_app_groups, drawable_apps


def draw_menu(stdscr, drawable_app_groups, drawable_items):
    for group in drawable_app_groups:
        y, x, printable_name, color = group
        stdscr.addstr(y, x, printable_name, curses.color_pair(color))
    for item in drawable_items:
        y, x, printable_name, state_or_color = item
        if state_or_color == 'reverse':
            stdscr.addstr(y, x, printable_name, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, printable_name,
                          curses.color_pair(int(state_or_color)))


def name_of_position(pos, apps, app_groups):
    for i in apps:
        if pos in i:
            return app_groups[i[1]][i[0][1]]
    exit(1)


def name_of_pos_group(numb, apps):
    for i in apps:
        if i[0][0] == numb:
            return i[1]
    exit(1)


def is_right_exist(pos, apps):
    for i in apps:
        if pos[0] + 1 == i[0][0]:
            return True
    return False


def is_left_exist(pos, apps):
    for i in apps:
        if pos[0] - 1 == i[0][0]:
            return True
    return False


def is_right_choice_exist(pos, apps):
    for i in apps:
        if [pos[0] + 1, pos[1]] in i:
            return True
    return False


def is_left_choice_exist(pos, apps):
    for i in apps:
        if [pos[0] - 1, pos[1]] in i:
            return True
    return False


def main(stdscr, app_groups):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    current_choice = [0, 0]
    apps = []

    while True:

        drawable_app_groups, drawable_items = calculate_menu(
            current_choice, app_groups, apps)

        draw_menu(stdscr, drawable_app_groups, drawable_items)

        key = stdscr.getch()

        name_of_current_group = ""
        for i in apps:
            if current_choice == i[0]:
                name_of_current_group = i[1]

        if key in UP and current_choice[1] != 0:
            current_choice[1] -= 1
        if (
            key in DOWN
            and current_choice[1] != len(app_groups[name_of_current_group]) - 1
        ):
            current_choice[1] += 1
        if key in RIGHT:
            if is_right_choice_exist(current_choice, apps):
                current_choice[0] += 1
            elif is_right_exist(current_choice, apps):
                rows = len(app_groups[name_of_pos_group(
                    current_choice[0] + 1, apps)]) - 1
                current_choice = [current_choice[0] + 1, rows]
        if key in LEFT:
            if is_left_choice_exist(current_choice, apps):
                current_choice[0] -= 1
            elif is_left_exist(current_choice, apps):
                rows = len(app_groups[name_of_pos_group(
                    current_choice[0] - 1, apps)]) - 1
                current_choice = [current_choice[0] - 1, rows]
        if key in ENTER:
            edit_config(name_of_position(current_choice, apps, app_groups))
            exit()
        if key in EXIT:
            exit(0)


def run_tui():
    app_groups = configuration_to_app_groups(get_data())
    wrapper(main, app_groups)
