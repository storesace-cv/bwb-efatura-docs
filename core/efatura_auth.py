"""
Gerenciamento de autenticação OIDC/OAuth2 para eFatura.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple
from urllib.parse import urlencode

import requests

from core.exceptions import EfaturaAuthError, EfaturaAuthNeedsReauth


LOGGER = logging.getLogger(__name__)


DEFAULT_MIN_TTL_SECONDS = 120
DEFAULT_EXPIRES_SKEW_SECONDS = 30


@dataclass
class OIDCDiscovery:
    authorization_endpoint: str
    token_endpoint: str


class EfaturaAuthManager:
    def __init__(
        self,
        issuer_url: str,
        client_id: str,
        redirect_uri: str,
        scopes: Iterable[str],
        token_store_path: Path,
        timeout: int = 15,
        retries: int = 3,
        client_secret: Optional[str] = None,
    ) -> None:
        self.issuer_url = issuer_url.rstrip("/")
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = list(scopes)
        self.token_store_path = token_store_path
        self.timeout = timeout
        self.retries = retries
        self.client_secret = client_secret
        self._discovery: Optional[OIDCDiscovery] = None

    def discover(self) -> OIDCDiscovery:
        if self._discovery is not None:
            return self._discovery
        url = f"{self.issuer_url}/.well-known/openid-configuration"
        data = self._get_json_with_retries(url)
        try:
            discovery = OIDCDiscovery(
                authorization_endpoint=str(data["authorization_endpoint"]),
                token_endpoint=str(data["token_endpoint"]),
            )
        except KeyError as exc:
            raise EfaturaAuthError(f"OIDC discovery inválido: campo ausente {exc}") from exc
        self._discovery = discovery
        return discovery

    def build_authorization_url(self) -> Tuple[str, str, str]:
        discovery = self.discover()
        state = secrets.token_urlsafe(32)
        code_verifier = self._generate_code_verifier()
        code_challenge = self._build_code_challenge(code_verifier)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{discovery.authorization_endpoint}?{urlencode(params)}", state, code_verifier

    def exchange_code_for_tokens(self, code: str, code_verifier: str) -> Dict[str, Any]:
        discovery = self.discover()
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": code_verifier,
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret
        tokens = self._post_token_endpoint(discovery.token_endpoint, payload)
        normalized = self._normalize_tokens(tokens)
        self.save_tokens(normalized)
        return normalized

    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        discovery = self.discover()
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret
        tokens = self._post_token_endpoint(discovery.token_endpoint, payload)
        normalized = self._normalize_tokens(tokens, refresh_token_override=refresh_token)
        self.save_tokens(normalized)
        return normalized

    def get_valid_access_token(self, min_ttl_seconds: int = DEFAULT_MIN_TTL_SECONDS) -> str:
        tokens = self.load_tokens()
        if not tokens:
            raise EfaturaAuthNeedsReauth("Sem tokens persistidos.")
        access_token = tokens.get("access_token")
        if not access_token:
            raise EfaturaAuthNeedsReauth("Token inválido: access_token ausente.")

        expires_at = tokens.get("expires_at")
        if expires_at is None:
            exp = _decode_jwt_exp_unverified(access_token)
            if exp:
                expires_at = exp - DEFAULT_EXPIRES_SKEW_SECONDS
                tokens["expires_at"] = expires_at
                self.save_tokens(tokens)

        now = int(time.time())
        if expires_at and (expires_at - now) > min_ttl_seconds:
            return access_token

        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            raise EfaturaAuthNeedsReauth("Token expirado sem refresh_token.")

        try:
            refreshed = self.refresh_tokens(refresh_token)
            return str(refreshed["access_token"])
        except EfaturaAuthNeedsReauth:
            raise
        except EfaturaAuthError as exc:
            self._clear_tokens()
            raise EfaturaAuthNeedsReauth("Refresh token inválido ou revogado.") from exc

    def load_tokens(self) -> Optional[Dict[str, Any]]:
        if not self.token_store_path.exists():
            return None
        data = self._load_token_file(self.token_store_path)
        if not data:
            return None
        return self._normalize_tokens(data, persist=False)

    def save_tokens(self, data: Dict[str, Any]) -> None:
        normalized = self._normalize_tokens(data)
        self.token_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_store_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    def migrate_legacy_tokens(self, legacy_path: Path) -> bool:
        if self.token_store_path.exists():
            return False
        if not legacy_path.exists():
            return False
        data = self._load_token_file(legacy_path)
        if not data:
            return False
        normalized = self._normalize_tokens(data)
        self.save_tokens(normalized)
        return True

    def start_login(self) -> Dict[str, str]:
        authorization_url, state, code_verifier = self.build_authorization_url()
        return {
            "authorization_url": authorization_url,
            "state": state,
            "code_verifier": code_verifier,
        }

    def finish_login(self, code: str, state: str, code_verifier: str) -> Dict[str, Any]:
        _ = state
        return self.exchange_code_for_tokens(code, code_verifier)

    def _normalize_tokens(
        self,
        data: Dict[str, Any],
        *,
        refresh_token_override: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        tokens = dict(data)
        now = int(time.time())
        if refresh_token_override:
            tokens["refresh_token"] = refresh_token_override

        if "expires_at" not in tokens:
            expires_in = tokens.get("expires_in")
            if expires_in is not None:
                try:
                    expires_at = now + int(expires_in) - DEFAULT_EXPIRES_SKEW_SECONDS
                    tokens["expires_at"] = expires_at
                except (TypeError, ValueError):
                    pass

        if "expires_at" not in tokens:
            access_token = tokens.get("access_token")
            exp = _decode_jwt_exp_unverified(access_token) if access_token else None
            if exp:
                tokens["expires_at"] = int(exp) - DEFAULT_EXPIRES_SKEW_SECONDS

        tokens.setdefault("obtained_at", now)
        tokens.setdefault("token_type", "bearer")
        if "scope" not in tokens and self.scopes:
            tokens["scope"] = " ".join(self.scopes)
        tokens["issuer_url"] = self.issuer_url
        tokens["client_id"] = self.client_id
        tokens["redirect_uri"] = self.redirect_uri

        if persist and ("expires_in" in tokens):
            tokens.pop("expires_in", None)
        return tokens

    def _post_token_endpoint(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.post(url, data=payload, timeout=self.timeout)
                if response.status_code >= 400:
                    raise EfaturaAuthError(self._format_token_error(response))
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                LOGGER.warning("Erro ao chamar token endpoint (tentativa %s/%s): %s", attempt, self.retries, exc)
        raise EfaturaAuthError(f"Falha ao chamar token endpoint: {last_exc}")

    def _get_json_with_retries(self, url: str) -> Dict[str, Any]:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                LOGGER.warning("Erro ao chamar discovery (tentativa %s/%s): %s", attempt, self.retries, exc)
        raise EfaturaAuthError(f"Falha ao obter discovery OIDC: {last_exc}")

    def _format_token_error(self, response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        error = payload.get("error")
        description = payload.get("error_description") or payload.get("errorMessage")
        if error == "invalid_grant":
            self._clear_tokens()
            raise EfaturaAuthNeedsReauth("Refresh token inválido ou revogado.")
        if error:
            return f"Token endpoint retornou erro: {error} ({description})"
        return f"Token endpoint retornou HTTP {response.status_code}"

    def _clear_tokens(self) -> None:
        try:
            if self.token_store_path.exists():
                self.token_store_path.unlink()
        except OSError:
            pass

    def _load_token_file(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise EfaturaAuthError(f"Falha ao ler tokens em {path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise EfaturaAuthError(f"Formato de tokens inválido em {path}")
        if not payload.get("access_token"):
            raise EfaturaAuthError(f"Token inválido em {path}: access_token ausente")
        return payload

    @staticmethod
    def _generate_code_verifier() -> str:
        verifier = secrets.token_urlsafe(96)
        if len(verifier) < 43:
            verifier = (verifier + secrets.token_urlsafe(64))[:96]
        return verifier[:128]

    @staticmethod
    def _build_code_challenge(code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def _decode_jwt_exp_unverified(token: Optional[str]) -> Optional[int]:
    if not token:
        return None
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload = base64.urlsafe_b64decode(payload_b64 + padding)
        obj = json.loads(payload.decode("utf-8", errors="replace"))
        exp = obj.get("exp")
        return int(exp) if exp is not None else None
    except Exception:
        return None
