import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from router import route


def test_github_keywords_route_to_github_agent():
    response = route("show me open pull requests")
    assert "GitHubAgent" in response


def test_linear_keywords_route_to_linear_agent():
    response = route("what issues are assigned to me")
    assert "LinearAgent" in response


def test_unrecognized_query_falls_through():
    response = route("what is the weather today")
    assert response == "I cannot answer this question."
