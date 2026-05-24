from __future__ import annotations

import json
import os
import re
import time
import traceback
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(os.environ.get("APP_ROOT", str(Path(__file__).resolve().parent.parent)))
BENCH_ROOT = ROOT / "lawbench-opencompass"
DATA_ROOT = BENCH_ROOT / "data"
PREDICTIONS_ROOT = BENCH_ROOT / "predictions"
APP_RUNS_ROOT = ROOT / "outputs"
FRONTEND_ROOT = ROOT / "webapp"
DOCS_ROOT = ROOT / "docs"

PROMPT_SCHEMA = "instruction + '\\n\\n' + question"
SINGLE_CHOICE_TASKS = {"1-2", "2-4", "2-8", "3-6"}
OPTION_LIST = ["A", "B", "C", "D"]

TASK_CATALOG: list[dict[str, Any]] = [
    {
        "task_id": "1-1",
        "name_zh": "法条背诵",
        "name_en": "Article Recitation",
        "level": "法律知识记忆",
        "source": "FLK",
        "metric": "ROUGE-L",
        "task_type": "生成",
        "online_batch": False,
    },
    {
        "task_id": "1-2",
        "name_zh": "法律知识问答",
        "name_en": "Knowledge Question Answering",
        "level": "法律知识记忆",
        "source": "JEC_QA",
        "metric": "Accuracy",
        "task_type": "单选",
        "online_batch": True,
    },
    {
        "task_id": "2-1",
        "name_zh": "文书校对",
        "name_en": "Document Proofread",
        "level": "法律知识理解",
        "source": "CAIL2022",
        "metric": "F0.5",
        "task_type": "生成",
        "online_batch": False,
    },
    {
        "task_id": "2-2",
        "name_zh": "纠纷焦点识别",
        "name_en": "Dispute Focus Identification",
        "level": "法律知识理解",
        "source": "LAIC2021",
        "metric": "F1",
        "task_type": "多选",
        "online_batch": False,
    },
    {
        "task_id": "2-3",
        "name_zh": "婚姻纠纷识别",
        "name_en": "Marital Disputes Identification",
        "level": "法律知识理解",
        "source": "AIStudio",
        "metric": "F1",
        "task_type": "多选",
        "online_batch": False,
    },
    {
        "task_id": "2-4",
        "name_zh": "问题主题识别",
        "name_en": "Issue Topic Identification",
        "level": "法律知识理解",
        "source": "CrimeKgAssistant",
        "metric": "Accuracy",
        "task_type": "单选",
        "online_batch": True,
    },
    {
        "task_id": "2-5",
        "name_zh": "阅读理解",
        "name_en": "Reading Comprehension",
        "level": "法律知识理解",
        "source": "CAIL2019",
        "metric": "rc-F1",
        "task_type": "抽取",
        "online_batch": False,
    },
    {
        "task_id": "2-6",
        "name_zh": "命名实体识别",
        "name_en": "Named Entity Recognition",
        "level": "法律知识理解",
        "source": "CAIL2021",
        "metric": "soft-F1",
        "task_type": "抽取",
        "online_batch": False,
    },
    {
        "task_id": "2-7",
        "name_zh": "舆情摘要",
        "name_en": "Opinion Summarization",
        "level": "法律知识理解",
        "source": "CAIL2022",
        "metric": "ROUGE-L",
        "task_type": "生成",
        "online_batch": False,
    },
    {
        "task_id": "2-8",
        "name_zh": "论点挖掘",
        "name_en": "Argument Mining",
        "level": "法律知识理解",
        "source": "CAIL2022",
        "metric": "Accuracy",
        "task_type": "单选",
        "online_batch": True,
    },
    {
        "task_id": "2-9",
        "name_zh": "事件检测",
        "name_en": "Event Detection",
        "level": "法律知识理解",
        "source": "LEVEN",
        "metric": "F1",
        "task_type": "多选",
        "online_batch": False,
    },
    {
        "task_id": "2-10",
        "name_zh": "触发词提取",
        "name_en": "Trigger Word Extraction",
        "level": "法律知识理解",
        "source": "LEVEN",
        "metric": "soft-F1",
        "task_type": "抽取",
        "online_batch": False,
    },
    {
        "task_id": "3-1",
        "name_zh": "法条预测（基于事实）",
        "name_en": "Fact-based Article Prediction",
        "level": "法律知识应用",
        "source": "CAIL2018",
        "metric": "F1",
        "task_type": "多选",
        "online_batch": False,
    },
    {
        "task_id": "3-2",
        "name_zh": "法条预测（基于场景）",
        "name_en": "Scene-based Article Prediction",
        "level": "法律知识应用",
        "source": "LawGPT_zh Project",
        "metric": "ROUGE-L",
        "task_type": "生成",
        "online_batch": False,
    },
    {
        "task_id": "3-3",
        "name_zh": "罪名预测",
        "name_en": "Charge Prediction",
        "level": "法律知识应用",
        "source": "CAIL2018",
        "metric": "F1",
        "task_type": "多选",
        "online_batch": False,
    },
    {
        "task_id": "3-4",
        "name_zh": "刑期预测（无法条内容）",
        "name_en": "Prison Term Prediction w.o Article",
        "level": "法律知识应用",
        "source": "CAIL2018",
        "metric": "Normalized log-distance",
        "task_type": "回归",
        "online_batch": False,
    },
    {
        "task_id": "3-5",
        "name_zh": "刑期预测（给定法条内容）",
        "name_en": "Prison Term Prediction w. Article",
        "level": "法律知识应用",
        "source": "CAIL2018",
        "metric": "Normalized log-distance",
        "task_type": "回归",
        "online_batch": False,
    },
    {
        "task_id": "3-6",
        "name_zh": "案例分析",
        "name_en": "Case Analysis",
        "level": "法律知识应用",
        "source": "JEC_QA",
        "metric": "Accuracy",
        "task_type": "单选",
        "online_batch": True,
    },
    {
        "task_id": "3-7",
        "name_zh": "犯罪金额计算",
        "name_en": "Criminal Damages Calculation",
        "level": "法律知识应用",
        "source": "LAIC2021",
        "metric": "Accuracy",
        "task_type": "回归",
        "online_batch": False,
    },
    {
        "task_id": "3-8",
        "name_zh": "咨询",
        "name_en": "Consultation",
        "level": "法律知识应用",
        "source": "hualv.com",
        "metric": "ROUGE-L",
        "task_type": "生成",
        "online_batch": False,
    },
]

