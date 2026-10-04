import time
from datetime import datetime, date, timezone
from typing import Optional, Union, Dict, Any, List

import requests

from .exceptions import (
    KaguneBinError,
    KaguneBinAuthError,
    KaguneBinNotFoundError,
    KaguneBinExpiredError,
    KaguneBinValidationError,
    KaguneBinConnectionError,
    KaguneBinAPIError,
)

DEFAULT_BASE_URL = "https://kagunebin.vercel.app"
USER_AGENT = "kagunebin-python/1.0.1"


class KaguneBin:
    """Official synchronous client for the KaguneBin paste sharing service."""

    SYNTAXES: List[str] = [
        "python", "javascript", "typescript", "java", "cpp", "c", "csharp",
        "go", "rust", "php", "ruby", "swift", "kotlin", "html", "css",
        "scss", "json", "xml", "yaml", "sql", "bash", "shell", "text",
        "plaintext", "markdown", "dockerfile",
    ]

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()

    def syntaxes(self) -> List[str]:
        """Return a copy of all supported syntax highlighting formats."""
        return self.SYNTAXES.copy()

    def is_valid_syntax(self, syntax: str) -> bool:
        """Check if a syntax string is supported."""
        return syntax.lower().strip() in self.SYNTAXES

    def _handle_response(self, response: requests.Response) -> requests.Response:
        status = response.status_code
        if 200 <= status < 300:
            return response

        try:
            err_json = response.json()
            err_msg = err_json.get("detail", response.text)
        except Exception:
            err_msg = response.text or f"HTTP {status}"

        if status == 400 or status == 422:
            raise KaguneBinValidationError(err_msg, status_code=status, response_body=response.text)
        elif status == 401:
            raise KaguneBinAuthError(err_msg, status_code=status, response_body=response.text)
        elif status == 404:
            raise KaguneBinNotFoundError(err_msg, status_code=status, response_body=response.text)
        elif status == 410:
            raise KaguneBinExpiredError(err_msg, status_code=status, response_body=response.text)
        elif status >= 500:
            raise KaguneBinAPIError(err_msg, status_code=status, response_body=response.text)
        else:
            raise KaguneBinError(err_msg, status_code=status, response_body=response.text)

    def verify(self) -> Dict[str, Any]:
        """Check connection status and latency to the KaguneBin service."""
        start = time.perf_counter()
        try:
            resp = self._session.get(f"{self.base_url}/status", timeout=self.timeout)
            self._handle_response(resp)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            data = resp.json()
            data["latency_ms"] = latency_ms
            return data
        except (requests.ConnectionError, requests.Timeout) as e:
            raise KaguneBinConnectionError(f"Failed to connect to {self.base_url}: {e}") from e

    def health(self) -> Dict[str, Any]:
        """Alias for verify()."""
        return self.verify()

    def create(
        self,
        content: str,
        title: str = "",
        syntax: str = "plaintext",
        password: Optional[str] = None,
        burn_after_read: bool = False,
        expires_in_hours: Optional[int] = None,
        expires_in_days: Optional[int] = None,
        expiry_date: Optional[Union[str, date]] = None,
        expiry_hour: Optional[int] = None,
        expiry_minute: Optional[int] = None,
        tz_offset_minutes: int = 0,
    ) -> Dict[str, Any]:
        """Create a new paste with optional encryption, burn-after-read, or expiration."""
        syntax = syntax.lower().strip()
        if not self.is_valid_syntax(syntax):
            raise KaguneBinValidationError(
                f"Invalid syntax '{syntax}'. Supported: {', '.join(self.SYNTAXES)}"
            )

        if expires_in_days is not None and expires_in_hours is None:
            expires_in_hours = expires_in_days * 24

        is_expiry = bool(expires_in_hours or (expiry_date and expiry_hour is not None and expiry_minute is not None))

        payload: Dict[str, Any] = {
            "title": title.strip(),
            "content": content,
            "syntax": syntax,
            "is_protected": bool(password),
            "password": password,
            "is_burn_after_read": burn_after_read,
            "is_expiry": is_expiry,
            "tz_offset_minutes": tz_offset_minutes,
        }

        if expires_in_hours is not None:
            payload["expires_in_hours"] = expires_in_hours

        if expiry_date is not None:
            payload["expiry_date"] = expiry_date.isoformat() if hasattr(expiry_date, "isoformat") else str(expiry_date)
        if expiry_hour is not None:
            payload["expiry_hour"] = expiry_hour
        if expiry_minute is not None:
            payload["expiry_minute"] = expiry_minute

        try:
            resp = self._session.post(
                f"{self.base_url}/paste",
                json=payload,
                timeout=self.timeout,
            )
            self._handle_response(resp)
            data = resp.json()
            if "url" in data and not data["url"].startswith("http"):
                data["full_url"] = f"{self.base_url}{data['url']}"
            return data
        except (requests.ConnectionError, requests.Timeout) as e:
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    def get(self, paste_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        """Fetch paste metadata and content by ID."""
        clean_id = paste_id.split("/")[-1].strip()
        params = {}
        if password:
            params["password"] = password

        try:
            resp = self._session.get(
                f"{self.base_url}/api/paste/{clean_id}",
                params=params,
                timeout=self.timeout,
            )
            self._handle_response(resp)
            data = resp.json()
            if "url" in data and not data["url"].startswith("http"):
                data["full_url"] = f"{self.base_url}{data['url']}"
            return data
        except (requests.ConnectionError, requests.Timeout) as e:
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    def raw(self, paste_id: str, password: Optional[str] = None) -> str:
        """Fetch raw plaintext content of a paste."""
        clean_id = paste_id.split("/")[-1].strip()
        params = {}
        if password:
            params["password"] = password

        try:
            resp = self._session.get(
                f"{self.base_url}/raw/{clean_id}",
                params=params,
                timeout=self.timeout,
            )
            self._handle_response(resp)
            return resp.text
        except (requests.ConnectionError, requests.Timeout) as e:
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    def download(
        self,
        paste_id: str,
        password: Optional[str] = None,
        save_as: Optional[str] = None,
    ) -> bytes:
        """Download paste binary/text content. If save_as is provided, saves to disk."""
        clean_id = paste_id.split("/")[-1].strip()
        params = {}
        if password:
            params["password"] = password

        try:
            resp = self._session.get(
                f"{self.base_url}/download/{clean_id}",
                params=params,
                timeout=self.timeout,
            )
            self._handle_response(resp)
            content = resp.content

            if save_as:
                with open(save_as, "wb") as f:
                    f.write(content)

            return content
        except (requests.ConnectionError, requests.Timeout) as e:
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e


class AsyncKaguneBin:
    """Official asynchronous client for KaguneBin using httpx."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout,
                    headers={"User-Agent": USER_AGENT},
                )
            except ImportError as e:
                raise ImportError(
                    "AsyncKaguneBin requires 'httpx'. Install it with: pip install kagunebin[async] or pip install httpx"
                ) from e
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _handle_response(self, response) -> Any:
        status = response.status_code
        if 200 <= status < 300:
            return response

        try:
            err_json = response.json()
            err_msg = err_json.get("detail", response.text)
        except Exception:
            err_msg = response.text or f"HTTP {status}"

        if status in (400, 422):
            raise KaguneBinValidationError(err_msg, status_code=status, response_body=response.text)
        elif status == 401:
            raise KaguneBinAuthError(err_msg, status_code=status, response_body=response.text)
        elif status == 404:
            raise KaguneBinNotFoundError(err_msg, status_code=status, response_body=response.text)
        elif status == 410:
            raise KaguneBinExpiredError(err_msg, status_code=status, response_body=response.text)
        elif status >= 500:
            raise KaguneBinAPIError(err_msg, status_code=status, response_body=response.text)
        else:
            raise KaguneBinError(err_msg, status_code=status, response_body=response.text)

    async def verify(self) -> Dict[str, Any]:
        client = await self._get_client()
        start = time.perf_counter()
        try:
            resp = await client.get("/status")
            await self._handle_response(resp)
            data = resp.json()
            data["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
            return data
        except Exception as e:
            raise KaguneBinConnectionError(f"Failed to connect: {e}") from e

    async def create(
        self,
        content: str,
        title: str = "",
        syntax: str = "plaintext",
        password: Optional[str] = None,
        burn_after_read: bool = False,
        expires_in_hours: Optional[int] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        client = await self._get_client()
        syntax = syntax.lower().strip()

        if expires_in_days is not None and expires_in_hours is None:
            expires_in_hours = expires_in_days * 24

        payload = {
            "title": title.strip(),
            "content": content,
            "syntax": syntax,
            "is_protected": bool(password),
            "password": password,
            "is_burn_after_read": burn_after_read,
            "is_expiry": bool(expires_in_hours),
        }
        if expires_in_hours is not None:
            payload["expires_in_hours"] = expires_in_hours

        try:
            resp = await client.post("/paste", json=payload)
            await self._handle_response(resp)
            data = resp.json()
            if "url" in data and not data["url"].startswith("http"):
                data["full_url"] = f"{self.base_url}{data['url']}"
            return data
        except Exception as e:
            if isinstance(e, KaguneBinError):
                raise
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    async def get(self, paste_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        client = await self._get_client()
        clean_id = paste_id.split("/")[-1].strip()
        params = {"password": password} if password else {}
        try:
            resp = await client.get(f"/api/paste/{clean_id}", params=params)
            await self._handle_response(resp)
            data = resp.json()
            if "url" in data and not data["url"].startswith("http"):
                data["full_url"] = f"{self.base_url}{data['url']}"
            return data
        except Exception as e:
            if isinstance(e, KaguneBinError):
                raise
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    async def raw(self, paste_id: str, password: Optional[str] = None) -> str:
        client = await self._get_client()
        clean_id = paste_id.split("/")[-1].strip()
        params = {"password": password} if password else {}
        try:
            resp = await client.get(f"/raw/{clean_id}", params=params)
            await self._handle_response(resp)
            return resp.text
        except Exception as e:
            if isinstance(e, KaguneBinError):
                raise
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e

    async def download(
        self,
        paste_id: str,
        password: Optional[str] = None,
        save_as: Optional[str] = None,
    ) -> bytes:
        client = await self._get_client()
        clean_id = paste_id.split("/")[-1].strip()
        params = {"password": password} if password else {}
        try:
            resp = await client.get(f"/download/{clean_id}", params=params)
            await self._handle_response(resp)
            content = resp.content
            if save_as:
                with open(save_as, "wb") as f:
                    f.write(content)
            return content
        except Exception as e:
            if isinstance(e, KaguneBinError):
                raise
            raise KaguneBinConnectionError(f"Connection failed: {e}") from e
