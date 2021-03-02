from dateutil.parser import isoparse
import npyscreen
import pluggy
from fastnumbers import fast_real
from configsuite import MetaKeys as MK
from configsuite_tui.config_tools import save, load, validate
from configsuite_tui.custom_widgets import (
    CustomFormMultiPage,
    CustomEditListPopup,
    CustomLoadPopup,
    CustomSavePopup,
)
from configsuite_tui import hookspecs, test_hook_named_dict, test_hook_list


def tui(**kwargs):
    tui.schema = {}
    tui.schema_name = ""
    tui.schema_list = {}
    tui.config = None
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
    pm.register(test_hook_named_dict)
    pm.register(test_hook_list)
    return pm


class Interface(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", SchemaForm())
        self.registerForm("SAVE", SaveConfig())
        self.registerForm("LOAD", LoadConfig())
        self.registerForm("SCHEMA", LoadSchema())
        self.registerForm("EDITLIST", EditListForm())


class SchemaForm(CustomFormMultiPage):
    def create(self):
        self.name = "Config Suite TUI"
        self.footer = self.footer = " ^A-Load Schema , ^Q-Quit "
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
            value=" Load a schema from the menu using the keybind Ctrl+A ",
        )

        # Add widgets from schema
        if tui.schema:
            self.render_schema()

    def render_schema(self, *args, **keywords):
        if not tui.test:
            self._clear_all_widgets()

        supported_types = ["string", "integer", "number", "date", "datetime", "bool"]
        base_collection = tui.schema[MK.Type][0]

        # Named dict page settings
        if base_collection == "named_dict":
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , ^Q-Quit "
            )
            if tui.config is None:
                tui.config = {}
            temp_config = {}
            schema_content = tui.schema[MK.Content]
        # List page settings
        elif base_collection == "list":
            self.add_handlers({"^E": self.edit_list})
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , E-Edit List , ^Q-Quit "
            )

            if tui.config is None:
                tui.config = []
                self.schemainfo = self.add(
                    npyscreen.FixedText,
                    value=" List is empty, add list entry from list menu from Ctrl+E ",
                )
            temp_config = []
            schema_content = range(len(tui.config))

        for s in schema_content:
            # Named dict widget settings
            if base_collection == "named_dict":
                basic_type = tui.schema[MK.Content][s][MK.Type][0]
                name = s + " (" + basic_type + "):"
                not_supported_type = (
                    "Field: '"
                    + s
                    + "' with Type: '"
                    + basic_type
                    + "' is currently not supported in this version of Config "
                    + "Suite TUI and has been rendered as a standard text field."
                )
            # List widget settings
            elif base_collection == "list":
                basic_type = tui.schema[MK.Content][MK.Item][MK.Type][0]
                name = basic_type + " [" + str(s) + "]:"
                not_supported_type = (
                    "Lists with Type: '"
                    + basic_type
                    + "' is currently not supported in this version of Config "
                    + "Suite TUI and has been rendered as a standard text field."
                )

            # Get config value if exists, store in temp config
            try:
                value = tui.config[s]
                if isinstance(tui.config, list):
                    temp_config.append(value)
                elif isinstance(tui.config, dict):
                    temp_config[s] = value
            except (KeyError, TypeError):
                value = 0 if basic_type == "bool" else ""

            # Render widget
            self.render_widget(name, value, basic_type, s)

            # Error message if unsupported type
            if basic_type not in supported_types:
                npyscreen.notify_confirm(
                    not_supported_type,
                    title="Error",
                )
        # Remove all config elements which is not in schema
        tui.config = temp_config

        self.display()
        self.adjust_widgets()

    def render_widget(self, name, value, basic_type, index):
        if basic_type == "bool":
            self.schemawidgets[index] = self.add_widget_intelligent(
                npyscreen.TitleCombo,
                name=name,
                use_two_lines=False,
                begin_entry_at=len(name) + 1,
                values=[False, True],
                value=int(value),
            )
        else:
            self.schemawidgets[index] = self.add_widget_intelligent(
                npyscreen.TitleText,
                name=name,
                use_two_lines=False,
                begin_entry_at=len(name) + 1,
                value=str(value),
            )

    def adjust_widgets(self, *args, **keywords):
        if tui.schema:
            base_collection = tui.schema[MK.Type][0]
            # Set iterable for widgets
            if base_collection == "named_dict":
                widgets = tui.schema[MK.Content]
            elif base_collection == "list":
                widgets = range(len(tui.config))
                basic_type = tui.schema[MK.Content][MK.Item][MK.Type][0]
            # Loop over widgets and update config with values
            for s in widgets:
                if base_collection == "named_dict":
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

    def validate_config(self, *args, **keywords):
        if tui.schema and tui.config:
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
        base_collection = tui.schema[MK.Type][0]
        try:
            if base_collection == "named_dict":
                description = tui.schema[MK.Content][
                    list(tui.schema[MK.Content])[self.editw]
                ][MK.Description]

            elif base_collection == "list":
                description = tui.schema[MK.Content][MK.Item][MK.Description]

        except KeyError:
            description = "This field has no description."

        npyscreen.notify_confirm(
            description, title=self._widgets_by_id[self.editw].name
        )

    def edit_list(self, *args, **keywords):
        self.parentApp.switchForm("EDITLIST")

    def save_config(self, *args, **keywords):
        self.parentApp.switchForm("SAVE")

    def load_config(self, *args, **keywords):
        self.parentApp.switchForm("LOAD")

    def load_schema(self, *args, **keywords):
        self.parentApp.switchForm("SCHEMA")

    def exit_application(self, *args, **keywords):
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()


