# LawBench 数据集设计与前后端映射

## 1. 数据集本体长什么样

这次项目使用的是 `open-compass/LawBench`，不是英文的 `LegalBench`。

LawBench 的核心特点：

- 基于中国法律体系
- 一共 20 个任务
- 覆盖 3 个司法认知层级
- 每个任务官方提供 500 条样本
- 每个任务同时提供 `zero_shot` 和 `one_shot` 两种 Prompt 设置

数据文件位于：

- `lawbench-opencompass/data/zero_shot/<task_id>.json`
- `lawbench-opencompass/data/one_shot/<task_id>.json`

每个 JSON 文件本质上是一个列表，每一条样本都包含：

- `instruction`
- `question`
- `answer`

## 2. 前端为什么适合展示它

LawBench 很适合做交互页面，因为它不是一堆散乱文本，而是天然具备结构化字段：

- 任务级信息：任务 ID、任务名、认知层级、指标、类型、数据来源
- 样本级信息：instruction、question、answer
- 运行级信息：模型、Prompt 设置、预测结果、准确率、弃权率

这意味着前端可以直接拆成三个展示维度：

- 数据集怎么设计
- 某个任务的数据样本长什么样
- 某个模型在这个任务上跑出来的结果怎么样

## 3. 这次项目的核心抽象

为了让页面和后端都能通用化，这个项目把 LawBench 抽象成了下面三层：

### 任务层

- `task_id`
- `name_zh`
- `name_en`
- `level`
- `metric`
- `task_type`
- `source`
- `online_batch`

### 样本层

- `instruction`
- `question`
- `answer`
- `sample_index`

### 运行层

- `run_id`
- `task_id`
- `shot`
- `model`
- `sample_count`
- `accuracy`
- `abstention_rate`
- `results`

## 4. Prompt 是怎么拼出来的

LawBench 这一版演示没有再额外寻找单独的 Prompt 模板文件，而是直接按照官方数据结构拼接：

- `instruction + "\n\n" + question`

这有两个好处：

- 和官方 JSON 数据格式完全对齐
- 前端也更容易把“数据集设计”讲清楚

也就是说，页面上展示出来的 Prompt，不是拍脑袋写的，而是从数据集字段直接生成的。

## 5. 为什么在线批量评测先支持单选题

LawBench 20 个任务里既有：

- 单选题
- 多选题
- 抽取题
- 生成题
- 回归题

如果目标是先做一个稳定、能上线、能演示的系统，那么第一步应该优先支持自动评分最稳定的任务类型，也就是单选题。

所以当前在线批量评测先支持：

- `1-2`
- `2-4`
- `2-8`
- `3-6`

这些任务都可以直接把模型输出归一化为 `A/B/C/D`，再和标准答案做自动比对。

## 6. 这套前后端是怎么配合的

前端负责：

- 展示 LawBench 总体设计
- 展示 20 个任务目录化后的结构信息
- 预览样本
- 发起单条推理和批量评测
- 展示历史运行结果

后端负责：

- 读取 LawBench 官方 JSON 数据
- 生成 Prompt
- 调用 DeepSeek API
- 对单选题做自动评分
- 把结果写回：

  - `lawbench-opencompass/predictions/...`
  - `outputs/...`

## 7. 为什么这个项目适合面试展示

因为它不只是“我接了一个模型 API”。

它完整体现了下面四件事：

- 你能读懂一个真实开源 benchmark 的数据结构
- 你能把 benchmark 抽象成通用前后端对象
- 你能把模型调用、结果归一化和评测流程串起来
- 你能把工程做成别人可以直接看的交互界面
