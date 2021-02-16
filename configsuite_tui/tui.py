from dateutil.parser import isoparse
import npyscreen
import pluggy
from fastnumbers import fast_real
from configsuite import MetaKeys as MK
from configsuite_tui.config_tools import save, load, validate
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
        tui.test = True
        schema = schema_list["test"]
        schema_name = list(schema_list.keys())[0]
        App.run(fork=False)
    else:
        tui.test = False
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


class SchemaForm(npyscreen.FormMultiPageWithMenus):
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
                basic_type = schema[MK.Content][s][MK.Type][0]
                value = self.schemawidgets[s].value
                if basic_type in ["string", "integer", "number"]:
                    config[s] = fast_real(value)
                elif basic_type == "bool" and isinstance(value, int):
                    config[s] = bool(value)
                elif basic_type == "date":
                    try:
                        config[s] = isoparse(value).date()
                    except ValueError:
                        config[s] = None
                elif basic_type == "datetime":
                    try:
                        config[s] = isoparse(value)
                    except ValueError:
                        config[s] = None
                else:
                    config[s] = None

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
        if not tui.test:
            self._clear_all_widgets()
        for s in schema[MK.Content]:
            basic_type = schema[MK.Content][s][MK.Type][0]
            name = s + " (" + basic_type + "):"
            if basic_type in ["string", "integer", "number", "date", "datetime"]:
                self.schemawidgets[s] = self.add_widget_intelligent(
                    npyscreen.TitleText,
                    name=name,
                    use_two_lines=False,
                    begin_entry_at=len(name) + 1,
                )
            elif basic_type == "bool":
                self.schemawidgets[s] = self.add_widget_intelligent(
                    npyscreen.TitleCombo,
                    name=name,
                    use_two_lines=False,
                    begin_entry_at=len(name) + 1,
                    values=[False, True],
                )

            self.validate_config()

    def validate_config(self, *args, **keywords):
        global valid
        if schema:
            valid = validate(config, schema)
            if valid:
                self.color = "GOOD"
                self.name = (
                    "Config Suite TUI - Schema: " + schema_name + " - Config: Valid"
                )
            else:
                self.color = "DEFAULT"
                self.name = (
                    "Config Suite TUI - Schema: " + schema_name + " - Config: Not Valid"
                )
            self.display()

    def exit_application(self, *args, **keywords):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


class SaveForm(npyscreen.ActionPopup):
    def create(self):
        self.name = "Save configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

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
            basic_type = schema[MK.Content][s][MK.Type][0]
            if s in config:
                if basic_type in ["string", "integer", "number", "date", "datetime"]:
                    self.parentApp.getForm("MAIN").schemawidgets[s].value = str(
                        config[s]
                    )
                elif basic_type == "bool":
                    self.parentApp.getForm("MAIN").schemawidgets[s].value = int(
                        config[s]
                    )
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
