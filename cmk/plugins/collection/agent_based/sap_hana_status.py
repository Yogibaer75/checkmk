#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    IgnoreResultsError,
    Result,
    Service,
    State,
    StringTable,
)
from cmk.plugins.lib import sap_hana


def parse_sap_hana_status(string_table: StringTable) -> sap_hana.ParsedSection:
    section: sap_hana.ParsedSection = {}
    for sid_instance, lines in sap_hana.parse_sap_hana(string_table).items():
        for line in lines:
            if line[0].startswith("hdbsql ERROR"):
                item_name = "Status"
                item_data = {
                    "instance": sid_instance,
                    "state_name": "error",
                    "message": line[0],
                }
            elif line[0].lower() == "all started":
                item_name = "Status"
                item_data = {
                    "instance": sid_instance,
                    "state_name": line[1],
                    "message": line[2],
                }
            else:  # Version
                item_name = line[0]
                item_data = {
                    "instance": sid_instance,
                    "version": line[2],
                }
            # always discover "Status", even if we don't have an error now
            section[f"Status {sid_instance}"] = item_data
            section[f"{item_name} {sid_instance}"] = item_data

    return section


agent_section_sap_hana_status = AgentSection(
    name="sap_hana_status",
    parse_function=parse_sap_hana_status,
)


def _check_sap_hana_status_data(data):
    state_name = data["state_name"]
    if state_name.lower() == "ok":
        cur_state = State.OK
    elif state_name.lower() in ["unknown", "error"]:
        cur_state = State.CRIT
    else:
        cur_state = State.WARN
    return cur_state, f"Status: {state_name}, Details: {data['message']}"


def discovery_sap_hana_status(section: sap_hana.ParsedSection) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_sap_hana_status(item: str, section: sap_hana.ParsedSection) -> CheckResult:
    data = section.get(item)
    if not data:
        raise IgnoreResultsError("Login into database failed.")

    if "Status" in item:
        cur_state, infotext = _check_sap_hana_status_data(data)
        yield Result(state=cur_state, summary=infotext)
    else:
        yield Result(state=State.OK, summary="Version: %s" % data["version"])


def cluster_check_sap_hana_status(
    item: str,
    section: Mapping[str, sap_hana.ParsedSection | None],
) -> CheckResult:
    yield Result(state=State.OK, summary="Nodes: %s" % ", ".join(section.keys()))
    for node_section in section.values():
        if node_section is not None and item in node_section:
            yield from check_sap_hana_status(item, node_section)
            return


check_plugin_sap_hana_status = CheckPlugin(
    name="sap_hana_status",
    service_name="SAP HANA %s",
    discovery_function=discovery_sap_hana_status,
    check_function=check_sap_hana_status,
    cluster_check_function=cluster_check_sap_hana_status,
)
