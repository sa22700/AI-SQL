# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from core.SQLuser import ask_user

def require_admin(
    admin_username: str | None = None,
    admin_password: str | None = None,
    interactive: bool = False,
) -> dict:
    if interactive:
        auth = ask_user()
    else:
        admin_username = (admin_username or "").strip()
        admin_password = admin_password or ""
        if not admin_username:
            return {"error": "Missing username"}
        if not admin_password:
            return {"error": "Missing password"}
        auth = ask_user(
            username=admin_username,
            password=admin_password
        )
    if not auth.get("ok"):
        return {"error": auth.get("error", "Login failed")}
    if not auth.get("user", {}).get("is_admin"):
        return {"error": "Admin required"}
    return {
        "ok": True,
        "auth": auth
    }