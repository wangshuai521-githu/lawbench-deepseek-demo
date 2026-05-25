# LawBench x DeepSeek 中文法律评测演示平台

基于 `open-compass/LawBench` 搭建的中文法律大模型评测演示系统，支持：

- LawBench 任务目录与数据集设计可视化
- DeepSeek 模型接入
- 单条样本在线推理
- 小批量自动评测
- 历史结果保存
- 腾讯云 CloudBase 云托管公网部署

这个项目的目标不是“跑一个 benchmark 脚本”，而是把中文法律 benchmark 做成一个可交互、可展示、可部署的工程化作品。

## 项目亮点

- 选题聚焦中文法律场景，基于 `LawBench` 而不是通用聊天数据。
- 不只展示静态结果，而是把前端、后端、模型调用和评测流程打通。
- 页面可以同时展示任务总览、数据集设计、样本结构、Prompt 逻辑、运行结果和历史记录。
- 对单选题任务做了输出归一化和自动打分，形成稳定的在线评测闭环。
- 项目已经完成云端部署，具备求职作品集展示能力。

## 功能概览

### 数据与任务展示

- 展示 20 个 LawBench 任务
- 展示 3 个认知层级分布
- 展示任务来源、指标、任务类型
- 展示 `zero_shot` / `one_shot` Prompt 设置

### 在线运行能力

- 单条样本推理
- 小批量评测
- 历史结果保存

当前在线自动评测优先支持单选题任务：

- `1-2`
- `2-4`
- `2-8`
- `3-6`

原因是这类任务可以稳定把模型输出归一化为 `A/B/C/D`，自动评分最稳。

## 技术方案

### 数据层

- 基于 `open-compass/LawBench` 官方数据组织任务目录
- 提取任务级、样本级、运行级三层结构

### 后端层

- 使用 Python 标准库实现轻量 HTTP 服务
- 读取 LawBench JSON 数据
- 组织 Prompt
- 调用 DeepSeek API
- 对单选题做自动评分

### 前端层

- 中文单页展示界面
- 展示任务总览、样本预览、Prompt 结构、运行结果、历史记录

### 部署层

- 使用 `Dockerfile` 容器化
- 推送 GitHub 仓库
- 部署到腾讯云 CloudBase 云托管

## 项目结构

- `backend/server.py`
  中文后端 API，负责数据读取、推理调用、批量评测和结果保存
- `webapp/`
  中文前端页面
- `lawbench-opencompass/`
  LawBench 官方仓库代码与数据
- `docs/frontend-backend-design.md`
  数据集设计与前后端映射说明
- `docs/job-showcase-lawbench.md`
  求职展示稿、面试讲解稿
- `DEPLOY-CLOUDBASE-LAWBENCH.md`
  腾讯云 CloudBase 部署说明
- `Dockerfile`
  云托管部署使用的容器化配置

## 本地运行

先在 PowerShell 中设置：

```powershell
$env:DEEPSEEK_API_KEY="你的 key"
```

然后启动后端：

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
& "D:\Program Files\IBM\SPSS\Statistics\27\Python3\python.exe" .\backend\server.py
```

浏览器访问：

```text
http://127.0.0.1:8787
```

## 命令行运行示例

```powershell
.\run-lawbench-deepseek.ps1 -TaskId 1-2 -Shot zero_shot -Model deepseek-v4-flash -MaxSamples 5
```

## 云端部署

项目当前已适配腾讯云 CloudBase 云托管，部署方式见：

- [DEPLOY-CLOUDBASE-LAWBENCH.md](DEPLOY-CLOUDBASE-LAWBENCH.md)

部署前至少需要配置：

- `DEEPSEEK_API_KEY`
- `APP_ROOT=/app`
- `HOST=0.0.0.0`

## 求职展示建议

如果你是从求职作品集角度看这个项目，建议重点展示这四件事：

1. 你选的是中文法律 benchmark，而不是普通通用问答 demo。
2. 你把 benchmark 做成了前后端可交互系统，而不是离线脚本。
3. 你完成了模型接入、评测归一化、自动评分和结果保存。
4. 你已经把项目部署到了云端，形成公网可访问作品。

更完整的求职讲解稿见：

- [docs/job-showcase-lawbench.md](docs/job-showcase-lawbench.md)
