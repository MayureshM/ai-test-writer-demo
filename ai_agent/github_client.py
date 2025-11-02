import os, tempfile, subprocess
from github import Github

class GitHubClient:
    def __init__(self, org: str, repo: str):
        self.org = org
        self.repo_name = repo
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN not set")
        self.gh = Github(self.token)
        self.repo = self.gh.get_repo(f"{org}/{repo}")

    def _auth_url(self) -> str:
        # Use token in HTTPS URL for non-interactive auth on CI
        return f"https://{self.token}:x-oauth-basic@github.com/{self.org}/{self.repo_name}.git"

    def clone_repo(self, branch: str = "main") -> str:
        tmp = tempfile.mkdtemp(prefix="repo_")
        subprocess.run(["git", "clone", "--depth", "1", "-b", branch, self._auth_url(), tmp], check=True)
        return tmp

    def commit_and_push(self, path: str, branch: str):
        subprocess.run(["git", "-C", path, "checkout", "-b", branch], check=True)
        subprocess.run(["git", "-C", path, "add", "."], check=True)
        # Avoid failing if nothing changed
        commit = subprocess.run(["git", "-C", path, "commit", "-m", "Add AI-generated pytest suite"], capture_output=True, text=True)
        if "nothing to commit" in commit.stdout.lower() or "nothing to commit" in commit.stderr.lower():
            return False
        subprocess.run(["git", "-C", path, "push", "origin", branch], check=True)
        return True

    def open_pr(self, head_branch: str, base_branch: str = "main", title: str = "AI-generated tests (pytest)", body: str = "Automated PR adding ai-generated-tests/"):
        # Create a pull request on GitHub
        self.repo.create_pull(title=title, head=head_branch, base=base_branch, body=body)
