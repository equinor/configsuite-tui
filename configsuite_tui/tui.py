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
    CustomNPSAppManaged,
    CustomCollectionButton,
)
from configsuite_tui import hookspecs, test_hook_named_dict, test_hook_list


def tui(**kwargs):
    # Variables to hold information and states of the TUI
    tui.schema = {}
    tui.schema_name = ""
    tui.schema_list = {}
    tui.config = None
    tui.valid = False
    # Indexes
    tui.schema_index = []
    tui.config_index = []
    tui.page_schema = None
    tui.page_config = None

    pm = get_plugin_manager()
    for s in pm.hook.configsuite_tui_schema():
        tui.schema_list.update(s)

    App = Interface()
    if "test" in kwargs and kwargs["test"]:
        tui.test = True
        tui.schema = tui.schema_list["test"]
        tui.schema_name = list(tui.schema_list.keys())[0]
        App.run(fork=False)
    elif "test_fork" in kwargs and kwargs["test_fork"]:
        tui.test = False
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


class Interface(CustomNPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", SchemaForm)
        self.addForm("SAVE", SaveConfig)
        self.addForm("LOAD", LoadConfig)
        self.addForm("SCHEMA", LoadSchema)
        self.addForm("EDITLISTMENU", EditListForm)

        self.addForm("EDIT_LEVEL_ONE", EditCollectionForm)
        self.addForm("EDIT_LEVEL_TWO", EditCollectionForm)
        self.addForm("EDIT_LEVEL_THREE", EditCollectionForm)


class SchemaForm(CustomFormMultiPage):
    def create(self):
        self.name = "Config Suite TUI"
        self.footer = self.footer = " ^A-Load Schema , ^Q-Quit "
        self.schemawidgets = {}
        self.page_collection = None
        self.supported_types = [
            "string",
            "integer",
            "number",
            "date",
            "datetime",
            "bool",
            "list",
            "named_dict",
        ]

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

    def beforeEditing(self):
        # Setting form specific settings for config and schema
        tui.page_schema = tui.schema
        tui.page_config = tui.config

        # Add widgets from schema
        if tui.schema:
            self.render_schema()

    def render_schema(self, *args, **keywords):
        if not tui.test:
            self._clear_all_widgets()

        self.page_collection = tui.page_schema[MK.Type][0]

        # Named dict page settings
        if self.page_collection == "named_dict":
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , ^Q-Quit "
            )
            if tui.page_config is None:
                tui.page_config = {}
            schema_content = tui.page_schema[MK.Content]

        # List page settings
        elif self.page_collection == "list":
            self.add_handlers({"^E": self.edit_list_menu})
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , E-Edit List , ^Q-Quit "
            )

            if tui.page_config is None:
                tui.page_config = []
                self.schemainfo = self.add(
                    npyscreen.FixedText,
                    value=" List is empty, add list entry from list"
                    + " menu using the keybind Ctrl+E ",
                )
            elif tui.page_config == []:
                self.schemainfo = self.add(
                    npyscreen.FixedText,
                    value=" List is empty, add list entry from list "
                    + " menu using the keybind Ctrl+E ",
                )

            schema_content = range(len(tui.page_config))

        # Loop over selected schema content
        for s in schema_content:
            # Named dict widget settings
            if self.page_collection == "named_dict":
                mk_type = tui.page_schema[MK.Content][s][MK.Type][0]
                name = s + " (" + mk_type + "):"
                not_supported_type = (
                    "Field: '"
                    + s
                    + "' with Type: '"
                    + mk_type
                    + "' is currently not supported in this version of Config "
                    + "Suite TUI and has been rendered as a standard text field."
                )
            # List widget settings
            elif self.page_collection == "list":
                mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]
                name = mk_type + " [" + str(s) + "]:"
                not_supported_type = (
                    "Lists with Type: '"
                    + mk_type
                    + "' is currently not supported in this version of Config "
                    + "Suite TUI and has been rendered as a standard text field."
                )

            # Get config value if exists
            try:
                value = tui.page_config[s]
            except (KeyError, TypeError):
                value = 0 if mk_type == "bool" else ""

            # Render widget
            self.render_widget(name, value, mk_type, s)

            # Error message if unsupported type
            if mk_type not in self.supported_types:
                npyscreen.notify_confirm(
                    not_supported_type,
                    title="Error",
                )

        self.display()
        self.adjust_widgets()

    def render_widget(self, name, value, mk_type, index):
        if mk_type == "bool":
            self.schemawidgets[index] = self.add_widget_intelligent(
                npyscreen.TitleCombo,
                name=name,
                use_two_lines=False,
                begin_entry_at=len(name) + 1,
                values=[False, True],
                value=int(value),
            )
        elif mk_type in ["list", "named_dict"]:
            self.schemawidgets[index] = self.add_widget_intelligent(
                CustomCollectionButton,
                name=name + " {...}",
                when_pressed_function=self.edit_collection,
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
        if tui.page_schema:
            # Set iterable for widgets
            if self.page_collection == "named_dict":
                widgets = tui.page_schema[MK.Content]
            elif self.page_collection == "list":
                widgets = range(len(tui.page_config))
                mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]
            # Loop over widgets and update config with values
            for s in widgets:
                if self.page_collection == "named_dict":
                    mk_type = tui.page_schema[MK.Content][s][MK.Type][0]
                value = self.schemawidgets[s].value
                if mk_type in ["integer", "number"]:
                    tui.page_config[s] = fast_real(value)
                elif mk_type == "bool" and isinstance(value, int):
                    tui.page_config[s] = bool(value)
                elif mk_type == "date":
                    try:
                        tui.page_config[s] = isoparse(value).date()
                    except ValueError:
                        tui.page_config[s] = None
                elif mk_type == "datetime":
                    try:
                        tui.page_config[s] = isoparse(value)
                    except ValueError:
                        tui.page_config[s] = None
                elif mk_type in ["list", "named_dict"]:
                    pass
                else:
                    tui.page_config[s] = value

            self.validate_config()

    def validate_config(self, *args, **keywords):
        tui.config = tui.page_config

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
        try:
            if self.page_collection == "named_dict":
                description = tui.page_schema[MK.Content][
                    list(tui.page_schema[MK.Content])[self.editw]
                ][MK.Description]

            elif self.page_collection == "list":
                description = tui.page_schema[MK.Content][MK.Item][MK.Description]

        except KeyError:
            description = "This field has no description."

        npyscreen.notify_confirm(
            description, title=self._widgets_by_id[self.editw].name
        )

    def edit_collection(self, *args, **keywords):
        if self.page_collection == "list":
            tui.config_index.append(self.editw)
            tui.schema_index.append((MK.Content, MK.Item))
        if self.page_collection == "named_dict":
            tui.config_index.append(list(tui.page_schema[MK.Content])[self.editw])
            tui.schema_index.append(
                (
                    MK.Content,
                    list(tui.page_schema[MK.Content])[self.editw],
                )
            )
        tui.page_config = None
        tui.page_schema = None
        self.edit_popup()

    def edit_popup(self, *args, **keywords):
        if len(tui.config_index) == 1:
            self.parentApp.switchForm("EDIT_LEVEL_ONE")
        elif len(tui.config_index) == 2:
            self.parentApp.switchForm("EDIT_LEVEL_TWO")
        elif len(tui.config_index) == 3:
            self.parentApp.switchForm("EDIT_LEVEL_THREE")
        else:
            npyscreen.notify_confirm(
                "Config Suite TUI currently only supports three levels of nested lists",
                title="Error",
            )

    def edit_list_menu(self, *args, **keywords):
        self.parentApp.switchForm("EDITLISTMENU")

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

    def beforeEditing(self):
        self.parentApp.removeCurrentFromHistory()
        self.previous_form = self.parentApp.getHistory()[-1]

    def add_list_entry(self):
        pos = self.parentApp.getForm(self.previous_form).editw
        collection = self.parentApp.getForm(self.previous_form).page_collection
        if collection == "list":
            mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]
        elif collection == "named_dict":
            mk_type = tui.page_schema[MK.Content][pos][MK.Type][0]

        if mk_type == "bool":
            tui.page_config.append(0)
        elif mk_type == "list":
            tui.page_config.append([])
        elif mk_type == "named_dict":
            tui.page_config.append({})
        else:
            tui.page_config.append("")
        self.parentApp.switchForm(self.previous_form)

    def delete_list_entry(self):
        pos = self.parentApp.getForm(self.previous_form).editw
        tui.page_config.pop(pos)
        self.parentApp.getForm(self.previous_form).render_schema()
        self.parentApp.getForm(self.previous_form).editw = pos - 1 if pos > 0 else 0
        self.parentApp.switchForm(self.previous_form)

    def move_list_entry_up(self):
        pos = self.parentApp.getForm(self.previous_form).editw
        if pos > 0:
            tui.page_config[pos], tui.page_config[pos - 1] = (
                tui.page_config[pos - 1],
                tui.page_config[pos],
            )
            self.parentApp.getForm(self.previous_form).render_schema()
            self.parentApp.getForm(self.previous_form).editw = pos - 1
            self.parentApp.switchForm(self.previous_form)

    def move_list_entry_down(self):
        pos = self.parentApp.getForm(self.previous_form).editw
        if pos < len(tui.page_config) - 1:
            tui.page_config[pos], tui.page_config[pos + 1] = (
                tui.page_config[pos + 1],
                tui.page_config[pos],
            )
            self.parentApp.getForm(self.previous_form).render_schema()
            self.parentApp.getForm(self.previous_form).editw = pos + 1
            self.parentApp.switchForm(self.previous_form)

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
        tui.page_config = None
        tui.page_schema = None
        self.parentApp.switchForm("MAIN")


