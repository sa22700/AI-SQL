# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

def drop_table() -> dict:
    return {
        "error": (
            "Table deletion is disabled in the "
            "fixed product catalog schema"
        )
    }