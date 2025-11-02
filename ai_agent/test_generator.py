import os, json, pathlib
from openai import OpenAI

class TestGenerator:
    def __init__(self, context_text: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
        self.context = context_text

    def generate_tests(self, repo_path: str):
        prompt = f"""You are a senior Python engineer.
Generate pytest-based tests for this project given its brief below.

Project brief:
{self.context}

Requirements:
- Unit tests for core functions/classes
- Add 1-3 light integration tests if HTTP or web frameworks are detected (FastAPI/Flask/Django)
- Deterministic: mock network/IO/time/randomness; avoid real external calls
- Only write under ai-generated-tests/
- Provide minimal scaffolding (pytest.ini, conftest.py, README.md) if missing
Return a JSON array of objects: {{ "path": "ai-generated-tests/...", "content": "..." }}
"""
        response = self.client.chat.completions.create(
            model="gpt-5-think",
            messages=[
                {"role":"system","content":"Generate runnable, deterministic pytest code with clear AAAs."},
                {"role":"user","content": prompt}
            ],
            max_tokens=9000,
            temperature=0.12
        )
        text = response.choices[0].message.content
        try:
            files = json.loads(text)
            assert isinstance(files, list)
        except Exception:
            files = [{"path":"ai-generated-tests/README.md","content": text}]
        self._write_files(repo_path, files)

    def _write_files(self, repo_path: str, files):
        root = pathlib.Path(repo_path)
        # Ensure scaffolding if not present
        paths = [f.get("path","") for f in files]
        if not any(p.endswith("pytest.ini") for p in paths):
            files.append({"path":"ai-generated-tests/pytest.ini","content":"[pytest]\ntestpaths = ai-generated-tests\naddopts = -q --maxfail=1 --disable-warnings --cov=. --cov-report=term-missing\n"})
        if not any("conftest.py" in p for p in paths):
            files.append({"path":"ai-generated-tests/conftest.py","content":"import os\nimport pytest\nfrom datetime import datetime\ntry:\n    from freezegun import freeze_time\nexcept Exception:\n    freeze_time = None\n\n@pytest.fixture\ndef freeze_now():\n    if freeze_time:\n        with freeze_time('2024-01-01 00:00:00'):\n            yield datetime.utcnow()\n    else:\n        yield datetime.utcnow()\n"})
        if not any(p.endswith("README.md") for p in paths):
            files.append({"path":"ai-generated-tests/README.md","content":"# AI-generated pytest suite\n\nRun with:\n\n```bash\npip install -r requirements.txt || true\npip install pytest pytest-cov freezegun httpx responses requests-mock || true\npytest\n```\n"})
        for f in files:
            dest = root / f["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f["content"], encoding="utf-8")
