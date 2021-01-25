import npyscreen
from configsuite import types
from configsuite import MetaKeys as MK
from .config import load

schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "name": {MK.Type: types.String},
        "hobby": {MK.Type: types.String},
        "age": {MK.Type: types.Integer},
    },
}

config = load("./tests/data/simple.yml")


class TUI(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())


class SchemaForm(npyscreen.FormBaseNewWithMenus):
    def create(self):
        self.name = "ConfigSuite TUI"
        for s in schema[MK.Content]:
            globals()[s] = self.add(
                npyscreen.TitleText,
                name=s + " (" + schema[MK.Content][s][MK.Type][0] + "):",
                value=str(config[s]),
                use_two_lines=False,
            )

    def while_editing(self, *args, **keywords):
        pass

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def validate_config(self):
        pass

    def save_config(self):
        pass
