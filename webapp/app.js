const state = {
  tasks: [],
  selectedTask: null,
  taskMeta: null,
  sampleRows: [],
};

async function apiGet(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

async function apiPost(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

function setStatus(text) {
  document.getElementById("statusBox").textContent = text;
}

function renderRuns(runs) {
  const host = document.getElementById("runsTable");
  if (!runs.length) {
    host.innerHTML = "<p>暂无已保存的评测记录。</p>";
    return;
  }
  host.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>任务</th>
          <th>划分</th>
          <th>模型</th>
          <th>准确率</th>
        </tr>
      </thead>
      <tbody>
        ${runs.slice().reverse().map(run => `
          <tr>
            <td>${run.task || run.task_name || "-"}</td>
            <td>${run.split || "-"}</td>
            <td>${run.model || "-"}</td>
            <td>${run.accuracy ?? "-"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderSamples(rows) {
  const host = document.getElementById("samplesTable");
  if (!rows.length) {
    host.innerHTML = "<p>当前没有可展示样本。</p>";
    return;
  }
  const columns = Object.keys(rows[0]);
  host.innerHTML = `
    <table>
      <thead>
        <tr>${columns.map(col => `<th>${col}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows.map(row => `
          <tr>${columns.map(col => `<td>${(row[col] || "").slice(0, 180)}</td>`).join("")}</tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function loadRuns() {
  const data = await apiGet("/api/runs");
  renderRuns(data.runs || []);
}

async function loadTaskList() {
  const data = await apiGet("/api/tasks");
  state.tasks = data.tasks || [];
  const select = document.getElementById("taskSelect");
  select.innerHTML = state.tasks.map(task => `<option value="${task.task_name}">${task.task_name}</option>`).join("");
  if (state.tasks.length) {
    select.value = state.tasks[0].task_name;
    updateSplitOptions();
  }
}

function updateSplitOptions() {
  const taskName = document.getElementById("taskSelect").value;
  const task = state.tasks.find(item => item.task_name === taskName);
  const splitSelect = document.getElementById("splitSelect");
  const options = [];
  if (task?.has_test) options.push("test");
  if (task?.has_train) options.push("train");
  splitSelect.innerHTML = options.map(opt => `<option value="${opt}">${opt}</option>`).join("");
  if (options.length) {
    splitSelect.value = options[0];
  }
}

async function loadTaskMeta() {
  const taskName = document.getElementById("taskSelect").value;
  const split = document.getElementById("splitSelect").value;
  const limit = document.getElementById("limitInput").value;
  state.selectedTask = taskName;

  const [meta, samples] = await Promise.all([
    apiGet(`/api/tasks/${taskName}`),
    apiGet(`/api/tasks/${taskName}/samples?split=${split}&limit=${limit}`),
  ]);

  state.taskMeta = meta;
  state.sampleRows = samples.rows || [];

  document.getElementById("taskTitle").textContent = taskName;
  document.getElementById("taskStats").textContent = `train ${meta.splits.train} / test ${meta.splits.test}`;
  document.getElementById("taskDescription").innerHTML = meta.description_html || "<p>暂无任务说明。</p>";
  document.getElementById("promptTemplate").textContent = meta.prompt_template || "暂无 Prompt 模板。";

  renderSamples(state.sampleRows);
  setStatus(`已加载任务：${taskName}`);
}

async function runSample() {
  const taskName = document.getElementById("taskSelect").value;
  const split = document.getElementById("splitSelect").value;
  const model = document.getElementById("modelInput").value;
  const rowIndex = Number(document.getElementById("rowIndexInput").value || "0");
  setStatus(`正在运行单条样本：任务 ${taskName}，索引 ${rowIndex}...`);
  const data = await apiPost("/api/run-sample", {
    task_name: taskName,
    split,
    model,
    row_index: rowIndex,
  });
  document.getElementById("sampleResult").textContent = [
    `任务: ${data.task_name}`,
    `数据划分: ${data.split}`,
    `样本索引: ${data.row_index}`,
    `标准答案: ${data.gold}`,
    `模型预测: ${data.prediction}`,
    "",
    "模型原始输出:",
    data.raw_output,
    "",
    "生成的 Prompt:",
    data.prompt,
  ].join("\n");
  setStatus(`单条样本运行完成，预测结果：${data.prediction}`);
}

async function runBatch() {
  const taskName = document.getElementById("taskSelect").value;
  const split = document.getElementById("splitSelect").value;
  const model = document.getElementById("modelInput").value;
  const maxSamples = Number(document.getElementById("limitInput").value || "10");
  setStatus(`正在执行批量评测：任务 ${taskName}，样本数 ${maxSamples}...`);
  const data = await apiPost("/api/run-batch", {
    task_name: taskName,
    split,
    model,
    max_samples: maxSamples,
  });
  document.getElementById("sampleResult").textContent = [
    `任务: ${data.run.task}`,
    `数据划分: ${data.run.split}`,
    `模型: ${data.run.model}`,
    `样本数: ${data.run.sample_count}`,
    `准确率: ${data.run.accuracy}`,
    `保存路径: ${data.saved_path}`,
  ].join("\n");
  await loadRuns();
  setStatus(`批量评测完成，准确率：${data.run.accuracy}`);
}

async function main() {
  try {
    await loadTaskList();
    await loadTaskMeta();
    await loadRuns();
    document.getElementById("taskSelect").addEventListener("change", async () => {
      updateSplitOptions();
      await loadTaskMeta();
    });
    document.getElementById("splitSelect").addEventListener("change", loadTaskMeta);
    document.getElementById("loadTaskBtn").addEventListener("click", loadTaskMeta);
    document.getElementById("runSampleBtn").addEventListener("click", runSample);
    document.getElementById("runBatchBtn").addEventListener("click", runBatch);
  } catch (err) {
    setStatus(String(err));
  }
}

main();
