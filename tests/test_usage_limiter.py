import json
from types import SimpleNamespace

from utils.usage_limiter import (
    UsageLimitConfig,
    consume_usage,
    get_client_identifier,
    get_usage_limit,
    normalize_ip,
    resolve_client_ip,
)


def test_normalize_ip_accepts_forwarded_lists_and_ports():
    assert normalize_ip("203.0.113.7, 10.0.0.1") == "203.0.113.7"
    assert normalize_ip("203.0.113.7:443") == "203.0.113.7"
    assert normalize_ip("[2001:db8::1]:443") == "2001:db8::1"


def test_normalize_ip_rejects_invalid_values():
    assert normalize_ip("not-an-ip") is None
    assert normalize_ip("") is None
    assert normalize_ip(None) is None


def test_resolve_client_ip_prefers_context_ip():
    context = SimpleNamespace(
        ip_address="203.0.113.10",
        headers={"x-forwarded-for": "203.0.113.20"},
    )

    assert resolve_client_ip(context) == "203.0.113.10"


def test_resolve_client_ip_uses_proxy_headers():
    context = SimpleNamespace(
        ip_address=None,
        headers={"x-forwarded-for": "203.0.113.20, 10.0.0.2"},
    )

    assert resolve_client_ip(context) == "203.0.113.20"


def test_get_client_identifier_falls_back_to_session_state():
    session_state = {}
    st_module = SimpleNamespace(
        context=SimpleNamespace(ip_address=None, headers={}),
        session_state=session_state,
    )

    identifier = get_client_identifier(st_module)

    assert identifier.startswith("session:")
    assert "_ats_usage_session_id" in session_state


def test_consume_usage_allows_only_configured_runs(tmp_path):
    config = UsageLimitConfig(max_runs=2, state_path=tmp_path / "usage.json")
    client = "ip:203.0.113.30"

    first = consume_usage(client, config)
    second = consume_usage(client, config)
    third = consume_usage(client, config)

    assert first.allowed is True
    assert first.runs_remaining == 1
    assert second.allowed is True
    assert second.runs_remaining == 0
    assert third.allowed is False
    assert third.runs_used == 2


def test_consume_usage_tracks_clients_separately(tmp_path):
    config = UsageLimitConfig(max_runs=1, state_path=tmp_path / "usage.json")

    first_client = consume_usage("ip:203.0.113.40", config)
    second_client = consume_usage("ip:203.0.113.41", config)

    assert first_client.allowed is True
    assert second_client.allowed is True


def test_consume_usage_does_not_store_raw_ip(tmp_path):
    config = UsageLimitConfig(max_runs=2, state_path=tmp_path / "usage.json")
    raw_ip = "203.0.113.50"

    consume_usage(f"ip:{raw_ip}", config)

    state_text = config.state_path.read_text(encoding="utf-8")
    state = json.loads(state_text)
    assert raw_ip not in state_text
    assert len(state["clients"]) == 1


def test_consume_usage_disabled_does_not_write_state(tmp_path):
    config = UsageLimitConfig(max_runs=2, state_path=tmp_path / "usage.json", enabled=False)

    decision = consume_usage("ip:203.0.113.60", config)

    assert decision.allowed is True
    assert decision.client_key == "disabled"
    assert not config.state_path.exists()


def test_invalid_usage_limit_env_falls_back(monkeypatch):
    monkeypatch.setenv("ATS_USAGE_LIMIT", "invalid")

    assert get_usage_limit() == 2
