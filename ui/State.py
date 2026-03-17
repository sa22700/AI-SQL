# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass

@dataclass
class AppState:
    username: str = ""
    password: str = ""
