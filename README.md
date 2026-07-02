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

| Agent | Keywords |
|---|---|
| `GitHubAgent` | pull request, pr, github, repo |
| `LinearAgent` | issue, assigned, ticket, linear |

Add agents or change keywords by editing `agents_config.json` — no Python changes needed.

## Setup

```bash
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` to enable LLM escalation (optional):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
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
