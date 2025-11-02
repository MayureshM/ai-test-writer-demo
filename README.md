# AI Test Writer (Python + pytest)

This project scaffolds an **AI agent (GPT‑5 Thinking)** that:
1) Connects to a GitHub repo in your org,
2) Reads project files to build context,
3) Generates **pytest** unit + light integration tests,
4) Pushes them in an `ai-generated-tests/` folder on a new branch and opens a PR.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables (see .env.example)
export $(cat .env | xargs)  # macOS/Linux only

python src/main.py
```

## GitHub Actions

Add your secrets in the repo:
- **OPENAI_API_KEY**
- **GITHUB_TOKEN** (GITHUB_TOKEN is usually provided automatically in Actions; for local runs use a PAT)
- Optionally set env **GITHUB_ORG**, **GITHUB_REPO**, **BASE_BRANCH** (defaults to `main`).

Then run the **AI Test Writer** workflow from the Actions tab.

## Notes

- The agent writes **only** under `ai-generated-tests/`.
- Tests are deterministic (mocks, frozen time) and avoid network calls.
- A small number of integration tests are added if HTTP or web frameworks are detected.
