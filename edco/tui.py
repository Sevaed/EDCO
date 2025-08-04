from edco.data import get_data
from edco.commands import edit_config

import curses
from curses import wrapper

def run_tui():
    data = get_data("data")

    def data_to_TUIdata(data={}):
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

    groups = data_to_TUIdata(data)

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
            blocks.clear()
            stdscr.clear()
            x = 2
            maxlen = 0
            for count, name in enumerate(groups.keys()):
                x += maxlen
                y = 2
                if name != "nogroup":
                    stdscr.addstr(y, x, "▼ " + name, curses.color_pair(1))
                    col = 2
                elif groups[name]:
                    stdscr.addstr(y, x, "▼ " + name, curses.color_pair(3))
                    col = 4
                else:
                    col = 2
                for counto, obj in enumerate(groups[name]):
                    blocks.append(([count, counto], name))
                    if counto != len(groups[name]) - 1:
                        line = "├── " + obj
                    else:
                        line = "└── " + obj
                    if [count, counto] == current_choice:
                        stdscr.addstr(y + counto + 1, x, line, curses.A_REVERSE)
                    else:
                        stdscr.addstr(y + counto + 1, x, line, curses.color_pair(col))

                    if len(line) > maxlen:
                        maxlen = len(line)

        draw_menu()

        while True:
            key = stdscr.getch()

            def name_of_position(pos):
                for i in blocks:
                    if pos in i:
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
            if key in LEFT:
                if is_left_choice_exist(current_choice):
                    current_choice[0] -= 1
                elif is_left_exist(current_choice):
                    rows = len(groups[name_of_pos_group(current_choice[0] - 1)]) - 1
                    current_choice = [current_choice[0] - 1, rows]
            if key in ENTER:
                edit_config(name_of_position(current_choice))
                exit()
            if key in EXIT:
                exit(0)

            draw_menu()

    wrapper(main)

