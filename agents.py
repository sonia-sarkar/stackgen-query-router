import os

_MOCKED_GITHUB_RESPONSES = {
    "pull_request": (
        "Here are your open pull requests — "
        "PR #42 \"Add dark mode toggle\" (3 reviews, 1 change requested), "
        "PR #41 \"Fix login redirect bug\" (1 approval, ready to merge)."
    ),
    "merge": (
        "PR #41 \"Fix login redirect bug\" was merged into main 2 hours ago."
    ),
    "branch": (
        "You have 3 active branches: feature/dark-mode, fix/login-bug, chore/update-deps."
    ),
    "commit": (
        "Your most recent commit was \"Refactor auth middleware for token refresh\", "
        "pushed 45 minutes ago."
    ),
    "review": (
        "You're requested as a reviewer on 1 pull request: "
        "#45 \"Add rate limiting to API routes\"."
    ),
    "default": (
        "Here's your GitHub summary: 2 open PRs, 1 recent merge, 3 active branches."
    ),
}

_MOCKED_LINEAR_RESPONSES = {
    "issue": (
        "You have 4 issues assigned to you: 2 in progress, 1 in review, 1 in backlog."
    ),
    "sprint": (
        "Current sprint \"Sprint 14\" ends in 3 days. You have 2 tasks remaining: "
        "\"Update onboarding flow\" and \"Fix pagination bug\"."
    ),
    "priority": (
        "You have 1 high-priority issue: LIN-91 \"Fix pagination bug\", due tomorrow."
    ),
    "backlog": (
        "Your backlog has 6 unscheduled issues, 3 of which are tagged \"bug\"."
    ),
    "in_progress": (
        "LIN-88 \"Update API docs\" is currently in progress, last updated 1 hour ago."
    ),
    "default": (
        "Here's your Linear summary: 4 assigned issues, 1 high-priority, 2 due this sprint."
    ),
}


def _match_github_response(query: str) -> str:
    q = query.lower()
    if "pull request" in q or " pr " in f" {q} " or q.startswith("pr "):
        return _MOCKED_GITHUB_RESPONSES["pull_request"]
    if "merge" in q:
        return _MOCKED_GITHUB_RESPONSES["merge"]
    if "branch" in q:
        return _MOCKED_GITHUB_RESPONSES["branch"]
    if "commit" in q:
        return _MOCKED_GITHUB_RESPONSES["commit"]
    if "review" in q or "approve" in q:
        return _MOCKED_GITHUB_RESPONSES["review"]
    return _MOCKED_GITHUB_RESPONSES["default"]


def _match_linear_response(query: str) -> str:
    q = query.lower()
    if "issue" in q or "assigned" in q:
        return _MOCKED_LINEAR_RESPONSES["issue"]
    if "sprint" in q:
        return _MOCKED_LINEAR_RESPONSES["sprint"]
    if "priority" in q:
        return _MOCKED_LINEAR_RESPONSES["priority"]
    if "backlog" in q:
        return _MOCKED_LINEAR_RESPONSES["backlog"]
    if "in progress" in q or "status" in q:
        return _MOCKED_LINEAR_RESPONSES["in_progress"]
    return _MOCKED_LINEAR_RESPONSES["default"]


def _github_live_available() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN")) and bool(os.environ.get("GITHUB_REPO"))


def _github_token_without_repo() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN")) and not bool(os.environ.get("GITHUB_REPO"))


def _fetch_live_prs() -> str:
    from github import Github
    g = Github(os.environ["GITHUB_TOKEN"])
    repo_name = os.environ["GITHUB_REPO"]
    repo = g.get_repo(repo_name)
    pulls = list(repo.get_pulls(state="open"))
    if not pulls:
        return "GitHubAgent: You have no open pull requests."
    count = len(pulls)
    lines = [f"You have {count} open pull request{'s' if count != 1 else ''}:"]
    lines += [f"- {repo_name}#{pr.number}: {pr.title}" for pr in pulls]
    return "GitHubAgent: " + "\n".join(lines)


class Agent:
    def handle(self, query: str) -> str:
        raise NotImplementedError


class GitHubAgent(Agent):
    def handle(self, query: str) -> str:
        if _github_token_without_repo():
            print("[GitHubAgent] GITHUB_TOKEN set but GITHUB_REPO missing, using mocked response")
        elif _github_live_available():
            repo = os.environ["GITHUB_REPO"]
            print(f"[GitHubAgent] Using live GitHub data for {repo}")
            try:
                return _fetch_live_prs()
            except Exception as exc:
                print(f"[GitHubAgent] Live API call failed ({exc}), falling back to mocked response")
        else:
            print("[GitHubAgent] No GITHUB_TOKEN set, using mocked response")
        return "GitHubAgent: " + _match_github_response(query)


class LinearAgent(Agent):
    def handle(self, query: str) -> str:
        return "LinearAgent: " + _match_linear_response(query)