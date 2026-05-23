# LegalBench dataset design and app mapping

## 1. What the dataset looks like

Each LegalBench task is a folder under:

`legalbench-main\tasks\<task_name>\`

Typical files inside a task folder:

- `README.md`: task description, labels, and legal meaning
- `base_prompt.txt`: prompt template
- `train.tsv`: training split
- `test.tsv`: test split, if provided

## 2. Core abstraction

For app development, each task can be modeled as:

- `task_name`
- `task_title`
- `task_type`
- `prompt_template`
- `available_splits`
- `columns`
- `samples`

Each sample row can be modeled as:

- `index`
- `fields`: all dataset columns
- `answer`

Each benchmark run can be modeled as:

- `run_id`
- `task_name`
- `split`
- `model`
- `sample_count`
- `accuracy`
- `results`

Each prediction result can be modeled as:

- `index`
- `gold`
- `prediction`
- `correct`
- `raw_output`

## 3. Why this maps well to a frontend

Because LegalBench uses prompt templates plus tabular data, the frontend can support:

- choosing a task
- previewing the prompt template
- previewing sample rows
- running one sample interactively
- running a batch evaluation
- browsing saved benchmark runs

## 4. Recommended architecture

Frontend:

- plain HTML + CSS + JavaScript for the first version
- optional upgrade path: React or Vue later

Backend:

- Python HTTP server
- reads LegalBench files
- renders prompt templates
- calls DeepSeek API
- stores run artifacts as JSON

## 5. Suggested API design

- `GET /api/tasks`
  returns task list and metadata

- `GET /api/tasks/<task_name>`
  returns task README summary, prompt template, columns, split sizes

- `GET /api/tasks/<task_name>/samples?split=test&limit=20`
  returns sample rows for preview

- `POST /api/run-sample`
  input: task, split, row index, model
  output: prompt, gold answer, prediction, raw model output

- `POST /api/run-batch`
  input: task, split, model, max_samples
  output: run summary and saved file path

- `GET /api/runs`
  returns saved benchmark runs

- `GET /api/runs/<run_id>`
  returns one saved run in detail

## 6. Frontend page design

Page 1: task explorer

- task list
- task description
- prompt preview
- sample preview

Page 2: interactive evaluator

- choose task
- choose split
- choose model
- choose sample count
- run one sample or one batch

Page 3: results dashboard

- run history
- accuracy table
- per-sample result details

## 7. Why start with plain HTML instead of React/Vue

For this project stage, plain HTML is enough because:

- the data model is already the important part
- backend and prompt flow are the core engineering story
- it avoids spending time on build tooling too early

After the backend is stable, upgrading the UI to React or Vue is straightforward.
