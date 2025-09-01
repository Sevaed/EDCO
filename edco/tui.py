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
    """
    Gets raw json EDCO config data
    returns dict with structure {
    group_name: list of elements
    ungroup: list of elements without group
    }
    """
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
    
    # sorting groups by:
    # - item's name length 
    # - after that by first digit in alphabetical sorting
    groups = dict(
        sorted(groups.items(), 
               key=lambda item: (-len(item[1]), item[0])
               )
    )

    groups["ungroup"] = ungroup
    return groups



groups = data_to_groups(get_data())
curr_curs_cords = [0, 0, 0]

class Element:
    def __init__(self, y: int, x: int, group: str, name: str, is_last: bool):
        self.y = y
        self.x = x
        self.group = group
        self.name = name
        self.curs_cords = []
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
        curs_y = 0
        curs_x = 0
        curr_row = 0
        curs_cords = {}

        for group in groups:
            col = Column(x, y, group)
            if curs_x in curs_cords:
                curs_y = curs_cords[curs_x]
            for element in col.elements:
                element.curs_cords = [curs_y, curs_x, curr_row]
                curs_y += 1
                curs_cords[curs_x] = curs_y
            if col.x + col.width > term_x:
                y += self.row_height[curr_row] + 2
                x = 2
                col = Column(x, y, group)
                curr_row += 1
                self.row_height[curr_row] = col.height
                x += col.width + 2
                curs_x = 0
                curs_y = curs_cords[curs_x]
                for element in col.elements:
                    element.curs_cords = [curs_y, curs_x, curr_row]
                    curs_y += 1
                    curs_cords[curs_x] = curs_y

            else:
                if col.height > self.row_height[curr_row]:
                    self.row_height[curr_row] = col.height
                x += col.width + 2
                curs_y = 0
            curs_x += 1
            print(group)
            for i in col.elements:
                print(i.curs_cords)
            columns.append(col)
        self.columns = columns


class Controls:
    def __init__(self, elements):
        self.elements = elements
        self.cords = []
        for element in elements:
            self.cords.append(element.curs_cords)
        only_curs_cords = []
        for something in self.cords:
            only_curs_cords.append([something[0], something[1]])

    def move_cursor(self, direct: str):
        global curr_curs_cords
        pos = curr_curs_cords
        upper = [[pos[0]-1, pos[1]], pos[0]-1]
        downer = [[pos[0]+1, pos[1]], pos[0]+1]
        righter = [[pos[0], pos[1]+1], pos[1]+1]
        lefter = [[pos[0], pos[1]-1], pos[1]-1]
        cords = self.cords
        if direct == "up" and upper in cords:
            curr_curs_cords = upper
        if direct == "down" and downer in cords:
            curr_curs_cords = downer
        if direct == "right" and righter in cords:
            curr_curs_cords = righter
        if direct == "left" and lefter in cords:
            curr_curs_cords = lefter

    def get_name(self):
        pos = curr_curs_cords
        for element in self.elements:
            if pos == element.curs_cords:
                return element.name


def run_tui():

    test = Screen(groups, [57, 61])

    def main(stdscr):
        curr_screen = None

        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        def draw_menu():
            nonlocal curr_screen
            stdscr.clear()
            term_size = stdscr.getmaxyx()
            to_draw = Screen(groups, term_size)
            curr_screen = to_draw
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

                    if curr_curs_cords == element.curs_cords:
                        stdscr.addstr(el_y, el_x, el_name, curses.A_REVERSE)
                    else:
                        stdscr.addstr(el_y, el_x, el_name,
                                      curses.color_pair(color))
            stdscr.refresh()
        draw_menu()

        while True:
            elements = []
            if curr_screen is None:
                exit("sys")
            for column in curr_screen.columns:  # type: ignore
                for element in column.elements:
                    elements.append(element)
            contr = Controls(elements)
            key = stdscr.getch()

            if key in UP:
                contr.move_cursor("up")
            if key in DOWN:
                contr.move_cursor("down")
            if key in RIGHT:
                contr.move_cursor("roght")
            if key in LEFT:
                contr.move_cursor("left")

            if key in ENTER:
                edit_config(contr.get_name())

            if key in EXIT:
                exit()

            draw_menu()

    wrapper(main)
