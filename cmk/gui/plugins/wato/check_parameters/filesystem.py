#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.exceptions import MKUserError
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.check_parameters.filesystem_utils import vs_filesystem
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    HostRulespec,
    rulespec_registry,
    RulespecGroupCheckParametersDiscovery,
    RulespecGroupCheckParametersStorage,
)
from cmk.gui.valuespec import (
    Checkbox,
    Dictionary,
    DictionaryEntry,
    DropdownChoice,
    ListChoice,
    ListOf,
    ListOfStrings,
    TextInput,
    TextOrRegExp,
)


def _validate_discovery_filesystem_params(value, varprefix):
    mountpoint_for_block_devices = value.get(
        "mountpoint_for_block_devices", "volume_name_as_mountpoint"
    )
    item_appearance = value.get("item_appearance", "mountpoint")
    grouping_behaviour = value.get("grouping_behaviour", "mountpoint")

    if item_appearance == "mountpoint" and grouping_behaviour != "mountpoint":
        raise MKUserError(
            varprefix,
            _(
                "You cannot use mountpoint as item and grouping based on"
                " volume name and mountpoint."
            ),
        )

    parameters = [
        p for p in [mountpoint_for_block_devices, item_appearance, grouping_behaviour] if p
    ]
    if any("volume_name" in p for p in parameters) and any("uuid" in p for p in parameters):
        raise MKUserError(
            varprefix,
            _(
                "You cannot mix volume name and UUID in 'Mountpoint for block devices',"
                " 'Item appearance' or 'Grouping'"
            ),
        )


def _valuespec_inventory_df_rules() -> Dictionary:
    return Dictionary(
        title=_("Filesystem discovery"),
        elements=[
            (
                "mountpoint_for_block_devices",
                DropdownChoice(
                    title=_("Mountpoint for block devices (brtfs)"),
                    choices=[
                        ("volume_name_as_mountpoint", _("Use volume name as mountpoint")),
                        ("uuid_as_mountpoint", _("Use UUID as mountpoint")),
                    ],
                    default_value="volume_name_as_mountpoint",
                ),
            ),
            (
                "item_appearance",
                DropdownChoice(
                    title=_("Item appearance"),
                    choices=[
                        ("mountpoint", _("Use mountpoint")),
                        ("volume_name_and_mountpoint", _("Use volume name and mountpoint")),
                        ("uuid_and_mountpoint", _("Use UUID and mountpoint")),
                    ],
                    default_value="mountpoint",
                ),
            ),
            (
                "grouping_behaviour",
                DropdownChoice(
                    title=_("Grouping applies to"),
                    choices=[
                        ("mountpoint", _("mountpoint only")),
                        ("volume_name_and_mountpoint", _("volume name and mountpoint")),
                        ("uuid_and_mountpoint", _("UUID and mountpoint")),
                    ],
                    help=_(
                        "Specifies how the <a href='wato.py?mode=edit_ruleset&varname=filesystem_groups'>Filesystem grouping patterns</a>"
                        " feature processes this filesystem."
                    ),
                    default_value="mountpoint",
                ),
            ),
            (
                "ignore_fs_types",
                ListChoice(
                    title=_("Filesystem types to ignore"),
                    choices=[
                        ("tmpfs", "tmpfs"),
                        ("nfs", "nfs"),
                        ("smbfs", "smbfs"),
                        ("cifs", "cifs"),
                        ("iso9660", "iso9660"),
                    ],
                    default_value=["tmpfs", "nfs", "smbfs", "cifs", "iso9660"],
                ),
            ),
            (
                "never_ignore_mountpoints",
                ListOf(
                    valuespec=TextOrRegExp(),
                    title=_("Mountpoints to never ignore"),
                    help=_(
                        "Regardless of filesystem type, these mountpoints will always be discovered."
                        "Regular expressions are supported."
                    ),
                ),
            ),
            _list_of_filesystem_groups_specs_elements(),
        ],
        validate=_validate_discovery_filesystem_params,
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="dict",
        name="inventory_df_rules",
        valuespec=_valuespec_inventory_df_rules,
    )
)

FILESYSTEM_GROUPS_WRAPPER_KEY = "groups"


