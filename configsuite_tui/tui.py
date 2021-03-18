from dateutil.parser import isoparse
import npyscreen
import pluggy
from fastnumbers import fast_real
from configsuite import MetaKeys as MK
import yaml
from configsuite_tui.config_tools import save, load, validate, readable
from configsuite_tui.custom_widgets import (
    CustomFormMultiPage,
    CustomEditMenuPopup,
    CustomLoadPopup,
    CustomSavePopup,
    CustomNPSAppManaged,
    CustomCollectionButton,
    CustomAddDictEntryPopup,
    custom_notify_wait,
)
from configsuite_tui import (
    hookspecs,
    test_hook_named_dict,
    test_hook_list,
    test_hook_dict,
)


def tui(config="", schema="", test=False, test_fork=False):
    # Variables to hold information and states of the TUI
    tui.schema = {}
    tui.schema_name = ""
    tui.schema_list = {}
    tui.config = None
    tui.config_file = ""
    tui.valid = False
    # Variables to hold partial schema and config for sub pages
    tui.page_schema = None
    tui.page_config = None
    tui.page_errors = {}
    # Indexes
    tui.schema_index = []
    tui.config_index = []
    tui.position = None

    # Get list of registered schemas
    pm = get_plugin_manager()
    for s in pm.hook.configsuite_tui_schema():
        tui.schema_list.update(s)

    # Process arguments
    if schema:
        tui.schema = tui.schema_list[schema]
        tui.schema_name = schema
    if config:
        tui.config, tmp_schema = load(config)
        if not tui.schema and tmp_schema:
            tui.schema = tui.schema_list[tmp_schema]
            tui.schema_name = tmp_schema

    # Run application
    App = Interface()
    if test:
        tui.test = True
        App.run(fork=False)
    elif test_fork:
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
    # Temporary hooks
    pm.register(test_hook_named_dict)
    pm.register(test_hook_list)
    pm.register(test_hook_dict)
    return pm


