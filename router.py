import json
import os
import re
from agents import GitHubAgent, LinearAgent

AGENT_CLASSES = {
    "GitHubAgent": GitHubAgent,
    "LinearAgent": LinearAgent,
}


def _load_config() -> dict:
    path = os.path.join(os.path.dirname(__file__), "agents_config.json")
    with open(path) as f:
        return json.load(f)


def _score(query: str, config: dict) -> dict:
    lowered = query.lower()
    return {
        name: sum(
            1 for kw in keywords
            if (re.search(rf"\b{re.escape(kw)}s?\b", lowered) if " " not in kw else kw in lowered)
        )
        for name, keywords in config.items()
    }


def _is_ambiguous(scores: dict) -> bool:
    positive = sorted([s for s in scores.values() if s > 0], reverse=True)
    return len(positive) >= 2 and (positive[0] - positive[1]) <= 1


def _multi_intent_response(query: str, scores: dict) -> str:
    ranked = sorted(
        [(name, score) for name, score in scores.items() if score > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    return "\n---\n".join(AGENT_CLASSES[name]().handle(query) for name, _ in ranked)


def _llm_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def route(query: str) -> str:
    config = _load_config()
    scores = _score(query, config)

    if _is_ambiguous(scores):
        print(f"[ROUTER] '{query}' -> ambiguous {scores}")
        if _llm_available():
            try:
                import llm_router
                label = llm_router.classify_with_llm(query)
                print(f"[ROUTER] LLM classified -> {label}")
                if label in AGENT_CLASSES:
                    return AGENT_CLASSES[label]().handle(query)
                if label == "BOTH":
                    return _multi_intent_response(query, scores)
                if label == "NONE":                             
                    return "I cannot answer this question."
            except Exception as exc:
                print(f"[ROUTER] LLM escalation failed ({exc}), falling back")
        return _multi_intent_response(query, scores)

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        print(f"[ROUTER] '{query}' -> None")
        return "I cannot answer this question."
    print(f"[ROUTER] '{query}' -> {best} (score={scores[best]})")
    return AGENT_CLASSES[best]().handle(query)
