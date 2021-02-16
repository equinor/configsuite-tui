from dateutil.parser import isoparse
import npyscreen
import pluggy
from fastnumbers import fast_real
from configsuite import MetaKeys as MK
from configsuite_tui.config_tools import save, load, validate
from configsuite_tui.custom_widgets import CustomFormMultiPageWithMenus
from configsuite_tui import hookspecs
from tests.schemas import test_schema_1


def tui(**kwargs):
    tui.schema = {}
    tui.schema_name = ""
    tui.schema_list = {}
    tui.config = {}
    tui.valid = False

    pm = get_plugin_manager()
    for s in pm.hook.configsuite_tui_schema():
        tui.schema_list.update(s)

    App = Interface()
    if "test" in kwargs and kwargs["test"]:
        tui.test = True
        tui.schema = tui.schema_list["test"]
        tui.schema_name = list(tui.schema_list.keys())[0]
        App.run(fork=False)
    else:
        tui.test = False
        App.run()
    return tui.config, tui.valid


def get_plugin_manager():
    pm = pluggy.PluginManager("configsuite_tui")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("configsuite_tui")
    pm.register(test_schema_1)
    return pm


class Interface(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())
        self.registerForm("SAVE", SaveForm())
        self.registerForm("LOAD", LoadForm())
        self.registerForm("SCHEMA", LoadSchema())


class SchemaForm(CustomFormMultiPageWithMenus):
    def create(self):
        self.name = "Config Suite TUI"
        self.footer = (
            " ^X-Menu , ^A-Load Schema , ^S-Save Config , "
            + "^L-Load Config , ^D-Show Field Description , ^Q-Quit "
        )
        self.schemawidgets = {}

        # Add keyboard shortcuts
        self.add_handlers({"^Q": self.exit_application})
        self.add_handlers({"^A": self.load_schema})
        self.add_handlers({"^S": self.save_config})
        self.add_handlers({"^L": self.load_config})
        self.add_handlers({"^D": self.show_field_description})

        # Add info text
        self.schemainfo = self.add(
            npyscreen.FixedText,
            value=" Load a schema from the menu or using the keybind Ctrl+A ",
        )

        # Add menu
        self.m1 = self.add_menu(name="Main Menu")
        self.m1.addItemsFromList(
            [
                ("Load schema", self.load_schema, "^A"),
                ("Save configuration file", self.save_config, "^S"),
                ("Load configuration file", self.load_config, "^L"),
                ("Exit Application", self.exit_application, "^Q"),
            ]
        )

        # Add widgets from schema
        if tui.schema:
            self.render_schema()

    def adjust_widgets(self, *args, **keywords):
        if tui.schema:
            for s in tui.schema[MK.Content]:
                basic_type = tui.schema[MK.Content][s][MK.Type][0]
                value = self.schemawidgets[s].value
                if basic_type in ["integer", "number"]:
                    tui.config[s] = fast_real(value)
                elif basic_type == "bool" and isinstance(value, int):
                    tui.config[s] = bool(value)
                elif basic_type == "date":
                    try:
                        tui.config[s] = isoparse(value).date()
                    except ValueError:
                        tui.config[s] = None
                elif basic_type == "datetime":
                    try:
                        tui.config[s] = isoparse(value)
                    except ValueError:
                        tui.config[s] = None
                else:
                    tui.config[s] = value

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
        supported_types = ["string", "integer", "number", "date", "datetime", "bool"]
        if not tui.test:
            self._clear_all_widgets()
        for s in tui.schema[MK.Content]:
            basic_type = tui.schema[MK.Content][s][MK.Type][0]
            name = s + " (" + basic_type + "):"
            if basic_type == "bool":
                self.schemawidgets[s] = self.add_widget_intelligent(
                    npyscreen.TitleCombo,
                    name=name,
                    use_two_lines=False,
                    begin_entry_at=len(name) + 1,
                    values=[False, True],
                )
            else:
                self.schemawidgets[s] = self.add_widget_intelligent(
                    npyscreen.TitleText,
                    name=name,
                    use_two_lines=False,
                    begin_entry_at=len(name) + 1,
                )

            if basic_type not in supported_types:
                npyscreen.notify_confirm(
                    "Field: '"
                    + s
                    + "' with Type: '"
                    + basic_type
                    + "' is currently not supported in this version of Config "
                    + "Suite TUI and has been rendered as a standard text field.",
                    title="Error",
                )
            self.validate_config()

    def validate_config(self, *args, **keywords):
        if tui.schema:
            tui.valid = validate(tui.config, tui.schema)
            if tui.valid:
                self.color = "GOOD"
                self.name = (
                    "Config Suite TUI - Schema: " + tui.schema_name + " - Config: Valid"
                )
            else:
                self.color = "DEFAULT"
                self.name = (
                    "Config Suite TUI - Schema: "
                    + tui.schema_name
                    + " - Config: Not Valid"
                )
            self.display()

    def show_field_description(self, *args, **keywords):
        try:
            description = tui.schema[MK.Content][
                list(tui.schema[MK.Content])[self.editw]
            ][MK.Description]

        except KeyError:
            description = "This field has no description."

        npyscreen.notify_confirm(
            description, title=self._widgets_by_id[self.editw].name
        )

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
        save(tui.config, self.filename.value)
        self.parentApp.switchFormPrevious()


class LoadForm(npyscreen.ActionPopup):
    def create(self):
        self.name = "Load configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        tui.config = load(self.filename.value)
        for s in tui.schema[MK.Content]:
            basic_type = tui.schema[MK.Content][s][MK.Type][0]
            if s in tui.config:
                if basic_type in ["string", "integer", "number", "date", "datetime"]:
                    self.parentApp.getForm("MAIN").schemawidgets[s].value = str(
                        tui.config[s]
                    )
                elif basic_type == "bool":
                    self.parentApp.getForm("MAIN").schemawidgets[s].value = int(
                        tui.config[s]
                    )
        self.parentApp.switchForm("MAIN")


class LoadSchema(npyscreen.ActionPopup):
    def create(self):
        self.name = "Load schema"
        values = list(tui.schema_list.keys())
        self.schema_choice = self.add(
            npyscreen.TitleCombo, name="Schema", values=values
        )

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        tui.schema = tui.schema_list[
            self.schema_choice.values[self.schema_choice.value]
        ]
        tui.schema_name = self.schema_choice.values[self.schema_choice.value]
        self.parentApp.getForm("MAIN").schemainfo.value = "Schema: " + tui.schema_name
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.switchForm("MAIN")
