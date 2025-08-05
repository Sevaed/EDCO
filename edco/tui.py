from edco.data import get_data
from edco.commands import edit_config

import curses
from curses import wrapper

import sys


def run_tui():
    data = get_data()

    def data_to_groups(data: dict) -> dict:
        groups = {}
        ungroup = []
        for i in data:
            if "group" in data[i]:
                group = data[i]["group"]
                if group not in groups:
                    groups[group] = []
                groups[group].append(i)
            else:
                ungroup.append(i)
        groups = dict(sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])))
        groups["nogroup"] = ungroup
        return groups

    groups = data_to_groups(data)

    UP = [curses.KEY_UP, ord("k"), ord("w")]
    DOWN = [curses.KEY_DOWN, ord("j"), ord("s")]
    RIGHT = [curses.KEY_RIGHT, ord("l"), ord("d")]
    LEFT = [curses.KEY_LEFT, ord("h"), ord("a")]
    ENTER = [curses.KEY_ENTER, 10, 13, ord(" ")]
    EXIT = [ord("q")]

    def main(stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        current_choice = [0, 0]
        blocks = []

        def draw_menu():
            def is_not_enough_space(block_width: int):
                if x + block_width > max_x:
                    return True
                else:
                    return False

            max_y, max_x = stdscr.getmaxyx()
            blocks.clear()
            stdscr.clear()
            y = 2
            x = 2
            next_maxwith = 0
            next_maxheight = 0
            for count, name in enumerate(groups.keys()):
                block_width = len(max(groups[name], key=len))
                cur_y = stdscr.getyx()[0]
                if is_not_enough_space(block_width):
                    if len(groups[name]) + cur_y + 1 > max_y:
                        curses.endwin()
                        exit("too small")
                    y += next_maxheight
                    x = 2
                    next_maxwith = 0
                x += next_maxwith + 2

                maxheight = 0
                maxwith = 0

                group_string = "▼ " + name
                if name != "nogroup":
                    stdscr.addstr(y, x, group_string, curses.color_pair(1))
                    col = 2
                elif groups[name]:
                    stdscr.addstr(y, x, group_string, curses.color_pair(3))
                    col = 4
                else:
                    col = 2

                if len(group_string) > maxwith:
                    maxwith = len(group_string)

                for counto, obj in enumerate(groups[name]):
                    blocks.append(([count, counto], name, obj))
                    if counto != len(groups[name]) - 1:
                        line = "├── " + obj
                    else:
                        line = "└── " + obj
                    if [count, counto] == current_choice:
                        stdscr.addstr(y + counto + 1, x, line, curses.A_REVERSE)
                    else:
                        stdscr.addstr(y + counto + 1, x, line, curses.color_pair(col))

                if len(max(groups[name], key=len)) + 4 > maxwith:
                    maxwith = len(max(groups[name], key=len)) + 4

                next_maxheight = maxheight
                next_maxwith = maxwith

        draw_menu()

        while True:
            key = stdscr.getch()

            def name_of_position(pos):
                for i in blocks:
                    if pos == i[0]:
                        return groups[i[1]][i[0][1]]
                exit(1)

            name_of_current_group = ""
            for i in blocks:
                if current_choice == i[0]:
                    name_of_current_group = i[1]

            def name_of_pos_group(numb):
                for i in blocks:
                    if i[0][0] == numb:
                        return i[1]
                exit(1)

            def is_right_exist(pos):
                for i in blocks:
                    if pos[0] + 1 == i[0][0]:
                        return True
                return False

            def is_left_exist(pos):
                for i in blocks:
                    if pos[0] - 1 == i[0][0]:
                        return True
                return False

            def is_right_choice_exist(pos):
                for i in blocks:
                    if [pos[0] + 1, pos[1]] in i:
                        return True
                return False

            def is_left_choice_exist(pos):
                for i in blocks:
                    if [pos[0] - 1, pos[1]] in i:
                        return True
                return False

            if key in UP and current_choice[1] != 0:
                current_choice[1] -= 1
            if (
                key in DOWN
                and current_choice[1] != len(groups[name_of_current_group]) - 1
            ):
                current_choice[1] += 1
            if key in RIGHT:
                if is_right_choice_exist(current_choice):
                    current_choice[0] += 1
                elif is_right_exist(current_choice):
                    rows = len(groups[name_of_pos_group(current_choice[0] + 1)]) - 1
                    current_choice = [current_choice[0] + 1, rows]
                else:
                    for i in blocks:
                        if [0, current_choice[1]] in i:
                            current_choice = [0, current_choice[1]]
                            draw_menu()
                            break
                    else:
                        current_choice = [0, 0]
            if key in LEFT:
                if is_left_choice_exist(current_choice):
                    current_choice[0] -= 1
                elif is_left_exist(current_choice):
                    rows = len(groups[name_of_pos_group(current_choice[0] - 1)]) - 1
                    current_choice = [current_choice[0] - 1, rows]
                elif current_choice[1] == blocks[-1][0][1]:
                    current_choice = [blocks[-1][0][0], current_choice[1]]
                else:
                    current_choice = [blocks[-1][0][0], 0]
            if key in ENTER:
                edit_config(name_of_position(current_choice))
                exit()
            if key in EXIT:
                return

            draw_menu()

    wrapper(main)
