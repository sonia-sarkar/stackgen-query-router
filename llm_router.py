import anthropic

_SYSTEM = (
    "You are a routing classifier. Given a user query, respond with exactly one of: "
    "GitHubAgent, LinearAgent, BOTH, NONE. "
    "GitHubAgent: pull requests, repos, GitHub. "
    "LinearAgent: issues, tickets, Linear project management. "
    "BOTH: query spans both systems. NONE: unrecognized domain. "
    "Output the label only — no explanation."
)


def classify_with_llm(query: str) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        system=_SYSTEM,
        messages=[{"role": "user", "content": query}],
    )
    return next(b.text for b in message.content if b.type == "text").strip()