import npyscreen
from fastnumbers import fast_real
from configsuite import types
from configsuite import MetaKeys as MK
from configsuite_tui.config import save, load, validate


schema = {
    MK.Type: types.NamedDict,
    MK.Content: {
        "name": {MK.Type: types.String},
        "hobby": {MK.Type: types.String},
        "age": {MK.Type: types.Integer},
    },
}

config = {}
valid = False


def tui(**kwargs):
    App = Interface()
    if "test" in kwargs and kwargs["test"]:
        App.run(fork=False)
    else:
        App.run()
    return config, valid


class Interface(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())
        self.registerForm("SAVE", SaveForm())
        self.registerForm("LOAD", LoadForm())


class SchemaForm(npyscreen.FormBaseNewWithMenus):
    def create(self):
        self.name = "ConfigSuite TUI"
        self.schemawidgets = {}

        # Add keyboard shortcuts
        self.add_handlers({"^Q": self.exit_application})
        self.add_handlers({"^S": self.save_config})
        self.add_handlers({"^L": self.load_config})
        self.add_handlers({"^V": self.validate_config})

        # Add widgets from schema
        for s in schema[MK.Content]:
            self.schemawidgets[s] = self.add(
                npyscreen.TitleText,
                name=s + " (" + schema[MK.Content][s][MK.Type][0] + "):",
                use_two_lines=False,
            )

        # Add menu
        self.m1 = self.add_menu(name="Main Menu")
        self.m1.addItemsFromList(
            [
                ("Save configuration file", self.save_config, "^S"),
                ("Load configuration file", self.load_config, "^L"),
                ("Validate configuration", self.validate_config, "^V"),
                ("Exit Application", self.exit_application, "^Q"),
            ]
        )
        # Add validation text
        self.validschema = self.add(
            npyscreen.FixedText,
            value="Configuration not valid",
            color="CRITICAL",
            rely=-3,
        )

    def while_editing(self, *args, **keywords):
        global config
        for s in schema[MK.Content]:
            config[s] = fast_real(self.schemawidgets[s].value)
        self.validate_config()

    def save_config(self, *args, **keywords):
        self.parentApp.setNextForm("SAVE")
        self.parentApp.switchFormNow()

    def load_config(self, *args, **keywords):
        self.parentApp.setNextForm("LOAD")
        self.parentApp.switchFormNow()

    def validate_config(self, *args, **keywords):
        global valid
        valid = validate(config, schema)
        if valid:
            self.validschema.value = "Configuration valid"
            self.validschema.color = "SAFE"
        else:
            self.validschema.value = "Configuration not valid"
            self.validschema.color = "CRITICAL"

    def exit_application(self, *args, **keywords):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


class SaveForm(npyscreen.ActionPopup):
    def create(self):
        self.name = "Save configuration file"
        self.filename = self.add(
            npyscreen.TitleFilenameCombo,
            name="Filename",
        )

    def beforeEditing(self):
        self.filename.value = self.parentApp.getForm("LOAD").filename.value

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        save(config, self.filename.value)
        self.parentApp.switchFormPrevious()


class LoadForm(npyscreen.ActionPopup):
    def create(self):
        self.name = "Load configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        global config
        config = load(self.filename.value)
        for s in schema[MK.Content]:
            if s in config:
                self.parentApp.getForm("MAIN").schemawidgets[s].value = str(config[s])
        self.parentApp.switchForm("MAIN")
