import sys
import os
import pytest
import json
from router import route, _load_config
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from router import route


@pytest.fixture(autouse=True)
def no_live_github():
    """Ensure router tests never accidentally hit real GitHub, regardless
    of what's set in the shell environment (e.g. leftover GITHUB_TOKEN)."""
    with patch("agents._github_live_available", return_value=False), \
         patch("agents._github_token_without_repo", return_value=False):
        yield


def test_github_route():
    response = route("show me open pull requests")
    assert "GitHubAgent" in response


def test_linear_route():
    response = route("what issues are assigned to me in linear")
    assert "LinearAgent" in response


def test_no_match():
    response = route("what is the weather today")
    assert response == "I cannot answer this question."


def test_high_confidence_skips_ambiguity():
    # three GitHub keywords → clear winner, LinearAgent must not appear
    response = route("review my pull request on github repo")
    assert "GitHubAgent" in response
    assert "LinearAgent" not in response


def test_ambiguous_without_llm_returns_multi_intent():
    # "github" (+1 GitHub) + "issues" contains "issue" (+1 Linear) + "assigned" (+1 Linear)
    # scores: GitHub=1, Linear=2 → diff=1 → ambiguous; no LLM → multi-intent
    with patch("router._llm_available", return_value=False):
        response = route("show me github issues assigned to me")
    assert "GitHubAgent" in response
    assert "LinearAgent" in response


def test_ambiguous_with_llm_routes_to_classified_agent():
    with patch("router._llm_available", return_value=True), \
         patch("llm_router.classify_with_llm", return_value="LinearAgent"):
        response = route("show me github issues assigned to me")
    assert "LinearAgent" in response


def test_ambiguous_with_llm_returns_both_combines_responses():
    with patch("router._llm_available", return_value=True), \
         patch("llm_router.classify_with_llm", return_value="BOTH"):
        response = route("show me github issues assigned to me")
    assert "GitHubAgent" in response
    assert "LinearAgent" in response


def test_ambiguous_with_llm_returns_none_gives_fallback_message():
    with patch("router._llm_available", return_value=True), \
         patch("llm_router.classify_with_llm", return_value="NONE"):
        response = route("show me github issues assigned to me")
    assert response == "I cannot answer this question."


def test_missing_config_file_raises_clear_error():
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with pytest.raises(FileNotFoundError):
            _load_config()


def test_malformed_config_file_raises_json_error():
    from unittest.mock import mock_open
    bad_json = "{ this is not valid json "
    with patch("builtins.open", mock_open(read_data=bad_json)):
        with pytest.raises(json.JSONDecodeError):
            _load_config()



def test_pr_does_not_falsely_match_inside_other_words():
    # "project" and "comprehensive" both contain "pr" as a substring —
    # this must NOT be treated as a GitHub "pr" keyword match
    response = route("give me a comprehensive project status update")
    assert response == "I cannot answer this question."


def test_standalone_pr_still_matches_github():
    # sanity check: "pr" as its own word should still route correctly
    response = route("any updates on my pr")
    assert "GitHubAgent" in response