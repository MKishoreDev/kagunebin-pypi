import requests

class KaguneBin:
    SYNTAXES = [
        "python",
        "javascript",
        "typescript",
        "java",
        "cpp",
        "c",
        "csharp",
        "go",
        "rust",
        "php",
        "ruby",
        "swift",
        "kotlin",
        "html",
        "css",
        "scss",
        "json",
        "xml",
        "yaml",
        "sql",
        "bash",
        "shell",
        "text",
        "plaintext",
    ]

    def __init__(self, base_url="https://kagunebin.vercel.app"):
        self.base_url = base_url.rstrip("/")

    def syntaxes(self):
        return self.SYNTAXES.copy()

    def is_valid_syntax(self, syntax):
        return syntax.lower() in self.SYNTAXES

    def create(
        self,
        title,
        content,
        syntax="plaintext",
        password=None,
        burn_after_read=False,
    ):
        syntax = syntax.lower()

        if not self.is_valid_syntax(syntax):
            raise ValueError(
                f"Invalid syntax '{syntax}'. "
                f"Use syntaxes() to view supported languages."
            )

        payload = {
            "title": title,
            "content": content,
            "syntax": syntax,
            "is_protected": bool(password),
            "password": password,
            "is_burn_after_read": burn_after_read,
            "is_expiry": False,
        }

        response = requests.post(
            f"{self.base_url}/paste",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def get(self, paste_id, password=None):
        params = {}

        if password:
            params["password"] = password

        response = requests.get(
            f"{self.base_url}/api/paste/{paste_id}",
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def raw(self, paste_id, password=None):
        params = {}

        if password:
            params["password"] = password

        response = requests.get(
            f"{self.base_url}/raw/{paste_id}",
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        return response.text

    def download(self, paste_id, password=None):
        params = {}

        if password:
            params["password"] = password

        response = requests.get(
            f"{self.base_url}/download/{paste_id}",
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        return response.content
