#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import List, Tuple
import os

import cmk.utils.paths


class Theme:
    def __init__(self) -> None:
        self._default_theme = "facelift"
        self._theme = "facelift"
        self._theme_choices: List[Tuple[str, str]] = []

    def from_config(self, default_theme: str, theme_choices: List[Tuple[str, str]]) -> None:
        self._default_theme = default_theme
        self._theme = default_theme
        self._theme_choices = theme_choices

    def set(self, theme_id: str) -> None:
        if not theme_id:
            theme_id = self._default_theme

        if theme_id not in dict(self._theme_choices):
            theme_id = self._default_theme

        self._theme = theme_id

    def get(self) -> str:
        return self._theme

    def icon_themes(self) -> List[str]:
        """Returns the themes where icons of a theme can be found in increasing order of importance.
        By default the facelift theme provides all icons. If a theme wants to use different icons it
        only needs to add those icons under the same name. See detect_icon_path for a detailed list
        of paths.
        """
        return ["facelift"] if self._theme == "facelift" else ["facelift", self._theme]

    def detect_icon_path(self, icon_name: str, prefix: str) -> str:
        """Detect from which place an icon shall be used and return it's path relative to htdocs/

        Priority:
        1. In case the modern-dark theme is active: <theme> = modern-dark -> priorities 3-6
        2. In case the modern-dark theme is active: <theme> = facelift -> priorities 3-6
        3. In case a theme is active: themes/<theme>/images/icon_[name].svg in site local hierarchy
        4. In case a theme is active: themes/<theme>/images/icon_[name].svg in standard hierarchy
        5. In case a theme is active: themes/<theme>/images/icon_[name].png in site local hierarchy
        6. In case a theme is active: themes/<theme>/images/icon_[name].png in standard hierarchy
        7. images/icons/[name].png in site local hierarchy
        8. images/icons/[name].png in standard hierarchy
        """
        for theme_id in self.icon_themes():
            theme_path = "htdocs/themes/%s/images/%s_%s" % (theme_id, prefix, icon_name)
            for file_type in ["svg", "png"]:
                for base_dir in [cmk.utils.paths.web_dir, str(cmk.utils.paths.local_web_dir)]:
                    if os.path.exists(base_dir + "/" + theme_path + "." + file_type):
                        return "themes/%s/images/%s_%s.%s" % (theme_id, prefix, icon_name,
                                                              file_type)
                    if os.path.exists(base_dir + "/htdocs/images/icons/%s.%s" %
                                      (icon_name, file_type)):
                        return "images/icons/%s.%s" % (icon_name, file_type)

        return "themes/facelift/images/icon_missing.svg"

    def url(self, rel_url: str) -> str:
        return "themes/%s/%s" % (self._theme, rel_url)
