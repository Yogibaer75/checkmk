// Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the
// terms and conditions defined in the file COPYING, which is part of this
// source code package.

#ifndef TableHostsByGroup_h
#define TableHostsByGroup_h

#include <string>

#include "livestatus/Table.h"
class ICore;

class TableHostsByGroup : public Table {
public:
    explicit TableHostsByGroup(ICore *mc);
    [[nodiscard]] std::string name() const override;
    [[nodiscard]] std::string namePrefix() const override;
    void answerQuery(Query &query, const User &user,
                     const ICore &core) override;
    // NOTE: We do *not* implement findObject() here, because we don't know
    // which host group we should refer to: Every host can be part of many host
    // groups.
};

#endif  // TableHostsByGroup_h
