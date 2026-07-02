# Query Router

Routes natural-language queries to the right agent using three-tier logic.

## Architecture

Tiers are applied in order on every query:

1. **Keyword scoring** — loads keyword lists from `agents_config.json`, counts matches per agent, picks the highest scorer.
2. **Ambiguity detection** — if the top two agents score within 1 point of each other (and both have at least one match), the query is flagged as ambiguous. Without an API key the router merges both agents' responses, separated by `---`.
3. **LLM escalation** — when `ANTHROPIC_API_KEY` is set, ambiguous queries are sent to Claude Opus 4.8 for authoritative single-agent classification before falling back to the merged response.

```
query
  │
  ▼
keyword scoring (agents_config.json)
  │
  ├─ clear winner ──────────────────────────► agent response
  │
  └─ ambiguous (scores within 1)
       │
       ├─ ANTHROPIC_API_KEY set? ──yes──► LLM classify ──► agent response
       │                                        │
       │                                  classification = BOTH
       │                                  or LLM fails
       │                                        │
       └─ no ◄──────────────────────────────────┘
            │
            ▼
       multi-intent: both agents respond, joined by ---
```

## Agents

| Agent | Keywords | Live mode |
|---|---|---|
| `GitHubAgent` | pull request, pr, github, repo | Yes — set `GITHUB_TOKEN` + `GITHUB_REPO` |
| `LinearAgent` | issue, assigned, ticket, linear | No (mocked only) |

Add agents or change keywords by editing `agents_config.json` — no Python changes needed.

### GitHubAgent live mode

When both `GITHUB_TOKEN` and `GITHUB_REPO` are set, GitHubAgent fetches real open pull requests from that specific repo. Scoped to one repo rather than the full account because a real agent would typically watch a specific project, not a user's entire GitHub history.

`GITHUB_REPO` format: `owner/repo`, e.g. `sonia-sarkar/cenrl-son`.

If `GITHUB_TOKEN` is set but `GITHUB_REPO` is missing, GitHubAgent logs the missing config and falls back to the mocked response rather than crashing or scanning all repos. Same fallback applies if the live API call fails for any reason (bad token, wrong repo name, rate limit, network error).

To generate a token: GitHub → Settings → Developer settings → Personal access tokens → Generate new token. A classic token with the `repo` scope, or a fine-grained token with **Pull requests: Read** on the target repo, is sufficient.

LinearAgent is mocked-only. A live integration would require a Linear workspace with real data and a Linear API key, which is out of scope here.

### Zero-setup mode

The project runs fully with **no environment variables set**. Both agents return realistic hardcoded responses, and all tests pass without any credentials.

## Setup

```bash
pip install -r requirements.txt
```

Optional environment variables:

```bash
export GITHUB_TOKEN=ghp_...                   # required for live GitHub data
export GITHUB_REPO=owner/repo                 # required for live GitHub data (e.g. sonia-sarkar/cenrl-son)
export ANTHROPIC_API_KEY=sk-ant-...           # enables LLM escalation for ambiguous queries
```

## Usage

```bash
python main.py
```

Example session:

```
Query: show me open pull requests
GitHubAgent: Here are the open pull requests — PR #42 "Add dark mode" (open, 3 reviews), PR #41 "Fix login bug" (open, 1 review).

Query: what github tickets are open
[ROUTER] 'what github tickets are open' -> ambiguous {'GitHubAgent': 1, 'LinearAgent': 1}
GitHubAgent: Here are the open pull requests — ...
---
LinearAgent: You have 2 issues assigned — ...

Query: exit
Goodbye!
```

## Tests

```bash
pytest tests/ -v
```
