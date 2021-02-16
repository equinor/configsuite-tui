import datetime
import curses
import os
import tempfile
import shutil
from unittest import TestCase
import npyscreen
from configsuite_tui.tui import tui
from configsuite_tui.config_tools import save


class Test_Tui_With_Files(TestCase):
    def setUp(self):
        # Create temporary directory
        self.tmpdir = tempfile.mkdtemp()

        os.chdir(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tui_input_save_return_validate(self):
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            testinput = [
                curses.KEY_DOWN,
                "Jane Doe",
                curses.KEY_DOWN,
                "Electrician",
                curses.KEY_DOWN,
                "35",
                curses.KEY_DOWN,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.ascii.NL,
                curses.KEY_DOWN,
                "45.35",
                curses.KEY_DOWN,
                "1999-01-01",
                curses.KEY_DOWN,
                "2011-11-04T00:05:23",
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                curses.KEY_UP,
                "^S",
                curses.ascii.NL,
                curses.KEY_RIGHT,
                curses.ascii.NL,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                curses.ascii.NL,
                "^Q",
            ]
            npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
            config, valid = tui(test=True)

            self.assertEqual(
                config,
                {
                    "name": "Jane Doe",
                    "hobby": "Electrician",
                    "age": 35,
                    "active": True,
                    "score": 45.35,
                    "birthday": datetime.date(1999, 1, 1),
                    "last_seen": datetime.datetime(2011, 11, 4, 0, 5, 23),
                },
            )
            self.assertTrue(valid)
            self.assertEqual(
                tmpfile.read(),
                b"name: Jane Doe\nhobby: Electrician\nage: 35\nactive: true\nscore: \
45.35\nbirthday: 1999-01-01\nlast_seen: 2011-11-04 00:05:23\n",
            )

    def test_tui_load_return_validate(self):
        config = {
            "name": "John Doe",
            "hobby": "Carpenter",
            "age": 45,
            "active": True,
            "score": 23.54,
            "birthday": datetime.date(1999, 2, 2),
            "last_seen": datetime.datetime(2011, 12, 4, 0, 4, 15),
        }
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            save(config, tmpfile.name)
            testinput = [
                "^D",
                curses.ascii.NL,
                curses.KEY_RIGHT,
                curses.ascii.NL,
                curses.ascii.NL,
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                curses.ascii.NL,
                "^Q",
            ]
            npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
            config, valid = tui(test=True)

            self.assertEqual(
                config,
                {
                    "name": "John Doe",
                    "hobby": "Carpenter",
                    "age": 45,
                    "active": True,
                    "score": 23.54,
                    "birthday": datetime.date(1999, 2, 2),
                    "last_seen": datetime.datetime(2011, 12, 4, 0, 4, 15),
                },
            )
            self.assertTrue(valid)

    def test_cancel_forms_and_no_fork(self):
        testinput = [
            "^A",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^S",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^D",
            curses.KEY_DOWN,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.KEY_UP,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui()

        self.assertEqual(config, {})
        self.assertFalse(valid)

    def test_load_schema(self):
        testinput = [
            "^A",
            curses.ascii.NL,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.KEY_DOWN,
            curses.ascii.NL,
            curses.KEY_DOWN,
            curses.KEY_UP,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui(test=True)

        self.assertEqual(
            config,
            {
                "name": "",
                "hobby": "",
                "age": "",
                "active": None,
                "score": "",
                "birthday": None,
                "last_seen": None,
            },
        )
        self.assertFalse(valid)
