# LawBench 数据集设计说明

## 1. 数据来源

本项目基于 `open-compass/LawBench` 中文法律评测基准构建。

LawBench 面向中文法律场景，覆盖以下三类能力层级：

- 法律知识记忆
- 法律知识理解
- 法律知识应用

当前版本共接入 20 个任务，每个任务官方提供 500 条样本，并同时提供：

- `zero_shot`
- `one_shot`

两种 Prompt 配置。

## 2. 数据文件组织

项目按 Prompt 方式分别读取官方数据文件：

- `lawbench-opencompass/data/zero_shot/<task_id>.json`
- `lawbench-opencompass/data/one_shot/<task_id>.json`

单条样本统一包含以下字段：

- `instruction`
- `question`
- `answer`

这种组织方式使任务切换、样本预览和 Prompt 生成可以复用同一套处理逻辑。

## 3. 页面展示结构

为便于在线展示与评测，系统将 LawBench 数据抽象为三层：

### 任务层

用于展示任务目录与基础属性：

- `task_id`
- `name_zh`
- `name_en`
- `level`
- `metric`
- `task_type`
- `source`
- `online_batch`

### 样本层

用于展示样本内容与样本预览：

- `sample_index`
- `instruction`
- `question`
- `answer`

### 运行层

用于展示模型运行结果与历史记录：

- `run_id`
- `task_id`
- `shot`
- `model`
- `sample_count`
- `accuracy`
- `abstention_rate`
- `results`

## 4. Prompt 生成方式

当前版本直接基于官方样本字段生成输入内容，规则如下：

- `instruction + "\n\n" + question`

该方式与 LawBench 原始数据结构保持一致，便于定位样本来源、复现评测输入和展示页面中的 Prompt 结构。

## 5. 在线评测策略

LawBench 任务类型包含单选、多选、抽取、生成与回归。考虑到公网演示的稳定性，当前版本优先开放单选题任务的在线自动评测。

当前支持在线批量评测的任务为：

- `1-2`
- `2-4`
- `2-8`
- `3-6`

上述任务可将模型输出稳定归一化为 `A/B/C/D`，并与标准答案进行自动比对，形成可复现的评测闭环。

## 6. 工程处理流程

系统运行流程如下：

1. 后端读取 LawBench 官方 JSON 数据
2. 根据任务和 Prompt 配置生成输入内容
3. 调用 DeepSeek 模型完成推理
4. 对单选题输出进行结果归一化
5. 计算准确率并生成运行记录
6. 将结果写入预测文件与历史记录文件

输出结果保存位置包括：

- `lawbench-opencompass/predictions/...`
- `outputs/...`

## 7. 当前版本定位

本项目当前版本的定位是：

- 基于真实中文法律 benchmark 的在线演示系统
- 面向任务理解、样本展示、模型推理和自动评测的一体化前后端项目


后续可继续扩展，进一步接入更多任务类型的自动评测、数据库持久化和多模型横向对比能力（可接入其他模型进行评测）。
