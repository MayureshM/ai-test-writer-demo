from typing import Optional

class PullRequestCreator:
    def __init__(self, gh_client):
        self.gh = gh_client

    def create_pr(self, repo_path: str, branch_name: str, base_branch: str = "main"):
        changed = self.gh.commit_and_push(repo_path, branch_name)
        if not changed:
            print("No changes to commit; skipping PR.")
            return
        self.gh.open_pr(head_branch=branch_name, base_branch=base_branch)
        print(f"Opened PR from {branch_name} -> {base_branch}")
