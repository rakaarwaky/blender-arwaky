"""T-12: RedactionRulesCapability — substring semantics, recursion, composition extension."""

from __future__ import annotations

import pytest

from modules.config.src.capabilities_redaction_rules import RedactionRulesCapability
from modules.shared.src.config.taxonomy_config_constant import REDACTION_PLACEHOLDER


@pytest.mark.unit
def test_auth_token_redacted():
    cap = RedactionRulesCapability()
    assert cap.redact_value("auth_token", "secret123") == REDACTION_PLACEHOLDER


@pytest.mark.unit
def test_oauth_secret_redacted():
    cap = RedactionRulesCapability()
    assert cap.redact_value("oauth.secret", "value") == REDACTION_PLACEHOLDER


@pytest.mark.unit
def test_substring_false_positive_accepted():
    # Q14: 'auth' substring also matches 'author' — accepted false positive
    cap = RedactionRulesCapability()
    assert cap.redact_value("author", "Some Author Name") == REDACTION_PLACEHOLDER


@pytest.mark.unit
def test_non_sensitive_passthrough():
    cap = RedactionRulesCapability()
    assert cap.redact_value("title", "My Project") == "My Project"


@pytest.mark.unit
def test_redact_dict_recurses_nested():
    cap = RedactionRulesCapability()
    data = {"user": {"api_key": "abc"}, "name": "ok"}
    out = cap.redact_dict(data)
    assert out["user"]["api_key"] == REDACTION_PLACEHOLDER
    assert out["name"] == "ok"


@pytest.mark.unit
def test_redact_dict_list_of_dicts():
    cap = RedactionRulesCapability()
    data = {"items": [{"password": "p1"}, {"name": "x"}]}
    out = cap.redact_dict(data)
    assert out["items"][0]["password"] == REDACTION_PLACEHOLDER
    assert out["items"][1]["name"] == "x"


@pytest.mark.unit
def test_extra_patterns_via_constructor():
    cap = RedactionRulesCapability(extra_patterns=("custom_secret",))
    assert cap.redact_value("custom_secret", "v") == REDACTION_PLACEHOLDER


@pytest.mark.unit
def test_placeholder_constant_exact():
    cap = RedactionRulesCapability()
    assert cap.get_redaction_rule().placeholder == "***REDACTED***"
    assert cap.get_redaction_rule().full_redact is True
