from edco.data import get_data
from edco.commands import edit_config

import curses
from curses import wrapper


def configuration_to_groups(configuration={}):
    groups = {}

    for app_name, app_data in configuration.items():
        group = app_data.get("group")
        if groups.setdefault(group, [app_name]) != [app_name]:
            groups[group].append(app_name)
    ungroupped = groups.pop(None)

    groups = dict(
        sorted(groups.items(), key=lambda item: len(item[1]), reverse=True))
    groups[None] = ungroupped
    for group in groups:
        old = groups[group]
        groups[group] = list(sorted(old, key=len, reverse=True))

    return groups


UP = [curses.KEY_UP, ord("k"), ord("w")]
DOWN = [curses.KEY_DOWN, ord("j"), ord("s")]
RIGHT = [curses.KEY_RIGHT, ord("l"), ord("d")]
LEFT = [curses.KEY_LEFT, ord("h"), ord("a")]
ENTER = [curses.KEY_ENTER, 10, 13, ord(" ")]
EXIT = [ord("q")]


def run_tui():
    groups = configuration_to_groups(get_data())
    wrapper(main, groups)


def calculate_menu(current_choice, groups, blocks):
    drawable_groups = []
    drawable_items = []
    blocks.clear()
    x = 2
    last_maximum_lenght = 0
    for group_index, group_name in enumerate(groups.keys()):
        current_maximum_lenght = 0
        x += last_maximum_lenght + 1
        y = 2
        if group_name is None:
            current_group_name = "▼ nogroup"
            drawable_groups.append((y, x, current_group_name, 3))
            color = 4
        elif groups[group_name]:
            current_group_name = "▼ " + group_name
            drawable_groups.append((y, x, current_group_name, 1))
            color = 2
        else:
            exit()
        for item_index, item_name in enumerate(groups[group_name]):
            blocks.append(([group_index, item_index], group_name))
            if item_index != len(groups[group_name]) - 1:
                printable_name = "├── " + item_name
            else:
                printable_name = "└── " + item_name

            if [group_index, item_index] == current_choice:
                drawable_items.append(
                    (y + item_index + 1, x, printable_name, "reverse"))
            else:
                drawable_items.append(
                    (y + item_index + 1, x, printable_name, f"{color}"))
            if len(printable_name) > current_maximum_lenght:
                current_maximum_lenght = len(printable_name)

        if len(current_group_name) > current_maximum_lenght:
            current_maximum_lenght = len(current_group_name)

        last_maximum_lenght = current_maximum_lenght
    return drawable_groups, drawable_items


# exit(str(calculate_menu(current_choice=[
#      0, 0], groups=configuration_to_groups(get_data()))))


def draw_menu(stdscr, drawable_groups, drawable_items):
    for group in drawable_groups:
        y, x, printable_name, color = group
        stdscr.addstr(y, x, printable_name, curses.color_pair(color))
    for item in drawable_items:
        y, x, printable_name, state_or_color = item
        if state_or_color == 'reverse':
            stdscr.addstr(y, x, printable_name, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, printable_name,
                          curses.color_pair(int(state_or_color)))


def name_of_position(pos, blocks, groups):
    for i in blocks:
        if pos in i:
            return groups[i[1]][i[0][1]]
    exit(1)


def name_of_pos_group(numb, blocks):
    for i in blocks:
        if i[0][0] == numb:
            return i[1]
    exit(1)


def is_right_exist(pos, blocks):
    for i in blocks:
        if pos[0] + 1 == i[0][0]:
            return True
    return False


def is_left_exist(pos, blocks):
    for i in blocks:
        if pos[0] - 1 == i[0][0]:
            return True
    return False


def is_right_choice_exist(pos, blocks):
    for i in blocks:
        if [pos[0] + 1, pos[1]] in i:
            return True
    return False


def is_left_choice_exist(pos, blocks):
    for i in blocks:
        if [pos[0] - 1, pos[1]] in i:
            return True
    return False


def main(stdscr, groups):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    current_choice = [0, 0]
    blocks = []

    while True:

        drawable_groups, drawable_items = calculate_menu(
            current_choice, groups, blocks)

        draw_menu(stdscr, drawable_groups, drawable_items)

        key = stdscr.getch()

        name_of_current_group = ""
        for i in blocks:
            if current_choice == i[0]:
                name_of_current_group = i[1]

        if key in UP and current_choice[1] != 0:
            current_choice[1] -= 1
        if (
            key in DOWN
            and current_choice[1] != len(groups[name_of_current_group]) - 1
        ):
            current_choice[1] += 1
        if key in RIGHT:
            if is_right_choice_exist(current_choice, blocks):
                current_choice[0] += 1
            elif is_right_exist(current_choice, blocks):
                rows = len(groups[name_of_pos_group(
                    current_choice[0] + 1, blocks)]) - 1
                current_choice = [current_choice[0] + 1, rows]
        if key in LEFT:
            if is_left_choice_exist(current_choice, blocks):
                current_choice[0] -= 1
            elif is_left_exist(current_choice, blocks):
                rows = len(groups[name_of_pos_group(
                    current_choice[0] - 1, blocks)]) - 1
                current_choice = [current_choice[0] - 1, rows]
        if key in ENTER:
            edit_config(name_of_position(current_choice, blocks, groups))
            exit()
        if key in EXIT:
            exit(0)
