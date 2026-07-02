import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from router import route


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
