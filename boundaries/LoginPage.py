"""
LoginPage <<Boundary>>
Simple authentication boundary. Not a graded use case.
"""


class LoginPage:

    # Hardcoded users for demo purposes
    USERS = {
        "staff": {"password": "staff123", "role": "Staff"},
        "manager": {"password": "manager123", "role": "Manager"},
    }

    def authenticate(self, username: str, password: str) -> dict:
        user = self.USERS.get(username)
        if user and user["password"] == password:
            return {
                "success": True,
                "username": username,
                "role": user["role"]
            }
        return {"success": False, "error": "Invalid username or password."}