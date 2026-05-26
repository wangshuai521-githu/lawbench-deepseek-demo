const { createApp, computed } = Vue;

function formatError(error) {
  if (error && typeof error === "object") {
    return error.error || error.detail || JSON.stringify(error, null, 2);
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
        this.resultText = [
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
        await this.loadRuns();
        this.setStatus(`批量评测完成。准确率 ${data.run.accuracy}，结果已写入 predictions 与 outputs 目录。`);
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
