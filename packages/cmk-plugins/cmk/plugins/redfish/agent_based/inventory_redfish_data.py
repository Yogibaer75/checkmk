#!/usr/bin/env python3
"""Redfish HW/SW inventory plugin"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from collections.abc import Mapping, Sequence
from typing import Any

from cmk.agent_based.v2 import InventoryPlugin, InventoryResult, TableRow
from cmk.plugins.redfish.lib import RedfishAPIData

IDSET = set[tuple[str, str, str, str, str, str]]


def _extract_odata_ids(
    data: None | RedfishAPIData | Sequence[Mapping[str, Any]], ids_set: IDSET
) -> IDSET:
    if isinstance(data, Mapping):
        for key, value in data.items():
            # if key '@odata.id' and value is a string, extract the OData ID value
            if key == "@odata.id" and isinstance(value, str):
                key_name = data.get("Name")
                serial_number = data.get("SerialNumber", "nothing set")
                part_number = data.get("PartNumber", "nothing set")
                manufacturer = data.get("Manufacturer", "nothing set")
                model = data.get("Model", "nothing set")
                # if 'Oem' in data, skip this entry and go deeper
                if "Oem" in value:
                    continue
                if key_name:
                    # add name is not None add to set
                    ids_set.add(
                        (
                            value,
                            key_name,
                            serial_number,
                            part_number,
                            manufacturer,
                            model,
                        )
                    )
            # else recursively call for nested mappings or sequences
            else:
                ids_set = _extract_odata_ids(value, ids_set)
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        for item in data:
            # Rekursiv für jedes Element in der Liste/Tupel aufrufen
            ids_set = _extract_odata_ids(item, ids_set)

    return ids_set


def inventory_redfish_data(
    section_redfish_storage: None | RedfishAPIData,
    section_redfish_processors: None | RedfishAPIData,
    section_redfish_drives: None | RedfishAPIData,
    section_redfish_psu: None | RedfishAPIData,
    section_redfish_memory: None | RedfishAPIData,
    section_redfish_power: None | RedfishAPIData,
    section_redfish_thermal: None | RedfishAPIData,
    section_redfish_networkadapters: None | RedfishAPIData,
) -> InventoryResult:
    result_path = ["redfish"]

    odata_ids_set: IDSET = set()
    odata_ids_set = _extract_odata_ids(section_redfish_processors, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_storage, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_drives, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_psu, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_memory, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_power, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_thermal, odata_ids_set)
    odata_ids_set = _extract_odata_ids(section_redfish_networkadapters, odata_ids_set)

    for path, name, serial, part_number, manufacturer, model in odata_ids_set:
        if serial == "nothing set":
            continue
        if path.startswith("/redfish/"):
            segments = (
                path.replace("#", "")
                .replace(":", "-")
                .replace(".", "_")
                .replace("'", "")
                .replace("(", "_")
                .replace(")", "_")
                .replace("%", "_")
                .strip("/")
                .split("/")
            )
            result_path = [element for element in segments if element != ""]
        item_id = result_path.pop()
        if result_path[0] == "redfish":
            result_path = result_path[1:]
        if result_path[0] == "v1":
            result_path = result_path[1:]
        final_path = ["hardware"] + result_path
        yield TableRow(
            path=final_path,
            key_columns={"name": name},
            inventory_columns={
                "id": item_id,
                "serial": serial,
                "part_number": part_number,
                "manufacturer": manufacturer,
                "model": model,
            },
        )


inventory_plugin_redfish_data = InventoryPlugin(
    name="redfish_data",
    sections=[
        "redfish_storage",
        "redfish_processors",
        "redfish_drives",
        "redfish_psu",
        "redfish_memory",
        "redfish_power",
        "redfish_thermal",
        "redfish_networkadapters",
    ],
    inventory_function=inventory_redfish_data,
)
