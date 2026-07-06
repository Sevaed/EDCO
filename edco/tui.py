from . import commands
from edco.data import get_apps_data
import curses
from curses import wrapper


UP = [curses.KEY_UP, ord("k"), ord("w")]
DOWN = [curses.KEY_DOWN, ord("j"), ord("s")]
RIGHT = [curses.KEY_RIGHT, ord("l"), ord("d")]
LEFT = [curses.KEY_LEFT, ord("h"), ord("a")]
ENTER = [curses.KEY_ENTER, 10, 13, ord(" ")]
EXIT = [ord("q"), 27]


ASCII_CODES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[36m",
    "YELLOW": "\033[33m",
    "GREEN": "\033[32m",
    "RED": "\033[1;31m",
}

apps_data = get_apps_data()


def main(stdscr, infinite):
    exit("TODO")


def run_tui(infinite=False):
    wrapper(main, infinite)
