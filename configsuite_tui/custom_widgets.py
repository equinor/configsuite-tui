import curses
from npyscreen import FormMultiPage, wgNMenuDisplay


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