TASK_MAP = {item["task_id"]: item for item in TASK_CATALOG}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def markdown_to_html(text: str) -> str:
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_parts: list[str] = []
    in_list = False
    for raw in escaped.splitlines():
        line = raw.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
        line = re.sub(
            r"\[(.*?)\]\((.*?)\)",
            r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
            line,
        )
        line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        if line.startswith("# "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h1>{line[2:]}</h1>")
            continue
        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{line[3:]}</h2>")
            continue
        if line.startswith("### "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h3>{line[4:]}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{line[2:]}</li>")
            continue
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        html_parts.append(f"<p>{line}</p>")
    if in_list:
        html_parts.append("</ul>")
    return "".join(html_parts)


def load_examples(task_id: str, shot: str) -> list[dict[str, Any]]:
    path = DATA_ROOT / shot / f"{task_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"未找到数据文件: {path}")
    data = read_json(path)
    if not isinstance(data, list):
        raise RuntimeError(f"数据格式异常: {path}")
    return data


def prompt_from_example(example: dict[str, Any]) -> str:
    instruction = str(example.get("instruction", "")).strip()
    question = str(example.get("question", "")).strip()
    if instruction and question:
        return f"{instruction}\n\n{question}"
    return instruction or question


def deepseek_chat(prompt: str, model: str, timeout: int = 120) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY 环境变量。")
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "user", "content": sanitize_text(prompt)}],
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API 错误: {detail}") from exc
    return str(body["choices"][0]["message"]["content"])


