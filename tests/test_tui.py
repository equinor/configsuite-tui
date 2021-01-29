import curses
import os
import tempfile
import shutil
from unittest import TestCase
import npyscreen
from configsuite_tui.tui import tui
from configsuite_tui.config import save


class TestTui(TestCase):
    def setUp(self):
        # Create temporary directory
        self.tmpdir = tempfile.mkdtemp()

        os.chdir(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_tui_input_save_return_validate(self):
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            testinput = [
                "Jane Doe",
                curses.KEY_DOWN,
                "Electrician",
                curses.KEY_DOWN,
                "35",
                curses.KEY_DOWN,
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
                {"name": "Jane Doe", "hobby": "Electrician", "age": 35},
            )
            self.assertTrue(valid)
            self.assertEqual(
                tmpfile.read(), b"name: Jane Doe\nhobby: Electrician\nage: 35\n"
            )

    def test_tui_load_return_validate(self):
        config = {"name": "John Doe", "hobby": "Carpenter", "age": 45}
        with tempfile.NamedTemporaryFile(dir=self.tmpdir) as tmpfile:
            save(config, tmpfile.name)
            testinput = [
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                curses.KEY_DOWN,
                "^L",
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
                {"name": "John Doe", "hobby": "Carpenter", "age": 45},
            )
            self.assertTrue(valid)

    def test_cancel_forms_and_no_fork(self):
        testinput = [
            curses.KEY_DOWN,
            curses.KEY_DOWN,
            curses.KEY_DOWN,
            "^L",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^S",
            curses.KEY_DOWN,
            curses.ascii.NL,
            "^Q",
        ]
        npyscreen.TEST_SETTINGS["TEST_INPUT"] = testinput
        config, valid = tui()

        self.assertEqual(config, {"age": "", "hobby": "", "name": ""})
        self.assertFalse(valid)
