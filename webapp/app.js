const state = {
  overview: null,
  tasks: [],
  selectedTaskId: "",
  selectedTask: null,
  samples: [],
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function apiGet(url) {
  const response = await fetch(url);
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { error: text };
  }
  if (!response.ok) {
    throw new Error(data.error || text || "请求失败");
  }
  return data;
}

async function apiPost(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function setStatus(text) {
  document.getElementById("statusBox").textContent = text;
}

function renderStats() {
  if (!state.overview) return;
  const levels = Object.entries(state.overview.levels || {})
    .map(([name, count]) => `<div class="kv-row"><span>${escapeHtml(name)}</span><strong>${count}</strong></div>`)
    .join("");
  document.getElementById("statsGrid").innerHTML = `
    <article class="stat-card">
      <div class="stat-label">任务数</div>
      <div class="stat-value">${state.overview.task_count}</div>
      <div class="stat-note">覆盖 3 个司法认知层级</div>
    </article>
    <article class="stat-card">
      <div class="stat-label">每任务样本数</div>
      <div class="stat-value">${state.overview.examples_per_task}</div>
      <div class="stat-note">官方仓库每个任务统一为 500 条</div>
    </article>
    <article class="stat-card">
      <div class="stat-label">Prompt 设置</div>
      <div class="stat-value">${state.overview.prompt_settings.join(" / ")}</div>
      <div class="stat-note">同一任务支持 zero-shot 与 one-shot</div>
    </article>
    <article class="stat-card">
      <div class="stat-label">认知层级分布</div>
      <div class="stat-stack">${levels}</div>
    </article>
  `;
}

function renderTaskCatalog() {
  const host = document.getElementById("taskCatalogTable");
  host.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>中文任务名</th>
          <th>认知层级</th>
          <th>指标</th>
          <th>类型</th>
          <th>在线批量</th>
        </tr>
      </thead>
      <tbody>
        ${state.tasks.map((task) => `
          <tr data-task-id="${escapeHtml(task.task_id)}">
            <td>${escapeHtml(task.task_id)}</td>
            <td>${escapeHtml(task.name_zh)}</td>
            <td>${escapeHtml(task.level)}</td>
            <td>${escapeHtml(task.metric)}</td>
            <td>${escapeHtml(task.task_type)}</td>
            <td>${task.online_batch ? "支持" : "暂不支持"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderRuns(runs) {
  const host = document.getElementById("runsTable");
  if (!runs.length) {
    host.innerHTML = "<p class='empty'>还没有保存的批量评测记录。</p>";
    return;
  }
  host.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>时间</th>
          <th>任务</th>
          <th>Prompt 设置</th>
          <th>模型</th>
          <th>样本数</th>
          <th>准确率</th>
          <th>弃权率</th>
        </tr>
      </thead>
      <tbody>
        ${runs.slice().reverse().map((run) => `
          <tr>
            <td>${escapeHtml(run.created_at || "-")}</td>
            <td>${escapeHtml(run.task_id || "-")} ${escapeHtml(run.task_name_zh || "")}</td>
            <td>${escapeHtml(run.shot || "-")}</td>
            <td>${escapeHtml(run.model || "-")}</td>
            <td>${escapeHtml(run.sample_count ?? "-")}</td>
            <td>${escapeHtml(run.accuracy ?? "-")}</td>
            <td>${escapeHtml(run.abstention_rate ?? "-")}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderSamples(rows) {
  const host = document.getElementById("samplesTable");
  if (!rows.length) {
    host.innerHTML = "<p class='empty'>当前任务暂无样本预览。</p>";
    return;
  }
  host.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>索引</th>
          <th>instruction</th>
          <th>question</th>
          <th>answer</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td>${row.index}</td>
            <td>${escapeHtml(row.instruction).slice(0, 90)}</td>
            <td>${escapeHtml(row.question).slice(0, 200)}</td>
            <td>${escapeHtml(row.answer).slice(0, 60)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function applyTaskOptions() {
  const select = document.getElementById("taskSelect");
  select.innerHTML = state.tasks
    .map((task) => `<option value="${escapeHtml(task.task_id)}">${escapeHtml(task.task_id)} - ${escapeHtml(task.name_zh)}</option>`)
    .join("");
  if (!state.selectedTaskId && state.tasks.length) {
    state.selectedTaskId = state.tasks[0].task_id;
  }
  select.value = state.selectedTaskId;
}

function refreshBatchNote() {
  const note = document.getElementById("batchSupportNote");
  if (!state.selectedTask) {
    note.textContent = "批量评测支持单选题任务：1-2、2-4、2-8、3-6";
    return;
  }
  note.textContent = state.selectedTask.online_batch
    ? `当前任务 ${state.selectedTask.task_id} 支持在线批量自动评分。`
    : `当前任务 ${state.selectedTask.task_id} 属于 ${state.selectedTask.task_type} 任务，页面支持单条交互推理，批量自动评分暂未开放。`;
}

async function loadOverview() {
  state.overview = await apiGet("/api/overview");
  document.getElementById("heroSubtitle").textContent = state.overview.subtitle;
  document.getElementById("heroBadge").textContent = `${state.overview.task_count} tasks`;
  document.getElementById("designDoc").innerHTML = state.overview.design_doc_html || "<p class='empty'>暂无设计文档。</p>";
  renderStats();
}

async function loadTasks() {
  const data = await apiGet("/api/tasks");
  state.tasks = data.tasks || [];
  state.selectedTaskId = state.selectedTaskId || state.tasks[0]?.task_id || "";
  applyTaskOptions();
  renderTaskCatalog();
}

async function loadTaskDetail() {
  state.selectedTaskId = document.getElementById("taskSelect").value;
  const detail = await apiGet(`/api/tasks/${state.selectedTaskId}`);
  state.selectedTask = detail;
  document.getElementById("taskTitle").textContent = `${detail.task_id} ${detail.name_zh}`;
  document.getElementById("taskTag").textContent = `${detail.metric} / ${detail.task_type}`;
  document.getElementById("taskDescription").innerHTML = detail.description_html;
  document.getElementById("promptSchema").textContent = `Prompt 结构：${detail.prompt_schema}`;
  document.getElementById("promptPreview").textContent = detail.prompt_preview;
  refreshBatchNote();
}

async function loadSamples() {
  const shot = document.getElementById("shotSelect").value;
  const limit = Number(document.getElementById("sampleLimitInput").value || "6");
  const data = await apiGet(`/api/tasks/${state.selectedTaskId}/samples?shot=${encodeURIComponent(shot)}&limit=${limit}`);
  state.samples = data.rows || [];
  renderSamples(state.samples);
}

async function loadRuns() {
  const data = await apiGet("/api/runs");
  renderRuns(data.runs || []);
}

async function refreshTaskView() {
  await loadTaskDetail();
  await loadSamples();
  setStatus(`已加载任务 ${state.selectedTaskId}，可以继续查看样本或发起推理。`);
}

async function runSample() {
  const taskId = document.getElementById("taskSelect").value;
  const shot = document.getElementById("shotSelect").value;
  const model = document.getElementById("modelInput").value.trim();
  const sampleIndex = Number(document.getElementById("sampleIndexInput").value || "0");
  setStatus(`正在运行单条样本：任务 ${taskId}，索引 ${sampleIndex}，模型 ${model}。`);
  const data = await apiPost("/api/run-sample", {
    task_id: taskId,
    shot,
    model,
    sample_index: sampleIndex,
  });
  document.getElementById("resultBox").textContent = [
    `任务: ${data.task_id}`,
    `Prompt 设置: ${data.shot}`,
    `模型: ${data.model}`,
    `样本索引: ${data.sample_index}`,
    `标准答案: ${data.gold}`,
    `抽取后的预测: ${data.prediction}`,
    `是否正确: ${data.correct === null ? "当前任务未做自动评分" : data.correct}`,
    "",
    "模型原始输出：",
    data.raw_output,
    "",
    "发送给模型的 Prompt：",
    data.prompt,
  ].join("\n");
  setStatus(`单条样本运行完成。预测结果：${data.prediction}`);
}

async function runBatch() {
  const taskId = document.getElementById("taskSelect").value;
  const shot = document.getElementById("shotSelect").value;
  const model = document.getElementById("modelInput").value.trim();
  const maxSamples = Number(document.getElementById("batchSizeInput").value || "5");
  const timeout = Number(document.getElementById("timeoutInput").value || "120");
  setStatus(`正在执行批量评测：任务 ${taskId}，样本数 ${maxSamples}，模型 ${model}。`);
  const data = await apiPost("/api/run-batch", {
    task_id: taskId,
    shot,
    model,
    max_samples: maxSamples,
    timeout,
  });
  document.getElementById("resultBox").textContent = [
    `运行 ID: ${data.run.run_id}`,
    `任务: ${data.run.task_id} ${data.run.task_name_zh}`,
    `Prompt 设置: ${data.run.shot}`,
    `模型: ${data.run.model}`,
    `样本数: ${data.run.sample_count}`,
    `准确率: ${data.run.accuracy}`,
    `弃权率: ${data.run.abstention_rate}`,
    `官方预测文件: ${data.run.prediction_path}`,
    `应用运行记录: ${data.saved_path}`,
  ].join("\n");
  await loadRuns();
  setStatus(`批量评测完成。准确率 ${data.run.accuracy}，结果已写入官方 predictions 目录与应用 outputs 目录。`);
}

async function main() {
  try {
    await loadOverview();
    await loadTasks();
    await refreshTaskView();
    await loadRuns();

    document.getElementById("taskSelect").addEventListener("change", refreshTaskView);
    document.getElementById("shotSelect").addEventListener("change", loadSamples);
    document.getElementById("refreshTaskBtn").addEventListener("click", refreshTaskView);
    document.getElementById("runSampleBtn").addEventListener("click", runSample);
    document.getElementById("runBatchBtn").addEventListener("click", runBatch);
  } catch (error) {
    setStatus(String(error));
  }
}

main();
