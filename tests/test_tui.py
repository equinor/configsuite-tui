import curses
from unittest import TestCase
import npyscreen
from configsuite_tui.tui import tui


# def test_enter_config_and_return_on_exit():
#     pobj = pexpect.spawn("/bin/bash")
#     pobj.sendline("python3 script.py")
#     pobj.expect(pexpect.EOF)
#     assert pobj.before == "test"


class TestTui(TestCase):
    def test_tui(self):
        npyscreen.add_test_input_from_iterable("First line")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.add_test_input_from_iterable("Second line")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.add_test_input_from_iterable("123")
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append(curses.KEY_DOWN)
        npyscreen.TEST_SETTINGS["TEST_INPUT"].append("^Q")

        npyscreen.TEST_SETTINGS["CONTINUE_AFTER_TEST_INPUT"] = True

        config = tui(test=True)
        # now, do some assertions (see later)
        self.assertEqual(
            config, {"name": "First line", "hobby": "Second line", "age": "123"}
        )
