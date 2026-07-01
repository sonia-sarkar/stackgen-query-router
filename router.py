from agents import GitHubAgent, LinearAgent

KEYWORD_MAP = {
    "pull request": GitHubAgent,
    "pr": GitHubAgent,
    "github": GitHubAgent,
    "repo": GitHubAgent,
    "issue": LinearAgent,
    "assigned": LinearAgent,
    "ticket": LinearAgent,
    "linear": LinearAgent,
}


def route(query: str) -> str:
    lowered = query.lower()
    for keyword, agent_class in KEYWORD_MAP.items():
        if keyword in lowered:
            return agent_class().handle(query)
    return "I cannot answer this question."
