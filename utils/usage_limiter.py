from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from ipaddress import ip_address
from pathlib import Path
from typing import Any

DEFAULT_MAX_RUNS = 2
DEFAULT_STATE_PATH = Path("/tmp/ats_resume_checker_usage.json")
_LOCK = threading.Lock()


@dataclass(frozen=True)
class UsageLimitConfig:
    max_runs: int
    state_path: Path
    enabled: bool = True


@dataclass(frozen=True)
class UsageDecision:
    allowed: bool
    runs_used: int
    runs_remaining: int
    max_runs: int
    client_key: str


def usage_limit_enabled() -> bool:
    raw_value = os.getenv("ATS_USAGE_LIMIT_ENABLED", "1").strip().lower()
    return raw_value not in {"0", "false", "no", "off", "disabled"}


def get_usage_limit() -> int:
    raw_value = os.getenv("ATS_USAGE_LIMIT", str(DEFAULT_MAX_RUNS)).strip()
    try:
        return max(1, int(raw_value))
    except ValueError:
        return DEFAULT_MAX_RUNS


def get_usage_state_path() -> Path:
    raw_path = os.getenv("ATS_USAGE_LIMIT_PATH")
    return Path(raw_path).expanduser() if raw_path else DEFAULT_STATE_PATH


def get_usage_config() -> UsageLimitConfig:
    return UsageLimitConfig(
        max_runs=get_usage_limit(),
        state_path=get_usage_state_path(),
        enabled=usage_limit_enabled(),
    )


def normalize_ip(value: Any) -> str | None:
    if value is None:
        return None

    raw_value = str(value).strip().strip('"').strip("'")
    if not raw_value:
        return None

    if "," in raw_value:
        for part in raw_value.split(","):
            normalized = normalize_ip(part)
            if normalized:
                return normalized
        return None

    if raw_value.startswith("[") and "]" in raw_value:
        raw_value = raw_value[1 : raw_value.index("]")]
    elif raw_value.count(":") == 1:
        host, maybe_port = raw_value.rsplit(":", 1)
        if maybe_port.isdigit():
            raw_value = host

    try:
        return str(ip_address(raw_value))
    except ValueError:
        return None


def _header_value(headers: Any, name: str) -> str | None:
    if not headers:
        return None
    for candidate in (name, name.lower(), name.upper()):
        try:
            value = headers.get(candidate)
        except AttributeError:
            value = None
        if value:
            return str(value)
    return None


def resolve_client_ip(streamlit_context: Any) -> str | None:
    direct_ip = normalize_ip(getattr(streamlit_context, "ip_address", None))
    if direct_ip:
        return direct_ip

    headers = getattr(streamlit_context, "headers", None)
    for header in ("x-forwarded-for", "cf-connecting-ip", "x-real-ip", "forwarded"):
        value = _header_value(headers, header)
        if not value:
            continue
        if header == "forwarded":
            for part in value.split(";"):
                key, separator, forwarded_value = part.partition("=")
                if separator and key.strip().lower() == "for":
                    value = forwarded_value
                    break
        normalized = normalize_ip(value)
        if normalized:
            return normalized

    return None


def get_client_identifier(st_module: Any) -> str:
    client_ip = resolve_client_ip(getattr(st_module, "context", None))
    if client_ip:
        return f"ip:{client_ip}"

    session_state = getattr(st_module, "session_state", None)
    if session_state is not None:
        if "_ats_usage_session_id" not in session_state:
            session_state["_ats_usage_session_id"] = secrets.token_urlsafe(24)
        return f"session:{session_state['_ats_usage_session_id']}"

    return "session:unknown"


def _new_state() -> dict[str, Any]:
    state: dict[str, Any] = {"version": 1, "clients": {}}
    if not os.getenv("ATS_USAGE_SALT"):
        state["salt"] = secrets.token_hex(32)
    return state


def _load_state(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return _new_state()

    if not isinstance(state, dict):
        return _new_state()
    if not isinstance(state.get("clients"), dict):
        state["clients"] = {}
    if not os.getenv("ATS_USAGE_SALT") and not state.get("salt"):
        state["salt"] = secrets.token_hex(32)
    return state


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _client_key(client_identifier: str, salt: str) -> str:
    digest = hmac.new(salt.encode("utf-8"), client_identifier.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()[:32]


def consume_usage(
    client_identifier: str,
    config: UsageLimitConfig | None = None,
) -> UsageDecision:
    config = config or get_usage_config()
    max_runs = max(1, config.max_runs)

    if not config.enabled:
        return UsageDecision(
            allowed=True,
            runs_used=0,
            runs_remaining=max_runs,
            max_runs=max_runs,
            client_key="disabled",
        )

    with _LOCK:
        state = _load_state(config.state_path)
        salt = os.getenv("ATS_USAGE_SALT") or str(state.get("salt") or secrets.token_hex(32))
        if not os.getenv("ATS_USAGE_SALT"):
            state["salt"] = salt
        client_key = _client_key(client_identifier, salt)
        clients = state.setdefault("clients", {})
        record = clients.setdefault(client_key, {"runs": 0})
        runs_used = max(0, int(record.get("runs", 0)))

        if runs_used >= max_runs:
            return UsageDecision(
                allowed=False,
                runs_used=runs_used,
                runs_remaining=0,
                max_runs=max_runs,
                client_key=client_key,
            )

        runs_used += 1
        record["runs"] = runs_used
        record["updated_at"] = datetime.now(UTC).isoformat()
        _write_state(config.state_path, state)

    return UsageDecision(
        allowed=True,
        runs_used=runs_used,
        runs_remaining=max(0, max_runs - runs_used),
        max_runs=max_runs,
        client_key=client_key,
    )
