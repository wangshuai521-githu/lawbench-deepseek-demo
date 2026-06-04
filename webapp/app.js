const { createApp, computed } = Vue;

function formatError(error) {
  if (!error) {
    return "发生未知错误。";
  }
  if (error instanceof Error) {
    return error.message || String(error);
  }
  if (error && typeof error === "object") {
    return error.error || error.detail || error.message || JSON.stringify(error, null, 2);
  }
  return String(error);
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
      statusText: "正在初始化 FastAPI + Vue3 演示平台...",
      resultText: "暂未运行。",
      resultMode: "待命",
      emptyDoc: "<p class='empty-copy'>暂无说明文档。</p>",
    };
  },
  computed: {
    promptSettingsText() {
      return (this.overview?.prompt_settings || []).join(" / ") || "-";
    },
    levelEntries() {
      return Object.entries(this.overview?.levels || {}).map(([name, count]) => ({ name, count }));
    },
    batchSupportText() {
      if (!this.selectedTask) {
        return "在线批量评测当前优先支持单选题任务：1-2、2-4、2-8、3-6。";
      }
      return this.selectedTask.online_batch
        ? `当前任务 ${this.selectedTask.task_id} 支持在线批量自动评分。`
        : `当前任务 ${this.selectedTask.task_id} 属于 ${this.selectedTask.task_type} 任务，当前优先开放单条推理展示。`;
    },
    orderedRuns() {
      return this.runs.slice().reverse();
    },
    resultModeLabel() {
      return this.resultMode;
    },
  },
  methods: {
    setStatus(text) {
      this.statusText = text;
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
      lines.push("当前页面已经直接展示了逐题结果，也可以点击下方“批量评测记录”再次查看历史明细。");

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
    },
    async refreshTaskView() {
      try {
        this.busy = true;
        await this.loadTaskDetail();
        await this.loadSamples();
        this.setStatus(`已加载任务 ${this.selectedTaskId}，当前可查看样本、运行单条推理或发起批量评测。`);
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
        await this.loadRuns();
        this.setStatus(`批量评测完成。准确率 ${data.run.accuracy}，逐题结果已在右侧结果区展示。`);
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
