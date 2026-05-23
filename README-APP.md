# 交互式应用说明

这个目录把前面的 benchmark 工作流扩展成了一个可以交互演示的 Web 应用。

## 当前新增内容

- 数据集到界面的设计说明：
  - `docs/frontend-backend-design.md`
- Python 后端：
  - `backend/server.py`
- 浏览器前端：
  - `webapp/index.html`
  - `webapp/styles.css`
  - `webapp/app.js`

## 交互流程

1. 前端从 `/api/tasks` 加载任务列表
2. 用户选择任务和数据划分
3. 前端请求：
   - 任务说明
   - Prompt 模板
   - 样本预览
4. 用户可以：
   - 运行单条样本
   - 执行批量评测
5. 后端调用 DeepSeek 并返回预测结果
6. 批量评测结果会保存到 `legalbench-main\outputs`

## 为什么这样设计

LegalBench 天然就是“任务目录 + Prompt 模板 + 表格数据”的结构，所以前端非常适合围绕下面这些对象展开：

- 任务浏览
- Prompt 查看
- 样本级交互
- 批量 benchmark 运行
- 历史结果回看

## 本地运行

要求本机已安装 Python。

Example:

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
$env:DEEPSEEK_API_KEY="your_api_key_here"
python .\backend\server.py
```

Then open:

`http://127.0.0.1:8787`

## 现在为什么先不用 Vue 或 React

推荐顺序：

1. 先用原生 HTML + JS
2. 先把后端交互跑通
3. 等数据流稳定后，再升级到 React 或 Vue

这才是这个项目合理的工程顺序。

## 准备部署

现在后端已经支持部署模式：

- 通过 `APP_ROOT` 指定项目根目录
- 通过 `HOST` 指定监听地址
- 通过 `PORT` 指定监听端口

例如在云平台上通常使用：

```powershell
$env:HOST="0.0.0.0"
$env:PORT="8787"
python .\backend\server.py
```

如果你准备部署到公网，优先看：

- `DEPLOY-RENDER.md`
