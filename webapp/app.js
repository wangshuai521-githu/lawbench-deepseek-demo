const { createApp } = Vue;

function formatError(error) {
  if (!error) return "发生未知错误。";
  if (error instanceof Error) return error.message || String(error);
  if (error && typeof error === "object") {
    return error.error || error.detail || error.message || JSON.stringify(error, null, 2);
  }
  return String(error);
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { error: text };
  }

  if (!response.ok) {
    throw new Error(data.error || data.detail || text || "请求失败");
  }

  return data;
}

createApp({
  data() {
    return {
      overview: null,
      tasks: [],
      selectedTaskId: "",
      selectedTask: null,
      samples: [],
      runs: [],
      shot: "zero_shot",
      model: "deepseek-v4-flash",
      sampleIndex: 0,
      sampleLimit: 6,
      batchSize: 5,
      timeout: 120,
      busy: false,
      statusText: "正在初始化 LawBench 控制台...",
      resultText: "尚未运行。请选择任务后运行单条样本，或对支持的任务发起批量评测。",
      resultMode: "待命",
      emptyDoc: "<p class='empty-copy'>暂无说明文档。</p>",
      activeView: "overview",
      taskSearch: "",
      taskScope: "all",
      selectedRunId: "",
    };
  },
  computed: {
    views() {
      return [
        { id: "overview", label: "概览" },
        { id: "workspace", label: "工作区" },
        { id: "history", label: "历史" },
      ];
    },
    promptSettingsText() {
      return (this.overview?.prompt_settings || []).join(" / ") || "-";
    },
    levelEntries() {
      return Object.entries(this.overview?.levels || {}).map(([name, count]) => ({ name, count }));
    },
    levelMax() {
      return Math.max(...this.levelEntries.map((item) => item.count), 1);
    },
    levelBars() {
      return this.levelEntries.map((item) => ({
        ...item,
        percent: Math.max(10, Math.round((item.count / this.levelMax) * 100)),
      }));
    },
    taskTypeBuckets() {
      const buckets = new Map();
      for (const task of this.tasks) {
        const key = task.task_type || "未知类型";
        buckets.set(key, (buckets.get(key) || 0) + 1);
      }
      return Array.from(buckets, ([name, count]) => ({ name, count }));
    },
    taskTypeMax() {
      return Math.max(...this.taskTypeBuckets.map((item) => item.count), 1);
    },
    filteredTasks() {
      const keyword = normalizeText(this.taskSearch);
      return this.tasks.filter((task) => {
        const matchesSearch =
          !keyword ||
          normalizeText(
            `${task.task_id} ${task.name_zh} ${task.level} ${task.metric} ${task.task_type} ${task.prompt_schema}`,
          ).includes(keyword);
        const matchesScope =
          this.taskScope === "all"
            ? true
            : this.taskScope === "online"
              ? Boolean(task.online_batch)
              : !task.online_batch;
        return matchesSearch && matchesScope;
      });
    },
    filteredTaskCount() {
      return this.filteredTasks.length;
    },
    onlineTaskCount() {
      return this.tasks.filter((task) => task.online_batch).length;
    },
    offlineTaskCount() {
      return Math.max(this.tasks.length - this.onlineTaskCount, 0);
    },
    selectedTaskIndex() {
      const index = this.tasks.findIndex((task) => task.task_id === this.selectedTaskId);
      return index >= 0 ? index + 1 : 0;
    },
    selectedTaskSummary() {
      if (!this.selectedTask) {
        return [];
      }
      return [
        { label: "任务编号", value: this.selectedTask.task_id },
        { label: "任务类型", value: this.selectedTask.task_type },
        { label: "评测指标", value: this.selectedTask.metric },
        { label: "认知层级", value: this.selectedTask.level },
        { label: "模式", value: this.selectedTask.online_batch ? "在线评分" : "浏览为主" },
      ];
    },
    taskMetaLine() {
      if (!this.selectedTask) return "-";
      return `${this.selectedTask.level} · ${this.selectedTask.metric} · ${this.selectedTask.task_type}`;
    },
    currentViewLabel() {
      return this.views.find((view) => view.id === this.activeView)?.label || "概览";
    },
    orderedRuns() {
      return this.runs.slice().reverse();
    },
    recentRuns() {
      return this.orderedRuns.slice(0, 3);
    },
    selectedRun() {
      return this.runs.find((run) => run.run_id === this.selectedRunId) || this.orderedRuns[0] || null;
    },
    selectedRunResults() {
      return this.selectedRun?.results || [];
    },
    resultModeLabel() {
      return this.resultMode;
    },
  },
  methods: {
    setStatus(text) {
      this.statusText = text;
    },
    levelWidth(count) {
      return `${Math.max(10, Math.round((count / this.levelMax) * 100))}%`;
    },
    taskCardLabel(task) {
      return task.online_batch ? "可评分" : "可浏览";
    },
    selectView(viewId) {
      this.activeView = viewId;
      if (viewId === "history" && !this.selectedRunId && this.orderedRuns.length) {
        this.selectedRunId = this.orderedRuns[0].run_id;
      }
    },
    focusRun(runId) {
      this.selectedRunId = runId;
      this.activeView = "history";
    },
    formatBatchResultText(run, savedPath = "") {
      const lines = [
        `运行 ID: ${run.run_id}`,
        `任务: ${run.task_id} ${run.task_name_zh}`,
        `Prompt 设置: ${run.shot}`,
        `模型: ${run.model}`,
        `样本数: ${run.sample_count}`,
        `准确率: ${run.accuracy}`,
        `弃权率: ${run.abstention_rate}`,
        `官方预测文件: ${run.prediction_path}`,
      ];

      if (savedPath || run.saved_path) {
        lines.push(`应用运行记录: ${savedPath || run.saved_path}`);
      }

      lines.push("");
      lines.push("逐题结果：");

      for (const item of run.results || []) {
        lines.push(
          `#${item.index} | 标准答案: ${item.gold_choice || item.gold} | 模型预测: ${item.prediction} | 是否正确: ${item.correct}`,
        );
      }

      lines.push("");
      lines.push("说明：上面的 /app/... 路径是云端容器内文件路径，公网浏览器不能直接打开。");
      lines.push("页面已经直接展示逐题结果，也可以在下方批量评测记录中再次查看历史明细。");

      return lines.join("\n");
    },
    async loadOverview() {
      this.overview = await fetchJson("/api/overview");
    },
    async loadTasks() {
      const data = await fetchJson("/api/tasks");
      this.tasks = data.tasks || [];
      if (!this.selectedTaskId && this.tasks.length) {
        this.selectedTaskId = this.tasks[0].task_id;
      }
    },
    async loadTaskDetail() {
      if (!this.selectedTaskId) return;
      this.selectedTask = await fetchJson(`/api/tasks/${this.selectedTaskId}`);
    },
    async loadSamples() {
      if (!this.selectedTaskId) return;
      const data = await fetchJson(
        `/api/tasks/${this.selectedTaskId}/samples?shot=${encodeURIComponent(this.shot)}&limit=${this.sampleLimit}`,
      );
      this.samples = data.rows || [];
    },
    async loadRuns() {
      const data = await fetchJson("/api/runs");
      this.runs = data.runs || [];
      if (!this.selectedRunId && this.orderedRuns.length) {
        this.selectedRunId = this.orderedRuns[0].run_id;
      }
    },
    async refreshTaskView() {
      try {
        this.busy = true;
        await this.loadTaskDetail();
        await this.loadSamples();
        this.setStatus(`已加载任务 ${this.selectedTaskId}，可以查看样本、运行单条推理或发起批量评测。`);
      } catch (error) {
        this.setStatus(formatError(error));
      } finally {
        this.busy = false;
      }
    },
    async selectTask(taskId) {
      this.selectedTaskId = taskId;
      await this.refreshTaskView();
    },
    async runSample() {
      try {
        this.busy = true;
        this.resultMode = "单条推理";
        this.setStatus(`正在运行单条样本：任务 ${this.selectedTaskId}，索引 ${this.sampleIndex}，模型 ${this.model}。`);
        const data = await fetchJson("/api/run-sample", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            task_id: this.selectedTaskId,
            shot: this.shot,
            model: this.model,
            sample_index: this.sampleIndex,
          }),
        });
        this.resultText = [
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
        this.setStatus(`单条样本运行完成。预测结果：${data.prediction}`);
      } catch (error) {
        this.resultText = formatError(error);
        this.setStatus(formatError(error));
      } finally {
        this.busy = false;
      }
    },
    async runBatch() {
      try {
        this.busy = true;
        this.resultMode = "批量评测";
        this.setStatus(`正在执行批量评测：任务 ${this.selectedTaskId}，样本数 ${this.batchSize}，模型 ${this.model}。`);
        const data = await fetchJson("/api/run-batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            task_id: this.selectedTaskId,
            shot: this.shot,
            model: this.model,
            max_samples: this.batchSize,
            timeout: this.timeout,
          }),
        });
        this.resultText = this.formatBatchResultText(data.run, data.saved_path);
        this.selectedRunId = data.run.run_id;
        this.activeView = "history";
        await this.loadRuns();
        this.setStatus(`批量评测完成。准确率 ${data.run.accuracy}，逐题结果已展示。`);
      } catch (error) {
        this.resultText = formatError(error);
        this.setStatus(formatError(error));
      } finally {
        this.busy = false;
      }
    },
    async showRunDetail(runId) {
      try {
        this.busy = true;
        this.resultMode = "历史记录";
        this.setStatus(`正在加载运行记录 ${runId} 的逐题结果。`);
        const run = await fetchJson(`/api/runs/${encodeURIComponent(runId)}`);
        this.selectedRunId = runId;
        this.resultText = this.formatBatchResultText(run);
        this.setStatus(`已加载运行记录 ${runId} 的逐题结果。`);
      } catch (error) {
        this.resultText = formatError(error);
        this.setStatus(formatError(error));
      } finally {
        this.busy = false;
      }
    },
    async bootstrap() {
      try {
        await this.loadOverview();
        await this.loadTasks();
        await this.refreshTaskView();
        await this.loadRuns();
      } catch (error) {
        this.setStatus(formatError(error));
      }
    },
  },
  mounted() {
    this.bootstrap();
  },
}).mount("#app");