def _valuespec_filesystem_groups() -> Dictionary:
    return Dictionary(
        title=_("Filesystem grouping patterns"),
        optional_keys=False,
        elements=[_list_of_filesystem_groups_specs_elements()],
    )


def _list_of_filesystem_groups_specs_elements() -> DictionaryEntry:
    return FILESYSTEM_GROUPS_WRAPPER_KEY, ListOf(
        valuespec=Dictionary(
            optional_keys=False,
            elements=[
                (
                    "group_name",
                    TextInput(
                        title=_("Group name"),
                        size=49,
                    ),
                ),
                (
                    "patterns_include",
                    ListOfStrings(
                        title=_("Inclusion patterns"),
                        orientation="horizontal",
                        size=49,
                        help=_(
                            "You can specify one or several globbing patterns containing "
                            "<tt>*</tt>, <tt>?</tt> and <tt>[...]</tt>, for example "
                            "<tt>/spool/tmpspace*</tt>. The filesystems matching the "
                            "patterns will be grouped together and monitored as one big "
                            "filesystem in a single service. Note that specifically for "
                            "the check <tt>df</tt>, the pattern matches either the mount "
                            "point or the combination of volume and mount point, "
                            "depending on the configuration in "
                            "<a href='wato.py?mode=edit_ruleset&varname=inventory_df_rules'>"
                            "Filesystem discovery</a>."
                        ),
                    ),
                ),
                (
                    "patterns_exclude",
                    ListOfStrings(
                        title=_("Exclusion patterns"),
                        orientation="horizontal",
                        size=49,
                        help=_(
                            "You can specify one or several globbing patterns containing "
                            "<tt>*</tt>, <tt>?</tt> and <tt>[...]</tt>, for example "
                            "<tt>/spool/tmpspace*</tt>. The filesystems matching the "
                            "patterns will excluded from grouping and monitored "
                            "individually. Note that specifically for the check "
                            "<tt>df</tt>, the pattern matches either the mount point or "
                            "the combination of volume and mount point, depending on the "
                            "configuration in "
                            "<a href='wato.py?mode=edit_ruleset&varname=inventory_df_rules'>"
                            "Filesystem discovery</a>."
                        ),
                    ),
                ),
            ],
        ),
        add_label=_("Add group"),
        title=_("Filesystem grouping patterns"),
        help=_(
            "By default, the file system checks (<tt>df</tt>, <tt>hr_fs</tt> and others) will "
            "create a single service for each file system. By defining grouping patterns, you "
            "can handle groups of file systems like one file system. For each group, you can "
            "define one or several include and exclude patterns. The file systems matching one "
            "of the include patterns will be monitored like one big file system in a single "
            "service. The file systems matching one of the exclude patterns will be excluded "
            "from the group and monitored individually."
        ),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="all",
        name="filesystem_groups",
        valuespec=_valuespec_filesystem_groups,
    )
)


def _item_spec_filesystem():
    return TextInput(
        title=_("Mount point"),
        help=_(
            "For Linux/UNIX systems, specify the mount point, for Windows systems "
            "the drive letter uppercase followed by a colon and a slash, e.g. <tt>C:/</tt>"
        ),
        allow_empty=False,
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="filesystem",
        group=RulespecGroupCheckParametersStorage,
        item_spec=_item_spec_filesystem,
        match_type="dict",
        parameter_valuespec=vs_filesystem,
        title=lambda: _("Filesystems (used space and growth)"),
    )
)


def _discovery_valuespec_qtree_quota() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "exclude_volume",
                Checkbox(
                    title=_("Exclude volume from service name"),
                    help=_(
                        "The service name of qtree services is composed of the "
                        "quota, quota-users and the volume name by default. Check this box "
                        "if you would like to use the quota and quota-users combination as the "
                        "service name on its own. "
                        "Please be advised that this may lead to a service name that is "
                        "not unique, resulting in some services, which are not shown!"
                    ),
                ),
            ),
        ],
        title=_("NetApp Qtree discovery"),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersDiscovery,
        match_type="list",
        name="discovery_qtree",
        valuespec=_discovery_valuespec_qtree_quota,
    )
)
