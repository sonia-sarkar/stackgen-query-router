class Agent:
    def handle(self, query: str) -> str:
        raise NotImplementedError


class GitHubAgent(Agent):
    def handle(self, query: str) -> str:
        return (
            "GitHubAgent: Here are the open pull requests — "
            "PR #42 \"Add dark mode\" (open, 3 reviews), "
            "PR #41 \"Fix login bug\" (open, 1 review)."
        )


class LinearAgent(Agent):
    def handle(self, query: str) -> str:
        return (
            "LinearAgent: You have 2 issues assigned — "
            "LIN-88 \"Update API docs\" (In Progress), "
            "LIN-91 \"Fix pagination bug\" (Todo)."
        )
