import os, pathlib, json
from openai import OpenAI

class RepoAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = pathlib.Path(repo_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)

    def _collect_code(self) -> str:
        # Collect Python files except tests to build context (cap size)
        files = [p for p in self.repo_path.rglob("*.py") if "test" not in str(p).lower()]
        combined = []
        budget = 0
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            snippet = content[:10000]
            combined.append(f"# FILE: {f.relative_to(self.repo_path)}\n{snippet}")
            budget += len(snippet)
            if budget > 400_000:  # keep token use sane
                break
        return "\n\n".join(combined)

    def build_context(self) -> str:
        code_sample = self._collect_code()
        resp = self.client.chat.completions.create(
            model="gpt-5-think",
            messages=[
                {"role":"system","content": "Summarize Python project into key modules, APIs, data models, and integration seams. Be precise and concise."},
                {"role":"user","content": code_sample},
            ],
            max_tokens=6000,
            temperature=0.1
        )
        return resp.choices[0].message.content
