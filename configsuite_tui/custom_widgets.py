import curses
from npyscreen import FormMultiPage, fmActionFormV2, ActionPopup, NPSAppManaged


class CustomNPSAppManaged(NPSAppManaged):
    def removeCurrentFromHistory(self):
        self._FORM_VISIT_LIST.pop()


class CustomFormMultiPage(FormMultiPage):
    OK_BUTTON_TEXT = "Back"

    def __init__(self, *args, **keywords):
        super(CustomFormMultiPage, self).__init__(*args, **keywords)
        self.edit_return_value = None
        self.action = False

    def display_footer_at(self):
        return self.lines - 1, 1

    def draw_form(self, *args, **keywords):
        super(CustomFormMultiPage, self).draw_form()
        footer = self.footer
        if isinstance(footer, bytes):
            footer = footer.decode("utf-8", "replace")
        y, x = self.display_footer_at()
        self.add_line(
            y,
            x,
            footer,
            self.make_attributes_list(footer, curses.A_NORMAL),
            self.columns - x - 1,
        )

    def on_ok(self):
        pass

    def pre_edit_loop(self):
        if self.action:
            self._page_for_buttons = len(self._pages__) - 1
            self.switch_page(self._page_for_buttons)

            # Add ok and cancel buttons. Will remove later
            tmp_rely, tmp_relx = self.nextrely, self.nextrelx

            my, mx = self.curses_pad.getmaxyx()
            ok_button_text = self.OK_BUTTON_TEXT
            my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
            mx -= len(ok_button_text) + self.__class__.OK_BUTTON_BR_OFFSET[1]
            self.ok_button = self.add_widget(
                self.__class__.OKBUTTON_TYPE,
                name=ok_button_text,
                rely=my,
                relx=mx,
                use_max_space=True,
            )
            self._ok_button_postion = len(self._widgets__) - 1
            # End add buttons
            self.nextrely, self.nextrelx = tmp_rely, tmp_relx
            self.switch_page(0)

    def _during_edit_loop(self):
        if self.action:
            if self.ok_button.value:
                self.editing = False
                self.ok_button.value = False
                self.edit_return_value = self.on_ok()

    def resize(self):
        if self.action:
            super(CustomFormMultiPage, self).resize()
            self.move_ok_button()

    def move_ok_button(self):
        if self.action:
            if hasattr(self, "ok_button"):
                my, mx = self.curses_pad.getmaxyx()
                my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
                mx -= (
                    len(self.__class__.OK_BUTTON_TEXT)
                    + self.__class__.OK_BUTTON_BR_OFFSET[1]
                )
                self.ok_button.relx = mx
                self.ok_button.rely = my

    def post_edit_loop(self):
        if self.action:
            self.switch_page(self._page_for_buttons)
            self.ok_button.destroy()
            del self._widgets__[self._ok_button_postion]
            del self.ok_button
            # self.nextrely, self.nextrelx = tmp_rely, tmp_relx
            self.display()
            self.editing = False

            return self.edit_return_value


class CustomEditListPopup(fmActionFormV2.ActionFormV2):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 30
    SHOW_ATX = 10
    SHOW_ATY = 2
    OK_BUTTON_TEXT = "Back"

    def create_control_buttons(self):
        self._add_button(
            "ok_button",
            self.__class__.OKBUTTON_TYPE,
            self.__class__.OK_BUTTON_TEXT,
            0 - self.__class__.OK_BUTTON_BR_OFFSET[0],
            0
            - self.__class__.OK_BUTTON_BR_OFFSET[1]
            - len(self.__class__.OK_BUTTON_TEXT),
            None,
        )


class CustomLoadPopup(ActionPopup):
    OK_BUTTON_TEXT = "Load"
    CANCEL_BUTTON_TEXT = "Back"


class CustomSavePopup(ActionPopup):
    OK_BUTTON_TEXT = "Save"
    CANCEL_BUTTON_TEXT = "Back"
