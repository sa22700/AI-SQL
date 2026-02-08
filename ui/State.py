from dataclasses import dataclass

@dataclass
class AppState:
    username: str = ""
    password: str = ""