class Interface(CustomNPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", SchemaForm)
        self.addForm("SAVE", SaveConfig)
        self.addForm("LOAD", LoadConfig)
        self.addForm("SCHEMA", LoadSchema)
        self.addFormClass("EDITMENU", EditMenu)
        self.addFormClass("ADD_DICT_ENTRY", AddDictEntryForm)
        self.addForm("EDIT_LEVEL_ONE", EditCollectionForm)
        self.addForm("EDIT_LEVEL_TWO", EditCollectionForm)
        self.addForm("EDIT_LEVEL_THREE", EditCollectionForm)


class SchemaForm(CustomFormMultiPage):
    def create(self):
        # Add application wide variables
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
            "dict",
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
        # Setting page specific settings for config and schema
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
            self.add_handlers({"^E": self.edit_menu})
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , ^E-Edit List , ^Q-Quit "
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

        # Dict page settings
        elif self.page_collection == "dict":
            self.add_handlers({"^E": self.edit_menu})
            self.footer = (
                " ^A-Load Schema , ^S-Save Config , "
                + "^L-Load Config , ^D-Show Description , ^E-Edit Dict , ^Q-Quit "
            )
            if tui.page_config is None:
                tui.page_config = {}
                self.schemainfo = self.add(
                    npyscreen.FixedText,
                    value=" Dict is empty, add dict entry from dict"
                    + " menu using the keybind Ctrl+E ",
                )
            elif tui.page_config == {}:
                self.schemainfo = self.add(
                    npyscreen.FixedText,
                    value=" Dict is empty, add dict entry from dict"
                    + " menu using the keybind Ctrl+E ",
                )
            schema_content = list(tui.page_config)

        # Loop over selected schema content
        for s in schema_content:
            # Named dict widget settings
            if self.page_collection == "named_dict":
                mk_type = tui.page_schema[MK.Content][s][MK.Type][0]
                name = str(s) + " (" + mk_type + "):"

            # List widget settings
            elif self.page_collection == "list":
                mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]
                name = mk_type + " [" + str(s) + "]:"

            # Dict widget settings
            elif self.page_collection == "dict":
                mk_type = tui.page_schema[MK.Content][MK.Value][MK.Type][0]
                name = str(s) + " (" + mk_type + "):"

            not_supported_type = (
                "Field: '"
                + str(s)
                + "' with Type: '"
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
        elif mk_type in ["dict", "named_dict"]:
            self.schemawidgets[index] = self.add_widget_intelligent(
                CustomCollectionButton,
                name=name + " {...}",
                when_pressed_function=self.edit_collection,
            )
        elif mk_type == "list":
            self.schemawidgets[index] = self.add_widget_intelligent(
                CustomCollectionButton,
                name=name + " [...]",
                when_pressed_function=self.edit_collection,
            )
        else:
            self.schemawidgets[index] = self.add_widget_intelligent(
                npyscreen.TitleText,
                name=name,
                use_two_lines=False,
                begin_entry_at=len(name) + 1,
                value=str(value) if value else "",
            )

    def adjust_widgets(self, *args, **keywords):
        if tui.page_schema:
            # Set iterable for widgets
            if self.page_collection == "named_dict":
                widgets = tui.page_schema[MK.Content]
            elif self.page_collection == "list":
                widgets = range(len(tui.page_config))
                mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]
            elif self.page_collection == "dict":
                widgets = list(tui.page_config)
                mk_type = tui.page_schema[MK.Content][MK.Value][MK.Type][0]

            # Loop over widgets
            for w in widgets:
                if self.page_collection == "named_dict":
                    mk_type = tui.page_schema[MK.Content][w][MK.Type][0]

                value = self.schemawidgets[w].value

                # Update config with values
                if mk_type in ["integer", "number"]:
                    tui.page_config[w] = fast_real(value)
                elif mk_type == "bool" and isinstance(value, int):
                    tui.page_config[w] = bool(value)
                elif mk_type == "date":
                    try:
                        tui.page_config[w] = isoparse(value).date()
                    except ValueError:
                        tui.page_config[w] = None
                elif mk_type == "datetime":
                    try:
                        tui.page_config[w] = isoparse(value)
                    except ValueError:
                        tui.page_config[w] = None
                elif mk_type in ["list", "dict", "named_dict"]:
                    pass
                elif not value:
                    tui.page_config[w] = None
                else:
                    tui.page_config[w] = value

                # Change color of label if error
                if w in list(tui.page_errors.keys()):
                    self.schemawidgets[w].labelColor = "DANGER"
                else:
                    self.schemawidgets[w].labelColor = "LABEL"

            self.validate_config()

    def validate_config(self, *args, **keywords):
        # Transfer this page's config to main config
        tui.config = tui.page_config

        if tui.schema and tui.config:
            # Validate and get errors
            tui.valid, tui.page_errors = validate(
                tui.config, tui.schema, tui.config_index
            )
            # Change color and name of TUI
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
        # Get description
        try:
            if self.page_collection == "named_dict":
                description = tui.page_schema[MK.Content][
                    list(tui.page_schema[MK.Content])[self.editw]
                ][MK.Description]
                if list(tui.page_schema[MK.Content])[self.editw] in tui.page_errors:
                    error = tui.page_errors[
                        list(tui.page_schema[MK.Content])[self.editw]
                    ]
                else:
                    error = "No errors"
            elif self.page_collection == "list":
                description = tui.page_schema[MK.Content][MK.Item][MK.Description]
                if self.editw in tui.page_errors:
                    error = tui.page_errors[self.editw]
                else:
                    error = "No errors"
            elif self.page_collection == "dict":
                description = tui.page_schema[MK.Content][MK.Description]
                if list(tui.page_schema[MK.Content])[self.editw] in tui.page_errors:
                    error = tui.page_errors[
                        list(tui.page_schema[MK.Content])[self.editw]
                    ]
                else:
                    error = "No errors"
        except KeyError:
            description = "This field has no description."

        # Get errors
        if self.page_collection in ["named_dict", "dict"]:
            if list(tui.page_schema[MK.Content])[self.editw] in tui.page_errors:
                error = tui.page_errors[list(tui.page_schema[MK.Content])[self.editw]]
            else:
                error = "No errors"
        elif self.page_collection == "list":
            description = tui.page_schema[MK.Content][MK.Item][MK.Description]
            if self.editw in tui.page_errors:
                error = tui.page_errors[self.editw]
            else:
                error = "No errors"

        description_string = "Description: " + description + "\nError: " + error
        npyscreen.notify_confirm(
            description_string, title=self._widgets_by_id[self.editw].name
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

    def edit_menu(self, *args, **keywords):
        tui.position = self.editw
        self.parentApp.switchForm("EDITMENU")

    def save_config(self, *args, **keywords):
        self.parentApp.switchForm("SAVE")

    def load_config(self, *args, **keywords):
        self.parentApp.switchForm("LOAD")

    def load_schema(self, *args, **keywords):
        self.parentApp.switchForm("SCHEMA")

    def exit_application(self, *args, **keywords):
        message = "Are you sure you want to exit?\nAll unsaved progress will be lost"
        if npyscreen.notify_yes_no(message, title="Exit application"):
            self.parentApp.setNextForm(None)
            self.editing = False
            self.parentApp.switchFormNow()


class EditMenu(CustomEditMenuPopup):
    def create(self):
        self.name = "Edit Collection"
        self.add(
            npyscreen.MiniButtonPress,
            name="Add entry",
            when_pressed_function=self.add_entry,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Move selected up",
            when_pressed_function=self.move_entry_up,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Move selected down",
            when_pressed_function=self.move_entry_down,
        )
        self.add(
            npyscreen.MiniButtonPress,
            name="Delete selected",
            when_pressed_function=self.delete_entry,
        )

    def beforeEditing(self):
        self.parentApp.removeCurrentFromHistory()
        self.previous_form = self.parentApp.getHistory()[-1]
        self.collection = self.parentApp.getForm(self.previous_form).page_collection
        self.pos = tui.position
        self.temp_dict = {}
        self.indexes = list(tui.page_config)

    def add_entry(self):
        if self.collection == "list":
            mk_type = tui.page_schema[MK.Content][MK.Item][MK.Type][0]

            if mk_type == "bool":
                tui.page_config.append(0)
            elif mk_type == "list":
                tui.page_config.append([])
            elif mk_type in ["dict", "named_dict"]:
                tui.page_config.append({})
            else:
                tui.page_config.append("")
            self.parentApp.switchForm(self.previous_form)

        elif self.collection == "dict":
            self.parentApp.switchForm("ADD_DICT_ENTRY")

    def delete_entry(self):
        if len(tui.page_config) > 0 and self.pos < len(tui.page_config):
            if self.collection == "list":
                tui.page_config.pop(self.pos)
            elif self.collection == "dict":
                self.indexes.pop(self.pos)
                for i in self.indexes:
                    self.temp_dict[i] = tui.page_config[i]
                tui.page_config = self.temp_dict

            self.parentApp.getForm(self.previous_form).validate_config()
            self.parentApp.switchForm(self.previous_form)

    def move_entry_up(self):
        if self.pos > 0 and self.pos < len(tui.page_config):
            if self.collection == "list":
                tui.page_config[self.pos], tui.page_config[self.pos - 1] = (
                    tui.page_config[self.pos - 1],
                    tui.page_config[self.pos],
                )
            elif self.collection == "dict":
                self.indexes[self.pos], self.indexes[self.pos - 1] = (
                    self.indexes[self.pos - 1],
                    self.indexes[self.pos],
                )
                for i in self.indexes:
                    self.temp_dict[i] = tui.page_config[i]
                tui.page_config = self.temp_dict

            self.parentApp.getForm(self.previous_form).validate_config()
            self.parentApp.switchForm(self.previous_form)

    def move_entry_down(self):
        if self.pos < len(tui.page_config) - 1 and self.pos < len(tui.page_config):
            if self.collection == "list":
                tui.page_config[self.pos], tui.page_config[self.pos + 1] = (
                    tui.page_config[self.pos + 1],
                    tui.page_config[self.pos],
                )
            elif self.collection == "dict":
                self.indexes[self.pos], self.indexes[self.pos + 1] = (
                    self.indexes[self.pos + 1],
                    self.indexes[self.pos],
                )
                for i in self.indexes:
                    self.temp_dict[i] = tui.page_config[i]
                tui.page_config = self.temp_dict

            self.parentApp.getForm(self.previous_form).validate_config()
            self.parentApp.switchForm(self.previous_form)

    def on_ok(self):
        self.parentApp.switchFormPrevious()


class AddDictEntryForm(CustomAddDictEntryPopup):
    def create(self):
        self.name = "Add dictionary key"

    def beforeEditing(self):
        self.key_type = tui.page_schema[MK.Content][MK.Key][MK.Type][0]
        name = "Dict Key (" + self.key_type + "):"
        self.dict_key = self.add(
            npyscreen.TitleText,
            name=name,
            use_two_lines=False,
            begin_entry_at=len(name) + 1,
        )

    def on_ok(self):
        if self.dict_key.value and self.dict_key.value not in tui.page_config:
            tui.page_config[self.dict_key.value] = ""
        elif self.dict_key.value in tui.page_config:
            npyscreen.notify_confirm(
                self.dict_key.value + " already exists.",
                title="Error",
            )
        else:
            npyscreen.notify_confirm(
                self.dict_key.value
                + " is not a valid key. Please enter a unique key of type "
                + self.key_type
                + ".",
                title="Error",
            )
        self.parentApp.switchFormPrevious()


class SaveConfig(CustomSavePopup):
    def create(self):
        self.name = "Save configuration file"
        self.footer = ""
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")

    def beforeEditing(self):
        if tui.config_file:
            self.filename.value = tui.config_file
            self.name = "Save configuration file"
            self.add_handlers({"^S": self.on_ok})
            self.footer = " ^S-Quick Save "

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self, *args, **keywords):
        if self.filename.value:
            save(tui.config, self.filename.value, tui.schema_name)
            tui.config_file = self.filename.value
            custom_notify_wait(
                title="Saved", message="Configuration saved to: " + tui.config_file
            )
            self.parentApp.switchFormPrevious()


