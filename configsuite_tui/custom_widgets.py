import curses
from npyscreen import FormMultiPage, wgNMenuDisplay, fmActionFormV2, ActionPopup


class CustomFormMultiPageWithMenus(FormMultiPage, wgNMenuDisplay.HasMenus):
    def __init__(self, *args, **keywords):
        super(CustomFormMultiPageWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

    def display_footer_at(self):
        return self.lines - 1, 1

    def draw_form(self, *args, **keywords):
        super(CustomFormMultiPageWithMenus, self).draw_form()
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