def extract_answer_letter(answer: str) -> str:
    for option in OPTION_LIST:
        if option in answer:
            return option
    return ""


def normalize_choice_prediction(text: str) -> str:
    value = text.strip()
    patterns = [
        r"\[正确答案\]\s*([A-D])\s*<eoa>",
        r"\[姝ｇ‘绛旀\]\s*([A-D])\s*<eoa>",
        r"正确答案[:：]?\s*([A-D])",
        r"姝ｇ‘绛旀[:：]?\s*([A-D])",
        r"(?i)\bcorrect answer\s*(?:is|:)?\s*([A-D])\b",
        r"(?i)\banswer\s*(?:is|:)?\s*([A-D])\b",
        r"(?i)\boption\s*([A-D])\b",
        r"(?i)^\s*([A-D])\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1).upper()
    present = [option for option in OPTION_LIST if option in value]
    if len(present) == 1:
        return present[0]
    return value


def score_single_choice(prediction: str, answer_letter: str) -> tuple[int, int]:
    count_dict = {option: 1 if option in prediction else 0 for option in OPTION_LIST}
    if sum(count_dict.values()) == 0:
        return 0, 1
    if count_dict.get(answer_letter, 0) == 1 and sum(count_dict.values()) == 1:
        return 1, 0
    return 0, 0


def task_markdown(task_id: str, sample: dict[str, Any]) -> str:
    task = TASK_MAP[task_id]
    support_text = "支持" if task["online_batch"] else "当前仅支持单条交互推理"
    return "\n".join(
        [
            f"## {task_id} {task['name_zh']}",
            f"- 英文名称：{task['name_en']}",
            f"- 认知层级：{task['level']}",
            f"- 数据来源：{task['source']}",
            f"- 指标：{task['metric']}",
            f"- 任务类型：{task['task_type']}",
            f"- 在线批量评测：{support_text}",
            "",
            "当前演示系统采用 LawBench 官方 JSON 样本格式，每条数据都包含：",
            "- `instruction`：任务指令",
            "- `question`：具体法律问题或样本文本",
            "- `answer`：官方标准答案",
            "",
            f"当前页面展示的 Prompt 结构固定为：`{PROMPT_SCHEMA}`。",
            "前端会先让你浏览数据集设计，再把选中的样本拼成 Prompt，后端再调用 DeepSeek 生成回答。",
            "",
            f"该任务第一条样本的指令预览：`{str(sample.get('instruction', ''))[:120]}`",
        ]
    )


def design_doc_html() -> str:
    design_path = DOCS_ROOT / "frontend-backend-design.md"
    if not design_path.exists():
        return ""
    return markdown_to_html(read_text(design_path))


def benchmark_overview() -> dict[str, Any]:
    level_counts: dict[str, int] = {}
    for item in TASK_CATALOG:
        level_counts[item["level"]] = level_counts.get(item["level"], 0) + 1
    return {
        "benchmark_name": "LawBench",
        "subtitle": "基于中国法律体系的中文法律大模型评测基准",
        "task_count": len(TASK_CATALOG),
        "examples_per_task": 500,
        "prompt_settings": ["zero_shot", "one_shot"],
        "prompt_schema": PROMPT_SCHEMA,
        "levels": level_counts,
        "online_batch_tasks": sorted(SINGLE_CHOICE_TASKS),
        "design_doc_html": design_doc_html(),
    }


def task_list_payload() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for task in TASK_CATALOG:
        zero_count = len(load_examples(task["task_id"], "zero_shot"))
        one_count = len(load_examples(task["task_id"], "one_shot"))
        items.append(
            {
                **task,
                "zero_shot_count": zero_count,
                "one_shot_count": one_count,
            }
        )
    return items


def task_detail_payload(task_id: str) -> dict[str, Any]:
    if task_id not in TASK_MAP:
        raise KeyError(f"未知任务: {task_id}")
    first_example = load_examples(task_id, "zero_shot")[0]
    prompt_preview = prompt_from_example(first_example)
    description_html = markdown_to_html(task_markdown(task_id, first_example))
    return {
        **TASK_MAP[task_id],
        "sample_count_per_setting": {
            "zero_shot": len(load_examples(task_id, "zero_shot")),
            "one_shot": len(load_examples(task_id, "one_shot")),
        },
        "prompt_schema": PROMPT_SCHEMA,
        "prompt_preview": prompt_preview,
        "description_html": description_html,
        "first_example": first_example,
    }


def sample_rows_payload(task_id: str, shot: str, limit: int) -> list[dict[str, Any]]:
    rows = load_examples(task_id, shot)[:limit]
    payload_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        payload_rows.append(
            {
                "index": index,
                "instruction": str(row.get("instruction", "")),
                "question": str(row.get("question", "")),
                "answer": str(row.get("answer", "")),
            }
        )
    return payload_rows


def official_prediction_path(task_id: str, shot: str, model: str) -> Path:
    safe_model = model.replace("/", "-")
    return PREDICTIONS_ROOT / shot / safe_model / f"{task_id}.json"


def save_official_predictions(task_id: str, shot: str, model: str, predictions: dict[str, Any]) -> str:
    path = official_prediction_path(task_id, shot, model)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(predictions, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def save_run(payload: dict[str, Any]) -> str:
    APP_RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    path = APP_RUNS_ROOT / f"{payload['run_id']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def read_runs() -> list[dict[str, Any]]:
    if not APP_RUNS_ROOT.exists():
        return []
    runs: list[dict[str, Any]] = []
    for path in sorted(APP_RUNS_ROOT.glob("*.json"), key=lambda p: p.stat().st_mtime):
        try:
            item = read_json(path)
        except Exception:
            continue
        item["saved_path"] = str(path)
        runs.append(item)
    return runs


def read_run(run_id: str) -> dict[str, Any] | None:
    path = APP_RUNS_ROOT / f"{run_id}.json"
    if not path.exists():
        return None
    data = read_json(path)
    data["saved_path"] = str(path)
    return data


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
        self.send_header("Access-Control-Allow-Origin", "*")
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
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        try:
            if route == "/" or route == "/index.html":
                self._text(200, read_text(FRONTEND_ROOT / "index.html"), "text/html")
                return
            if route == "/app.js":
                self._text(200, read_text(FRONTEND_ROOT / "app.js"), "application/javascript")
                return
            if route == "/styles.css":
                self._text(200, read_text(FRONTEND_ROOT / "styles.css"), "text/css")
                return
            if route == "/api/overview":
                self._json(200, benchmark_overview())
                return
            if route == "/api/tasks":
                self._json(200, {"tasks": task_list_payload()})
                return
            if route.startswith("/api/tasks/") and route.endswith("/samples"):
                task_id = route.split("/")[3]
                shot = query.get("shot", ["zero_shot"])[0]
                limit = int(query.get("limit", ["8"])[0])
                self._json(
                    200,
                    {
                        "task_id": task_id,
                        "shot": shot,
                        "rows": sample_rows_payload(task_id, shot, limit),
                    },
                )
                return
            if route.startswith("/api/tasks/"):
                task_id = route.split("/")[3]
                self._json(200, task_detail_payload(task_id))
                return
            if route == "/api/runs":
                self._json(200, {"runs": read_runs()})
                return
            if route.startswith("/api/runs/"):
                run_id = route.split("/")[3]
                run = read_run(run_id)
                if run is None:
                    self._json(404, {"error": f"未找到运行记录: {run_id}"})
                    return
                self._json(200, run)
                return
            self._text(404, "Not found", "text/plain")
        except Exception as exc:
            self._json(500, {"error": str(exc), "traceback": traceback.format_exc()})

    def do_POST(self) -> None:
        try:
            if self.path == "/api/run-sample":
                payload = self._body()
                task_id = str(payload["task_id"])
                shot = str(payload.get("shot", "zero_shot"))
                sample_index = int(payload.get("sample_index", 0))
                model = str(payload.get("model", "deepseek-v4-flash"))

                examples = load_examples(task_id, shot)
                example = examples[sample_index]
                prompt = prompt_from_example(example)
                raw_output = deepseek_chat(prompt, model)

                normalized_prediction = raw_output.strip()
                answer_letter = ""
                correct: bool | None = None

                if task_id in SINGLE_CHOICE_TASKS:
                    answer_letter = extract_answer_letter(str(example.get("answer", "")))
                    normalized_prediction = normalize_choice_prediction(raw_output)
                    score, _ = score_single_choice(normalized_prediction, answer_letter)
                    correct = bool(score)

                self._json(
                    200,
                    {
                        "task_id": task_id,
                        "shot": shot,
                        "sample_index": sample_index,
                        "model": model,
                        "gold": str(example.get("answer", "")),
                        "gold_choice": answer_letter,
                        "prediction": normalized_prediction,
                        "correct": correct,
                        "raw_output": raw_output,
                        "prompt": prompt,
                        "example": example,
                    },
                )
                return

            if self.path == "/api/run-batch":
                payload = self._body()
                task_id = str(payload["task_id"])
                shot = str(payload.get("shot", "zero_shot"))
                model = str(payload.get("model", "deepseek-v4-flash"))
                max_samples = int(payload.get("max_samples", 10))
                timeout = int(payload.get("timeout", 120))

                if task_id not in SINGLE_CHOICE_TASKS:
                    self._json(
                        400,
                        {
                            "error": (
                                f"当前在线批量评测仅支持单选任务: {', '.join(sorted(SINGLE_CHOICE_TASKS))}。"
                            )
                        },
                    )
                    return

                examples = load_examples(task_id, shot)[:max_samples]
                predictions: dict[str, Any] = {}
                results: list[dict[str, Any]] = []
                correct_count = 0
                abstentions = 0

                for index, example in enumerate(examples):
                    prompt = prompt_from_example(example)
                    raw_output = deepseek_chat(prompt, model, timeout=timeout)
                    prediction = normalize_choice_prediction(raw_output)
                    answer = str(example.get("answer", ""))
                    answer_letter = extract_answer_letter(answer)
                    score, abstention = score_single_choice(prediction, answer_letter)
                    correct = bool(score)

                    predictions[str(index)] = {
                        "origin_prompt": [{"role": "HUMAN", "prompt": prompt}],
                        "prediction": prediction,
                        "raw_prediction": raw_output,
                        "refr": answer,
                        "correct": correct,
                    }
                    results.append(
                        {
                            "index": index,
                            "gold": answer,
                            "gold_choice": answer_letter,
                            "prediction": prediction,
                            "correct": correct,
                            "raw_output": raw_output,
                        }
                    )
                    correct_count += int(correct)
                    abstentions += abstention
                    time.sleep(0.2)

                timestamp = time.strftime("%Y%m%d-%H%M%S")
                run_id = f"{task_id}-{shot}-{model.replace('/', '-')}-{timestamp}"
                accuracy = round(correct_count / len(results), 4) if results else 0.0
                abstention_rate = round(abstentions / len(results), 4) if results else 0.0
                prediction_path = save_official_predictions(task_id, shot, model, predictions)
                run_payload = {
                    "run_id": run_id,
                    "task_id": task_id,
                    "task_name_zh": TASK_MAP[task_id]["name_zh"],
                    "shot": shot,
                    "model": model,
                    "sample_count": len(results),
                    "accuracy": accuracy,
                    "abstention_rate": abstention_rate,
                    "prediction_path": prediction_path,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "results": results,
                }
                saved_path = save_run(run_payload)
                self._json(200, {"run": run_payload, "saved_path": saved_path})
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