class LoadConfig(CustomLoadPopup):
    def create(self):
        self.name = "Load configuration file"
        self.filename = self.add(npyscreen.TitleFilenameCombo, name="Filename")
        self.error_message = ""

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        try:
            tui.config = load(self.filename.value)[0]
            tui.config_file = self.filename.value
        except yaml.YAMLError:
            self.error_message = (
                "The loaded configuration is corrupt. "
                + "Please check that the configuration is created "
                + "for the loaded schema and formatted properly."
            )

        if not readable(tui.config, tui.schema):
            self.error_message = (
                "The loaded configuration is invalid. "
                + "Please check that the configuration is created "
                + "for the loaded schema and formatted properly.",
            )
            tui.config = None

        if self.error_message:
            npyscreen.notify_confirm(
                self.error_message,
                title="Error",
            )

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
        # Setting page specific settings for config
        if len(tui.schema_index) == 1:
            # Set config index. If not exists: create it
            i = tui.config_index[0]
            try:
                tui.page_config = tui.config[i]
            except KeyError:
                tui.page_config = None
        elif len(tui.schema_index) == 2:
            i, j = tui.config_index
            try:
                tui.page_config = tui.config[i][j]
            except KeyError:
                tui.page_config = None
        elif len(tui.schema_index) == 3:
            i, j, k = tui.config_index
            try:
                tui.page_config = tui.config[i][j][k]
            except KeyError:
                tui.page_config = None

        # Setting page specific settings for schema
        tui.page_schema = tui.schema
        schema_indexes = []
        for j in tui.schema_index:
            schema_indexes.extend(list(j))
        for k in schema_indexes:
            tui.page_schema = tui.page_schema[k]

        # Add widgets from schema
        if tui.schema:
            self.render_schema()

    def validate_config(self, *args, **keywords):
        # Transfer this page's config to main config
        if len(tui.schema_index) == 1:
            tui.config[tui.config_index[0]] = tui.page_config
        elif len(tui.schema_index) == 2:
            i, j = tui.config_index
            tui.config[i][j] = tui.page_config
        elif len(tui.schema_index) == 3:
            i, j, k = tui.config_index
            tui.config[i][j][k] = tui.page_config

        if tui.schema and tui.config:
            tui.valid, tui.page_errors = validate(
                tui.config, tui.schema, tui.config_index
            )
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
