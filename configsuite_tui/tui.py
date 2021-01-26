import npyscreen
from configsuite import types
from configsuite import MetaKeys as MK

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "name": {MK.Type: types.String},
        "hobby": {MK.Type: types.String},
        "age": {MK.Type: types.Integer},
    },
}

config = {}


def tui(**kwargs):
    App = Interface()
    if "test" in kwargs and kwargs["test"]:
        App.run(fork=False)
    else:
        App.run()
    return config


class Interface(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())


class SchemaForm(npyscreen.FormWithMenus):
    def create(self):
        self.name = "ConfigSuite TUI"
        self.widgetList = {}

        # Add keyboard shortcuts
        self.add_handlers({"^Q": self.exit_application})

        # Add widgets from schema
        for s in schema[MK.Content]:
            self.widgetList[s] = self.add(
                npyscreen.TitleText,
                name=s + " (" + schema[MK.Content][s][MK.Type][0] + "):",
            )

        # Add menu
        self.m1 = self.add_menu(name="Main Menu")
        self.m1.addItemsFromList(
            [
                ("Save configuration file", self.save_config),
                ("Load configuration file", self.load_config),
                ("Validate configuration", self.validate_config),
                ("Exit Application", self.exit_application),
            ]
        )

    def while_editing(self, *args, **keywords):
        for s in schema[MK.Content]:
            config[s] = self.widgetList[s].value

    def save_config(self):
        pass

    def load_config(self):
        pass

    def validate_config(self):
        pass

    def exit_application(self, *args, **keywords):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()
