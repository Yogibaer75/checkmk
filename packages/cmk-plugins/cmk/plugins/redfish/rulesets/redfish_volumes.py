#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""rule for discovery of volume items"""

from cmk.rulesets.v1 import form_specs, Help, rule_specs, Title  # type: ignore[import]


def _form_discovery_redfish_volumes() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        title=Title("Redfish volume discovery"),
        elements={
            "item": form_specs.DictElement(
                parameter_form=form_specs.SingleChoice(
                    title=Title("Discovery settings for volumes"),
                    help_text=Help("Specify if volume item should be the current version or "
                                   "item should be build from controller and volume id."),
                    elements=[
                        form_specs.SingleChoiceElement(name="classic", title=Title("Classic")),
                        form_specs.SingleChoiceElement(name="ctrlid", title=Title("Controller ID")),
                    ],
                ),
            ),
        },
    )


rule_spec_discovery_redfish_volumes = rule_specs.DiscoveryParameters(
    title=Title("Redfish Volume discovery"),
    topic=rule_specs.Topic.SERVER_HARDWARE,
    name="discovery_redfish_volumes",
    parameter_form=_form_discovery_redfish_volumes,
)
