import npyscreen
import pluggy
from fastnumbers import fast_real
from configsuite import MetaKeys as MK
from configsuite_tui.config import save, load, validate
from configsuite_tui import hookspecs, test_hook

schema = {}
schema_name = ""
schema_list = {}

config = {}
valid = False


def tui(**kwargs):
    global schema, schema_name, schema_list
    pm = get_plugin_manager()
    for s in pm.hook.configsuite_tui_schema():
        schema_list.update(s)

    App = Interface()
    if "test" in kwargs and kwargs["test"]:
        schema = schema_list["test"]
        schema_name = list(schema_list.keys())[0]
        App.run(fork=False)
    else:
        App.run()
    return config, valid


def get_plugin_manager():
    pm = pluggy.PluginManager("configsuite_tui")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("configsuite_tui")
    pm.register(test_hook)
    return pm


class Interface(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())
        self.registerForm("SAVE", SaveForm())
        self.registerForm("LOAD", LoadForm())
        self.registerForm("SCHEMA", LoadSchema())


class SchemaForm(npyscreen.FormBaseNewWithMenus):
    def create(self):
        self.name = "ConfigSuite TUI"
        self.schemawidgets = {}

        # Add keyboard shortcuts
        self.add_handlers({"^Q": self.exit_application})
        self.add_handlers({"^A": self.load_schema})
        self.add_handlers({"^S": self.save_config})
        self.add_handlers({"^D": self.load_config})

        self.schemainfo = self.add(
            npyscreen.FixedText, value="Load a schema from the menu"
        )

        # Add menu
        self.m1 = self.add_menu(name="Main Menu")
        self.m1.addItemsFromList(
            [
                ("Load schema", self.load_schema, "^A"),
                ("Save configuration file", self.save_config, "^S"),
                ("Load configuration file", self.load_config, "^D"),
                ("Exit Application", self.exit_application, "^Q"),
            ]
        )

        # Add widgets from schema
        if schema:
            self.render_schema()

    def adjust_widgets(self, *args, **keywords):
        global config
        if schema:
            for s in schema[MK.Content]:
                config[s] = fast_real(self.schemawidgets[s].value)
            self.validate_config()

    def save_config(self, *args, **keywords):
        self.parentApp.setNextForm("SAVE")
        self.parentApp.switchFormNow()

    def load_config(self, *args, **keywords):
        self.parentApp.setNextForm("LOAD")
        self.parentApp.switchFormNow()

    def load_schema(self, *args, **keywords):
        self.parentApp.setNextForm("SCHEMA")
        self.parentApp.switchFormNow()

    def render_schema(self, *args, **keywords):
        for s in schema[MK.Content]:
            self.schemawidgets[s] = self.add(
                npyscreen.TitleText,
                name=s + " (" + schema[MK.Content][s][MK.Type][0] + "):",
                use_two_lines=False,
            )
            self.display()

    def validate_config(self, *args, **keywords):
        global valid
        if schema:
            valid = validate(config, schema)
            if valid:
                self.schemainfo.value = (
                    "Schema: " + schema_name + " - Configuration valid"
                )
                self.schemainfo.color = "DEFAULT"
            else:
                self.schemainfo.value = (
                    "Schema: " + schema_name + " - Configuration not valid"
                )
                self.schemainfo.color = "DANGER"
            self.display()

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


class LoadSchema(npyscreen.ActionPopup):
    def create(self):
        self.name = "Load schema"
        values = list(schema_list.keys())
        self.schema_choice = self.add(
            npyscreen.TitleCombo, name="Schema", values=values
        )

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        global schema, schema_name
        schema = schema_list[self.schema_choice.values[self.schema_choice.value]]
        schema_name = self.schema_choice.values[self.schema_choice.value]
        self.parentApp.getForm("MAIN").schemainfo.value = "Schema: " + schema_name
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.switchForm("MAIN")
