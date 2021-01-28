import curses
import sys
import os
import select
from unittest import TestCase
import npyscreen
import pyte
from configsuite_tui.tui import tui


class TestTui(TestCase):
    def test_tui_returns_correct_config(self):
        pid, f_d = os.forkpty()
        if pid == 0:
            npyscreen.add_test_input_from_iterable("Joe Biden")
            npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
            npyscreen.add_test_input_from_iterable("President")
            npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
            npyscreen.add_test_input_from_iterable("78")
            npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
            npyscreen.TEST_SETTINGS["TEST_INPUT"].append("^Q")

            config = tui(test=True)
            sys.stdout.write(str(config))

        else:
            screen = pyte.Screen(60, 24)
            stream = pyte.ByteStream(screen)
            while True:
                try:
                    [f_d], _, _ = select.select([f_d], [], [], 1)
                except (KeyboardInterrupt, ValueError):
                    break
                else:
                    try:
                        data = os.read(f_d, 1024)
                        stream.feed(data)
                    except OSError:
                        break

            self.assertEqual(
                screen.display[-1],
                "{'name': 'Joe Biden', 'hobby': 'President', 'age': 78}      ",
            )
