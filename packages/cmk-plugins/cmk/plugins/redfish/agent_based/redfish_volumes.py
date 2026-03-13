#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk.plugins.redfish.lib import (
    parse_redfish_multiple,
    redfish_health_state,
    RedfishAPIData,
)

agent_section_redfish_volumes = AgentSection(
    name="redfish_volumes",
    parse_function=parse_redfish_multiple,
    parsed_section_name="redfish_volumes",
)


def _build_volume_item(data: Mapping[str, Any]) -> tuple[str, str]:
    item1 = data["Id"]
    item2 = item1
    if isinstance(data.get("@odata.id"), str):
        odataid = str(data.get("@odata.id"))
        parts = odataid.split("/")
        try:
            system_id = parts[parts.index("Systems") + 1]
            storage_id = parts[parts.index("Storage") + 1]
            drive_id = parts[parts.index("Volumes") + 1]
            item2 = ":".join([system_id, storage_id, drive_id])
        except ValueError:
            item2 = item1
    return item1, item2


def discovery_redfish_volumes(
    params: Mapping[str, Any], section: RedfishAPIData
) -> DiscoveryResult:
    for _key, data in section.items():
        item1, item2 = _build_volume_item(data)
        if params.get("item", "classic") == "classic":
            yield Service(item=item1)
        yield Service(item=item2)


def check_redfish_volumes(item: str, section: RedfishAPIData) -> CheckResult:
    data = None
    for _key, volume_data in section.items():
        item1, item2 = _build_volume_item(volume_data)
        if item in (item1, item2):
            data = volume_data
            break
    if data is None:
        return
    volume_msg = (
        f"Raid Type: {data.get('RAIDType', None)}, "
        f"Size: {int(data.get('CapacityBytes', 0.0)) / 1024 / 1024 / 1024:0.1f}GB"
    )
    yield Result(state=State(0), summary=volume_msg)

    dev_state, dev_msg = redfish_health_state(data.get("Status", {}))
    status = dev_state
    message = dev_msg

    yield Result(state=State(status), notice=message)


check_plugin_redfish_volumes = CheckPlugin(
    name="redfish_volumes",
    service_name="Volume %s",
    sections=["redfish_volumes"],
    discovery_function=discovery_redfish_volumes,
    discovery_ruleset_name="discovery_redfish_volumes",
    discovery_default_parameters={"item": "classic"},
    check_function=check_redfish_volumes,
)