class EditCollectionForm(SchemaForm):
    def __init__(self, *args, **keywords):
        super(EditCollectionForm, self).__init__(*args, **keywords)
        self.action = True

    def beforeEditing(self):
        # Settings for config and schema
        if len(tui.schema_index) == 1:
            # Set config index. If not exists: create it
            i = tui.config_index[0]
            try:
                tui.page_config = tui.config[i]
            except KeyError:
                tui.config[i] = None
                tui.page_config = tui.config[i]

            tui.page_schema = tui.schema
            for i in tui.schema_index[0]:
                tui.page_schema = tui.page_schema[i]

        if len(tui.schema_index) == 2:
            i, j = tui.config_index
            try:
                tui.page_config = tui.config[i][j]
            except KeyError:
                tui.config[i][j] = None
                tui.page_config = tui.config[i][j]

            tui.page_schema = tui.schema
            for j in tui.schema_index[0] + tui.schema_index[1]:
                tui.page_schema = tui.page_schema[j]

        if len(tui.schema_index) == 3:
            i, j, k = tui.config_index
            try:
                tui.page_config = tui.config[i][j][k]
            except KeyError:
                tui.config[i][j][k] = None
                tui.page_config = tui.config[i][j][k]

            tui.page_schema = tui.schema
            for j in tui.schema_index[0] + tui.schema_index[1] + tui.schema_index[2]:
                tui.page_schema = tui.page_schema[j]

        # Add widgets from schema
        if tui.schema:
            self.render_schema()

    def validate_config(self, *args, **keywords):
        if len(tui.schema_index) == 1:
            tui.config[tui.config_index[0]] = tui.page_config

        if len(tui.schema_index) == 2:
            i, j = tui.config_index
            tui.config[i][j] = tui.page_config

        if len(tui.schema_index) == 3:
            i, j, k = tui.config_index
            tui.config[i][j][k] = tui.page_config

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

    def on_ok(self):
        tui.config_index.pop()
        tui.schema_index.pop()
        self.parentApp.switchFormPrevious()
