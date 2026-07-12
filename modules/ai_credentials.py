from __future__ import annotations

import os
from dataclasses import dataclass


SERVICE_NAME = "Living OS"
ACCOUNT_NAME = "openai_api_key"
ENVIRONMENT_VARIABLE = "OPENAI_API_KEY"


class CredentialError(RuntimeError):
    """A safe credential-store error that never contains a secret."""


@dataclass(frozen=True)
class CredentialStatus:
    configured: bool
    source: str
    masked: str


def mask_api_key(api_key: str) -> str:
    clean = api_key.strip()
    if not clean:
        return ""
    if len(clean) <= 8:
        return "********"
    return f"{clean[:3]}...{clean[-4:]}"


def _keyring():
    try:
        import keyring
    except ImportError as exc:
        raise CredentialError("Operating-system credential storage is unavailable.") from exc
    return keyring


def load_saved_api_key() -> str:
    try:
        return str(_keyring().get_password(SERVICE_NAME, ACCOUNT_NAME) or "").strip()
    except CredentialError:
        raise
    except Exception as exc:
        raise CredentialError("The saved API key could not be read from the operating-system credential store.") from exc


def save_api_key(api_key: str) -> None:
    clean = api_key.strip()
    if not clean:
        raise CredentialError("Enter an API key before saving it.")
    try:
        _keyring().set_password(SERVICE_NAME, ACCOUNT_NAME, clean)
    except CredentialError:
        raise
    except Exception as exc:
        raise CredentialError("The API key could not be saved to the operating-system credential store.") from exc


def remove_saved_api_key() -> None:
    try:
        keyring = _keyring()
        if keyring.get_password(SERVICE_NAME, ACCOUNT_NAME):
            keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
    except CredentialError:
        raise
    except Exception as exc:
        raise CredentialError("The saved API key could not be removed from the operating-system credential store.") from exc


def resolve_api_key(session_key: str = "") -> tuple[str, str]:
    clean_session_key = session_key.strip()
    if clean_session_key:
        return clean_session_key, "session"

    try:
        saved = load_saved_api_key()
    except CredentialError:
        saved = ""
    if saved:
        return saved, "operating-system credential store"

    environment_key = os.environ.get(ENVIRONMENT_VARIABLE, "").strip()
    if environment_key:
        return environment_key, "environment"
    return "", "not configured"


def credential_status(session_key: str = "") -> CredentialStatus:
    api_key, source = resolve_api_key(session_key)
    return CredentialStatus(bool(api_key), source, mask_api_key(api_key))
