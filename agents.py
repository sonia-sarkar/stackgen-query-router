import os

_MOCKED_GITHUB_RESPONSE = (
    "GitHubAgent: Here are the open pull requests — "
    "PR #42 \"Add dark mode\" (open, 3 reviews), "
    "PR #41 \"Fix login bug\" (open, 1 review)."
)

_MOCKED_LINEAR_RESPONSE = (
    "LinearAgent: You have 2 issues assigned — "
    "LIN-88 \"Update API docs\" (In Progress), "
    "LIN-91 \"Fix pagination bug\" (Todo)."
)


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
        return _MOCKED_GITHUB_RESPONSE


class LinearAgent(Agent):
    def handle(self, query: str) -> str:
        return _MOCKED_LINEAR_RESPONSE
