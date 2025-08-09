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


def data_to_groups(data: dict) -> dict:
    groups = {}
    ungroup = []
    for element in data:
        if "group" in data[element]:
            group = data[element]["group"]
            if group not in groups:
                groups[group] = []
            groups[group].append(element)
        else:
            ungroup.append(element)
    groups = dict(
        sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])))
    groups["ungroup"] = ungroup
    return groups


groups = data_to_groups(get_data())


class Element:
    def __init__(self, y: int, x: int, group: str, name: str, is_last: bool):
        self.y = y
        self.x = x
        self.group = group
        self.name = name
        if is_last:
            self.disp_name = "└── " + name
        else:
            self.disp_name = "├── " + name


class Column:
    def __init__(self, x: int, start_y: int, group: str):
        self.x = x
        self.name_y = start_y
        self.group = group
        self.width = len(group)+2
        self.height: int = 1
        self.elements = []
        for count, el in enumerate(groups[group]):
            self.height += 1
            if count == len(groups[group])-1:
                is_last = True
            else:
                is_last = False
            self.elements.append(
                Element(start_y + count+1, x, group, el, is_last))
            if len(self.elements[-1].disp_name) > self.width:
                self.width = len(self.elements[-1].disp_name)


class Screen:
    def __init__(self, groups: dict, term_size: list):
        y = 2
        x = 2
        term_x = term_size[1]
        columns = []
        self.row_height = {0: 0}
        curr_row = 0
        for group in groups:
            print(group)
            col = Column(x, y, group)
            if col.x + col.width > term_x:
                print("Not enought space")
                y += self.row_height[curr_row] + 2
                x = 2
                col = Column(x, y, group)
                curr_row += 1
                self.row_height[curr_row] = col.height
                x += col.width + 2
            else:
                if col.height > self.row_height[curr_row]:
                    self.row_height[curr_row] = col.height
                x += col.width + 2
            columns.append(col)
            print(col.name_y, col.x)
            print(curr_row, col.height)
        self.columns = columns


def run_tui():

    # test = Screen(groups, [50, 30])

    def main(stdscr):

        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        def draw_menu():
            stdscr.clear()
            term_size = stdscr.getmaxyx()
            to_draw = Screen(groups, term_size)
            for Column in to_draw.columns:
                group = Column.group
                group_name = "▼ "+group
                group_y = Column.name_y
                group_x = Column.x
                elements = Column.elements
                if group == "ungroup":
                    color = 4
                else:
                    color = 2
                stdscr.addstr(group_y, group_x, group_name,
                              curses.color_pair(color - 1))
                for element in elements:
                    el_x = element.x
                    el_y = element.y
                    el_name = element.disp_name

                    stdscr.addstr(el_y, el_x, el_name,
                                  curses.color_pair(color))
            stdscr.refresh()
        draw_menu()

        while True:
            key = stdscr.getch()
            draw_menu()

            if key in EXIT:
                exit()

    wrapper(main)