class EditListForm(CustomEditListPopup):
    def create(self):
        self.name = "Edit List"
        self.add(
            npyscreen.MiniButtonPress,
            name="Add list entry",
            when_pressed_function=self.add_list_entry,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Move selected up",
            when_pressed_function=self.move_list_entry_up,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Move selected down",
            when_pressed_function=self.move_list_entry_down,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Delete selected",
            when_pressed_function=self.delete_list_entry,
        )

    def add_list_entry(self):
        pos = self.parentApp.getForm("MAIN").editw
        tui.config.append("")
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.getForm("MAIN").editw = pos
        self.parentApp.switchForm("MAIN")

    def delete_list_entry(self):
        pos = self.parentApp.getForm("MAIN").editw
        tui.config.pop(pos)
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.getForm("MAIN").editw = pos - 1 if pos > 0 else 0
        self.parentApp.switchForm("MAIN")

    def move_list_entry_up(self):
        pos = self.parentApp.getForm("MAIN").editw
        if pos > 0:
            tui.config[pos], tui.config[pos - 1] = tui.config[pos - 1], tui.config[pos]
            self.parentApp.getForm("MAIN").render_schema()
            self.parentApp.getForm("MAIN").editw = pos - 1
            self.parentApp.switchForm("MAIN")

    def move_list_entry_down(self):
        pos = self.parentApp.getForm("MAIN").editw
        if pos < len(tui.config) - 1:
            tui.config[pos], tui.config[pos + 1] = tui.config[pos + 1], tui.config[pos]
            self.parentApp.getForm("MAIN").render_schema()
            self.parentApp.getForm("MAIN").editw = pos + 1
            self.parentApp.switchForm("MAIN")

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        self.parentApp.switchFormPrevious()


class SaveConfig(CustomSavePopup):
    def create(self):
        self.name = "Save configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        save(tui.config, self.filename.value)
        self.parentApp.switchFormPrevious()


class LoadConfig(CustomLoadPopup):
    def create(self):
        self.name = "Load configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        tui.config = load(self.filename.value)
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.switchForm("MAIN")


class LoadSchema(CustomLoadPopup):
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
        tui.config = None
        self.parentApp.getForm("MAIN").render_schema()
        self.parentApp.switchForm("MAIN")
