class Agent:
    def handle(self, query: str) -> str:
        raise NotImplementedError


class GitHubAgent(Agent):
    def handle(self, query: str) -> str:
        return "GitHubAgent: fetching GitHub data..."


class LinearAgent(Agent):
    def handle(self, query: str) -> str:
        return "LinearAgent: fetching Linear data..."
