from __future__ import annotations

import json
import os
import re
import traceback
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("APP_ROOT", str(Path(__file__).resolve().parent.parent)))
REPO_ROOT = ROOT / "legalbench-main"
TASKS_ROOT = REPO_ROOT / "tasks"
OUTPUTS_ROOT = REPO_ROOT / "outputs"
FRONTEND_ROOT = ROOT / "webapp"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def tsv_rows(path: Path) -> list[dict[str, str]]:
    lines = read_text(path).splitlines()
    if not lines:
        return []
    headers = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        parts = line.split("\t")
        while len(parts) < len(headers):
            parts.append("")
        rows.append(dict(zip(headers, parts)))
    return rows


def summarize_readme(task_dir: Path) -> str:
    for name in ("README.md", "README.MD"):
        path = task_dir / name
        if path.exists():
            text = read_text(path)
            return text[:2400]
    return ""


def sanitize_text(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\xa0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", text)
    text = re.sub(r"[\ud800-\udfff]", "", text)
    return text


def normalize_prediction(text: str) -> str:
    value = text.strip()
    patterns = [
        (r"(?i)\byes\b", "Yes"),
        (r"(?i)\bno\b", "No"),
        (r"(?i)\boption\s*([A-D])\b", None),
        (r"(?i)\banswer\s*(?:is|:)?\s*[\"']?([A-D])[\"']?\b", None),
        (r"(?i)\bcorrect answer\s*(?:is|:)?\s*[\"']?([A-D])[\"']?\b", None),
        (r"(?i)\bthe answer\s*(?:is|:)?\s*[\"']?([A-D])[\"']?\b", None),
        (r"(?i)^\s*[\"']?([A-D])[\"']?\s*$", None),
    ]
    for pattern, fixed in patterns:
        match = re.search(pattern, value)
        if match:
            return fixed or match.group(1).upper()
    return value


def render_prompt(template: str, row: dict[str, str]) -> str:
    output = template
    for match in re.findall(r"\{\{([^}]+)\}\}", template):
        key = match.strip()
        output = output.replace("{{" + match + "}}", row.get(key, ""))
    return output


def deepseek_chat(prompt: str, model: str) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY environment variable.")

    url = "https://api.deepseek.com/chat/completions"
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "user", "content": sanitize_text(prompt)}],
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API error: {detail}") from exc
    return body["choices"][0]["message"]["content"]


def task_metadata(task_name: str) -> dict[str, Any]:
    task_dir = TASKS_ROOT / task_name
    train_path = task_dir / "train.tsv"
    test_path = task_dir / "test.tsv"
    prompt_path = task_dir / "base_prompt.txt"

    train_rows = tsv_rows(train_path) if train_path.exists() else []
    test_rows = tsv_rows(test_path) if test_path.exists() else []
    prompt_template = read_text(prompt_path) if prompt_path.exists() else ""

    columns: list[str] = []
    if train_rows:
        columns = list(train_rows[0].keys())
    elif test_rows:
        columns = list(test_rows[0].keys())

    return {
        "task_name": task_name,
        "description": summarize_readme(task_dir),
        "description_html": markdown_to_html(summarize_readme(task_dir)),
        "prompt_template": prompt_template,
        "columns": columns,
        "splits": {
            "train": len(train_rows),
            "test": len(test_rows),
        },
        "has_prompt": prompt_path.exists(),
    }


def list_tasks() -> list[dict[str, Any]]:
    tasks = []
    for task_dir in sorted(TASKS_ROOT.iterdir()):
        if not task_dir.is_dir():
            continue
        base_prompt = task_dir / "base_prompt.txt"
        train_tsv = task_dir / "train.tsv"
        test_tsv = task_dir / "test.tsv"
        if base_prompt.exists() and (train_tsv.exists() or test_tsv.exists()):
            tasks.append(
                {
                    "task_name": task_dir.name,
                    "has_train": train_tsv.exists(),
                    "has_test": test_tsv.exists(),
                }
            )
    return tasks


def load_rows(task_name: str, split: str) -> list[dict[str, str]]:
    path = TASKS_ROOT / task_name / f"{split}.tsv"
    if not path.exists():
        raise FileNotFoundError(f"Dataset split not found: {path}")
    return tsv_rows(path)


def task_has_split(task_name: str, split: str) -> bool:
    return (TASKS_ROOT / task_name / f"{split}.tsv").exists()


def save_run(payload: dict[str, Any]) -> str:
    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = payload["run_id"]
    path = OUTPUTS_ROOT / f"{run_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def read_runs() -> list[dict[str, Any]]:
    if not OUTPUTS_ROOT.exists():
        return []
    runs = []
    for path in sorted(OUTPUTS_ROOT.glob("*.json"), key=lambda p: p.stat().st_mtime):
        try:
            runs.append(read_json(path))
        except Exception:
            continue
    return runs


