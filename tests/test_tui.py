import curses
import sys
from unittest import TestCase
import npyscreen
from configsuite_tui.tui import tui


class TestTui(TestCase):
    def test_tui_returns_correct_config(self):
        npyscreen.add_test_input_from_iterable("Joe Biden")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.add_test_input_from_iterable("President")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.add_test_input_from_iterable("78")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append("^Q")

        config = tui(test=True)
        sys.stdout.write(str(config))
        self.assertEqual(
            config,
            {"name": "Joe Biden", "hobby": "President", "age": 78},
        )
