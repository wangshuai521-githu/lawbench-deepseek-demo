# Render 部署说明（LawBench 版）

## 1. 这个部署有什么用

部署到 Render 之后，你的项目会得到一个公网网址。

这意味着：

- 你不需要只在自己电脑上展示
- HR 或面试官可以直接打开网页看你的项目
- 你可以把“数据集设计 + 前后端交互 + 模型评测”作为完整作品对外展示

## 2. 当前项目适合怎么部署

这个项目已经包含：

- `render.yaml`
- `backend/server.py`
- `webapp/`

也就是说，当前结构已经是可以往 Render 推的。

Render 上只需要做两件事：

1. 连接你的 GitHub 仓库
2. 配置 `DEEPSEEK_API_KEY`

## 3. GitHub 仓库准备建议

仓库名建议：

- `lawbench-deepseek-demo`
- 或 `lawbench-chinese-legal-benchmark-demo`

推荐第一个，短、清楚、方便展示。

## 4. Render 创建服务时怎么填

如果你用的是 `render.yaml` 自动识别，通常不需要手动填写太多内容。

关键项：

- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `python backend/server.py`

环境变量：

- `DEEPSEEK_API_KEY=你的key`
- `HOST=0.0.0.0`
- `APP_ROOT=/opt/render/project/src`

## 5. 部署成功后怎么展示

建议你把展示逻辑分成三段：

1. 先讲 LawBench 是什么
2. 再讲你怎么把它做成前后端可交互系统
3. 最后现场点一个任务，运行单条样本或批量样本

## 6. 线上演示时要提前注意

因为这个项目会真实调用 DeepSeek API，所以：

- 线上调用会消耗 API 配额
- 不建议一次性跑太多样本
- 面试演示时建议批量样本数控制在 `3` 到 `5`

## 7. 推荐上线后的页面展示重点

优先让别人看到：

- 20 个任务总览
- 数据集设计说明
- 任务详情
- 样本预览
- 单条推理结果
- 历史评测记录

这样比单纯展示“模型答了一题”更能体现你的工程能力。
