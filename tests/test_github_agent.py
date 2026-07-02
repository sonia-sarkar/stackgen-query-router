import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents import GitHubAgent


def test_no_token_returns_mocked_response():
    with patch("agents._github_live_available", return_value=False), \
         patch("agents._github_token_without_repo", return_value=False):
        response = GitHubAgent().handle("show me my pull requests")
    assert "GitHubAgent" in response
    assert "pull request" in response.lower()


def test_token_set_but_no_repo_falls_back_to_mocked():
    with patch("agents._github_token_without_repo", return_value=True), \
         patch("agents._github_live_available", return_value=False):
        response = GitHubAgent().handle("show me my pull requests")
    assert "GitHubAgent" in response
    assert "pull request" in response.lower()


def test_live_mode_returns_single_repo_formatted_prs():
    live_response = (
        "GitHubAgent: You have 2 open pull requests:\n"
        "- sonia-sarkar/cenrl-son#10: Fix login bug\n"
        "- sonia-sarkar/cenrl-son#3: Add tests"
    )
    with patch("agents._github_live_available", return_value=True), \
         patch("agents._github_token_without_repo", return_value=False), \
         patch("agents._fetch_live_prs", return_value=live_response), \
         patch.dict(os.environ, {"GITHUB_REPO": "sonia-sarkar/cenrl-son"}):
        response = GitHubAgent().handle("show me my pull requests")
    assert "sonia-sarkar/cenrl-son#10" in response
    assert "GitHubAgent" in response


def test_live_api_failure_falls_back_to_mocked_response():
    with patch("agents._github_live_available", return_value=True), \
         patch("agents._github_token_without_repo", return_value=False), \
         patch("agents._fetch_live_prs", side_effect=Exception("API rate limit exceeded")), \
         patch.dict(os.environ, {"GITHUB_REPO": "sonia-sarkar/cenrl-son"}):
        response = GitHubAgent().handle("show me my pull requests")
    assert "GitHubAgent" in response
    assert "pull request" in response.lower()