def markdown_to_html(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    lines = escaped.splitlines()
    html_parts: list[str] = []
    in_list = False

    def inline_format(value: str) -> str:
        value = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" target="_blank" rel="noreferrer">\1</a>', value)
        value = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", value)
        value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
        return value

    for raw in lines:
        line = raw.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        if line.startswith("### "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h3>{inline_format(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{inline_format(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h1>{inline_format(line[2:])}</h1>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{inline_format(line[2:])}</li>")
            continue

        if in_list:
            html_parts.append("</ul>")
            in_list = False
        html_parts.append(f"<p>{inline_format(line)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts)


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _text(self, code: int, text: str, content_type: str) -> None:
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/index.html":
            self._text(200, read_text(FRONTEND_ROOT / "index.html"), "text/html")
            return
        if self.path == "/app.js":
            self._text(200, read_text(FRONTEND_ROOT / "app.js"), "application/javascript")
            return
        if self.path == "/styles.css":
            self._text(200, read_text(FRONTEND_ROOT / "styles.css"), "text/css")
            return
        if self.path == "/api/tasks":
            self._json(200, {"tasks": list_tasks()})
            return
        if self.path.startswith("/api/tasks/") and "/samples" not in self.path:
            task_name = self.path.replace("/api/tasks/", "", 1)
            self._json(200, task_metadata(task_name))
            return
        if self.path.startswith("/api/tasks/") and "/samples" in self.path:
            try:
                prefix, query = self.path.split("?", 1) if "?" in self.path else (self.path, "")
                task_name = prefix.split("/")[3]
                params = {}
                for item in query.split("&"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        params[key] = value
                split = params.get("split", "test")
                limit = int(params.get("limit", "20"))
                if not task_has_split(task_name, split):
                    self._json(400, {"error": f"Task '{task_name}' does not have split '{split}'."})
                    return
                rows = load_rows(task_name, split)[:limit]
                self._json(200, {"task_name": task_name, "split": split, "rows": rows})
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return
        if self.path == "/api/runs":
            self._json(200, {"runs": read_runs()})
            return
        self._text(404, "Not found", "text/plain")

    def do_POST(self) -> None:
        try:
            if self.path == "/api/run-sample":
                payload = self._body()
                task_name = payload["task_name"]
                split = payload.get("split", "test")
                row_index = int(payload.get("row_index", 0))
                model = payload.get("model", "deepseek-v4-flash")

                rows = load_rows(task_name, split)
                row = rows[row_index]
                template = read_text(TASKS_ROOT / task_name / "base_prompt.txt")
                prompt = render_prompt(template, row)
                raw_output = deepseek_chat(prompt, model)
                prediction = normalize_prediction(raw_output)

                self._json(
                    200,
                    {
                        "task_name": task_name,
                        "split": split,
                        "row_index": row_index,
                        "gold": row.get("answer", ""),
                        "prediction": prediction,
                        "raw_output": raw_output,
                        "prompt": prompt,
                        "row": row,
                    },
                )
                return

            if self.path == "/api/run-batch":
                payload = self._body()
                task_name = payload["task_name"]
                split = payload.get("split", "test")
                model = payload.get("model", "deepseek-v4-flash")
                max_samples = int(payload.get("max_samples", 10))

                rows = load_rows(task_name, split)[:max_samples]
                template = read_text(TASKS_ROOT / task_name / "base_prompt.txt")
                results = []
                correct = 0
                for row in rows:
                    prompt = render_prompt(template, row)
                    raw_output = deepseek_chat(prompt, model)
                    prediction = normalize_prediction(raw_output)
                    gold = row.get("answer", "")
                    is_correct = prediction == gold
                    correct += int(is_correct)
                    results.append(
                        {
                            "index": row.get("index", ""),
                            "gold": gold,
                            "prediction": prediction,
                            "correct": is_correct,
                            "raw_output": raw_output,
                        }
                    )

                accuracy = round(correct / len(results), 4) if results else 0
                run_id = f"{task_name}-{split}-{model}-pyapi"
                run_payload = {
                    "run_id": run_id,
                    "task": task_name,
                    "split": split,
                    "model": model,
                    "sample_count": len(results),
                    "accuracy": accuracy,
                    "results": results,
                }
                path = save_run(run_payload)
                self._json(200, {"run": run_payload, "saved_path": path})
                return

            self._text(404, "Not found", "text/plain")
        except Exception as exc:
            self._json(500, {"error": str(exc), "traceback": traceback.format_exc()})


def main() -> int:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8787"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Server running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
