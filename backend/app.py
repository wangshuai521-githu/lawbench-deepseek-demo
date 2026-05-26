from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from . import server as legacy


WEB_ROOT = legacy.FRONTEND_ROOT


class RunSampleRequest(BaseModel):
    task_id: str
    shot: str = "zero_shot"
    sample_index: int = 0
    model: str = "deepseek-v4-flash"


class RunBatchRequest(BaseModel):
    task_id: str
    shot: str = "zero_shot"
    model: str = "deepseek-v4-flash"
    max_samples: int = Field(default=10, ge=1, le=100)
    timeout: int = Field(default=120, ge=30, le=300)


app = FastAPI(
    title="LawBench x DeepSeek API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


def error_response(exc: Exception, status_code: int = 500) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "traceback": traceback.format_exc()},
    )


def static_file(name: str, content_type: str) -> FileResponse:
    path = WEB_ROOT / name
    return FileResponse(path, media_type=content_type)


@app.get("/")
def index() -> FileResponse:
    return static_file("index.html", "text/html")


@app.get("/app.js")
def app_js() -> FileResponse:
    return static_file("app.js", "application/javascript")


@app.get("/styles.css")
def styles_css() -> FileResponse:
    return static_file("styles.css", "text/css")


@app.get("/api/overview", response_model=None)
def overview():
    try:
        return legacy.benchmark_overview()
    except Exception as exc:
        return error_response(exc)


@app.get("/api/tasks", response_model=None)
def tasks():
    try:
        return {"tasks": legacy.task_list_payload()}
    except Exception as exc:
        return error_response(exc)


@app.get("/api/tasks/{task_id}", response_model=None)
def task_detail(task_id: str):
    try:
        return legacy.task_detail_payload(task_id)
    except KeyError as exc:
        return error_response(exc, 404)
    except Exception as exc:
        return error_response(exc)


@app.get("/api/tasks/{task_id}/samples", response_model=None)
def task_samples(task_id: str, shot: str = "zero_shot", limit: int = 8):
    try:
        return {
            "task_id": task_id,
            "shot": shot,
            "rows": legacy.sample_rows_payload(task_id, shot, limit),
        }
    except Exception as exc:
        return error_response(exc)


@app.get("/api/runs", response_model=None)
def runs():
    return {"runs": legacy.read_runs()}


@app.get("/api/runs/{run_id}", response_model=None)
def run_detail(run_id: str):
    run = legacy.read_run(run_id)
    if run is None:
        return JSONResponse(status_code=404, content={"error": f"未找到运行记录: {run_id}"})
    return run


@app.post("/api/run-sample", response_model=None)
def run_sample(payload: RunSampleRequest):
    try:
        examples = legacy.load_examples(payload.task_id, payload.shot)
        example = examples[payload.sample_index]
        prompt = legacy.prompt_from_example(example)
        raw_output = legacy.deepseek_chat(prompt, payload.model)

        normalized_prediction = raw_output.strip()
        answer_letter = ""
        correct: Optional[bool] = None

        if payload.task_id in legacy.SINGLE_CHOICE_TASKS:
            answer_letter = legacy.extract_answer_letter(str(example.get("answer", "")))
            normalized_prediction = legacy.normalize_choice_prediction(raw_output)
            score, _ = legacy.score_single_choice(normalized_prediction, answer_letter)
            correct = bool(score)

        return {
            "task_id": payload.task_id,
            "shot": payload.shot,
            "sample_index": payload.sample_index,
            "model": payload.model,
            "gold": str(example.get("answer", "")),
            "gold_choice": answer_letter,
            "prediction": normalized_prediction,
            "correct": correct,
            "raw_output": raw_output,
            "prompt": prompt,
            "example": example,
        }
    except Exception as exc:
        return error_response(exc)


@app.post("/api/run-batch", response_model=None)
def run_batch(payload: RunBatchRequest):
    try:
        if payload.task_id not in legacy.SINGLE_CHOICE_TASKS:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"当前在线批量评测仅支持单选任务: {', '.join(sorted(legacy.SINGLE_CHOICE_TASKS))}。"
                },
            )

        examples = legacy.load_examples(payload.task_id, payload.shot)[: payload.max_samples]
        predictions: Dict[str, Any] = {}
        results: List[Dict[str, Any]] = []
        correct_count = 0
        abstentions = 0

        for index, example in enumerate(examples):
            prompt = legacy.prompt_from_example(example)
            raw_output = legacy.deepseek_chat(prompt, payload.model, timeout=payload.timeout)
            prediction = legacy.normalize_choice_prediction(raw_output)
            answer = str(example.get("answer", ""))
            answer_letter = legacy.extract_answer_letter(answer)
            score, abstention = legacy.score_single_choice(prediction, answer_letter)
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
            legacy.time.sleep(0.2)

        timestamp = legacy.time.strftime("%Y%m%d-%H%M%S")
        run_id = f"{payload.task_id}-{payload.shot}-{payload.model.replace('/', '-')}-{timestamp}"
        accuracy = round(correct_count / len(results), 4) if results else 0.0
        abstention_rate = round(abstentions / len(results), 4) if results else 0.0
        prediction_path = legacy.save_official_predictions(payload.task_id, payload.shot, payload.model, predictions)
        run_payload = {
            "run_id": run_id,
            "task_id": payload.task_id,
            "task_name_zh": legacy.TASK_MAP[payload.task_id]["name_zh"],
            "shot": payload.shot,
            "model": payload.model,
            "sample_count": len(results),
            "accuracy": accuracy,
            "abstention_rate": abstention_rate,
            "prediction_path": prediction_path,
            "created_at": legacy.time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
        }
        saved_path = legacy.save_run(run_payload)
        return {"run": run_payload, "saved_path": saved_path}
    except Exception as exc:
        return error_response(exc)


def main() -> int:
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8787"))
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
