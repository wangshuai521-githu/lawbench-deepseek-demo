from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent
DATA_ROOT = REPO_ROOT / "data"
PREDICTIONS_ROOT = REPO_ROOT / "predictions"

# Minimal first pass: support the official single-choice tasks so the correct
# LawBench pipeline can be rerun on the right benchmark immediately.
SINGLE_CHOICE_TASKS = {"1-2", "2-4", "2-8", "3-6"}
OPTION_LIST = ["A", "B", "C", "D"]


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


def deepseek_chat(prompt: str, model: str, timeout: int) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY environment variable.")

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
        raise RuntimeError(f"DeepSeek API error: {detail}") from exc
    return str(body["choices"][0]["message"]["content"])


def extract_answer_letter(answer: str) -> str:
    for option in OPTION_LIST:
        if option in answer:
            return option
    return ""


def normalize_prediction(text: str) -> str:
    value = text.strip()
    patterns = [
        r"\[正确答案\]\s*([A-D])\s*<eoa>",
        r"\[姝ｇ‘绛旀\]\s*([A-D])\s*<eoa>",
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


def multi_choice_score(prediction: str, answer_letter: str) -> tuple[int, int]:
    count_dict = {option: 1 if option in prediction else 0 for option in OPTION_LIST}
    if sum(count_dict.values()) == 0:
        return 0, 1
    if count_dict.get(answer_letter, 0) == 1 and sum(count_dict.values()) == 1:
        return 1, 0
    return 0, 0


def build_prompt(example: dict[str, str]) -> str:
    instruction = str(example.get("instruction", "")).strip()
    question = str(example.get("question", "")).strip()
    return f"{instruction}\n\n{question}".strip()


def ensure_supported(task_id: str) -> None:
    if task_id not in SINGLE_CHOICE_TASKS:
        supported = ", ".join(sorted(SINGLE_CHOICE_TASKS))
        raise RuntimeError(
            f"Current minimal runner only supports single-choice tasks: {supported}. "
            f"Requested: {task_id}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="1-2")
    parser.add_argument("--shot", choices=["zero_shot", "one_shot"], default="zero_shot")
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--max-samples", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    ensure_supported(args.task)

    data_path = DATA_ROOT / args.shot / f"{args.task}.json"
    if not data_path.exists():
        raise RuntimeError(f"Dataset not found: {data_path}")

    examples = read_json(data_path)
    if args.max_samples > 0:
        examples = examples[: args.max_samples]

    model_dir = Path(args.output_dir) if args.output_dir else PREDICTIONS_ROOT / args.shot / args.model
    model_dir.mkdir(parents=True, exist_ok=True)
    output_path = model_dir / f"{args.task}.json"

    results: dict[str, Any] = {}
    score_sum = 0
    abstentions = 0

    for idx, example in enumerate(examples):
        prompt = build_prompt(example)
        raw_output = deepseek_chat(prompt, args.model, args.timeout)
        prediction = normalize_prediction(raw_output)
        answer = str(example.get("answer", ""))
        answer_letter = extract_answer_letter(answer)
        score, abstention = multi_choice_score(prediction, answer_letter)
        score_sum += score
        abstentions += abstention

        results[str(idx)] = {
            "origin_prompt": [{"role": "HUMAN", "prompt": prompt}],
            "prediction": prediction,
            "raw_prediction": raw_output,
            "refr": answer,
            "correct": bool(score),
        }

        print(
            f"[{idx + 1}/{len(examples)}] gold={answer_letter} pred={prediction} "
            f"correct={bool(score)}"
        )
        if args.sleep > 0:
            time.sleep(args.sleep)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    accuracy = score_sum / len(examples) if examples else 0.0
    abstention_rate = abstentions / len(examples) if examples else 0.0

    print()
    print(f"Task: {args.task}")
    print(f"Shot: {args.shot}")
    print(f"Model: {args.model}")
    print(f"Samples: {len(examples)}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Abstention rate: {abstention_rate:.4f}")
    print(f"Saved predictions to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
