import os
from ai_agent.github_client import GitHubClient
from ai_agent.repo_analyzer import RepoAnalyzer
from ai_agent.test_generator import TestGenerator
from ai_agent.pr_creator import PullRequestCreator

def main():
    org = os.getenv("GITHUB_ORG")
    repo = os.getenv("GITHUB_REPO")
    base_branch = os.getenv("BASE_BRANCH", "main")

    if not org or not repo:
        raise SystemExit("Please set GITHUB_ORG and GITHUB_REPO environment variables.")

    gh = GitHubClient(org, repo)
    tmp_repo_path = gh.clone_repo(base_branch)

    analyzer = RepoAnalyzer(tmp_repo_path)
    project_brief = analyzer.build_context()

    generator = TestGenerator(project_brief)
    generator.generate_tests(tmp_repo_path)

    pr_creator = PullRequestCreator(gh)
    pr_creator.create_pr(tmp_repo_path, branch_name="ai-tests/add-pytest-suite", base_branch=base_branch)

if __name__ == "__main__":
    main()
