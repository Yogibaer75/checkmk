#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import datetime
from collections import OrderedDict
from zoneinfo import ZoneInfo

import time_machine

from cmk.agent_based.v2 import Attributes
from cmk.plugins.collection.agent_based.inv_esx_vsphere_hostsystem import inv_esx_vsphere_hostsystem

from .utils_inventory import sort_inventory_result

section = OrderedDict(
    (
        ("config.product.build", ["123456"]),
        ("config.product.licenseProductName", ["VMware ESX Server"]),
        ("config.product.osType", ["vmnix-x86"]),
        ("config.product.vendor", ["VMware"]),
        ("config.product.version", ["6.7.0"]),
        ("hardware.biosInfo.biosVersion", ["-[ABIOSVERSION-1.0]-"]),
        ("hardware.biosInfo.releaseDate", ["2000-01-26T00:00:00Z"]),
        ("hardware.cpuInfo.hz", ["2933437096"]),
        ("hardware.cpuInfo.numCpuCores", ["12"]),
        ("hardware.cpuInfo.numCpuPackages", ["2"]),
        ("hardware.cpuInfo.numCpuThreads", ["24"]),
        ("hardware.cpuPkg.busHz.0", ["133338039"]),
        ("hardware.cpuPkg.description.0", ["Intel(R)", "Xeon(R)", "CPU", "X5670", "@", "2.93GHz"]),
        ("hardware.cpuPkg.hz.0", ["2933437105"]),
        ("hardware.cpuPkg.hz.1", ["2933437088"]),
        ("hardware.cpuPkg.index.0", ["1"]),
        ("hardware.cpuPkg.vendor.0", ["intel"]),
        ("hardware.memorySize", ["146016378880"]),
        ("hardware.systemInfo.model", ["System", "x1111", "M3", "-[foo-bar]-"]),
        ("hardware.systemInfo.otherIdentifyingInfo.AssetTag.0", ["none"]),
        ("hardware.systemInfo.otherIdentifyingInfo.OemSpecificString.0", ["IBM", "SystemX"]),
        ("hardware.systemInfo.otherIdentifyingInfo.ServiceTag.0", ["none"]),
        ("hardware.systemInfo.uuid", ["foo-bar"]),
        ("hardware.systemInfo.vendor", ["IBM"]),
        ("hardware.systemInfo.model", ["System", "x1", "M3", "-[123456]-"]),
        ("hardware.systemInfo.otherIdentifyingInfo.AssetTag.0", ["none"]),
        ("hardware.systemInfo.otherIdentifyingInfo.OemSpecificString.0", ["IBM", "SystemX"]),
        ("hardware.systemInfo.otherIdentifyingInfo.ServiceTag.0", ["none"]),
        ("hardware.systemInfo.uuid", ["bar-foo"]),
    )
)


def test_inventory() -> None:
    # Setting the timezone is needed, otherwise test results will differ between CI and local
    # runs
    with time_machine.travel(datetime.datetime(2024, 1, 1, tzinfo=ZoneInfo("UTC"))):
        actual = sort_inventory_result(inv_esx_vsphere_hostsystem(section))
    assert actual == sort_inventory_result(
        [
            Attributes(
                path=["hardware", "cpu"],
                inventory_attributes={
                    "max_speed": 2933437096.0,
                    "cpus": "2",
                    "cores": "12",
                    "threads": "24",
                    "model": "Intel(R) Xeon(R) CPU X5670 @ 2.93GHz",
                    "vendor": "intel",
                    "bus_speed": 133338039.0,
                    "cores_per_cpu": 6.0,
                    "threads_per_cpu": 12.0,
                },
                status_attributes={},
            ),
            Attributes(
                path=["software", "bios"],
                inventory_attributes={"version": "-[ABIOSVERSION-1.0]-", "date": "2000-01-26"},
                status_attributes={},
            ),
            Attributes(
                path=["software", "os"],
                inventory_attributes={
                    "name": "VMware ESX Server",
                    "version": "6.7.0",
                    "build": "123456",
                    "vendor": "VMware",
                    "type": "vmnix-x86",
                },
                status_attributes={},
            ),
            Attributes(
                path=["hardware", "system"],
                inventory_attributes={
                    "product": "System x1 M3 -[123456]-",
                    "vendor": "IBM",
                    "uuid": "bar-foo",
                },
                status_attributes={},
            ),
            Attributes(
                path=["hardware", "memory"],
                inventory_attributes={"total_ram_usable": 146016378880.0},
                status_attributes={},
            ),
        ]
    )
