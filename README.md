# LawBench x DeepSeek 中文法律评测演示平台

这个项目基于正确的仓库 `open-compass/LawBench` 搭建，目标不是只跑一个脚本，而是把：

- 数据集设计
- DeepSeek 接入
- 单条推理
- 小批量评测
- 前端可视化展示

做成一套能本地演示、也能后续部署上线的完整 demo。

## 项目结构

- `lawbench-opencompass/`
  说明：官方 LawBench 仓库
- `lawbench-opencompass/run_deepseek_lawbench.py`
  说明：LawBench 专用 DeepSeek runner
- `run-lawbench-deepseek.ps1`
  说明：PowerShell 启动脚本
- `backend/server.py`
  说明：中文后端 API
- `webapp/`
  说明：中文前端页面
- `docs/frontend-backend-design.md`
  说明：数据集设计与系统设计说明
- `outputs/`
  说明：页面触发的批量评测运行记录

## 当前能力

### 已完成

- 正确切换到 `LawBench`
- 使用 DeepSeek 成功跑通 `1-2` 任务
- 页面可展示 20 个任务的设计信息
- 页面可预览 `zero_shot` / `one_shot` 样本
- 页面可发起单条推理
- 页面可对单选题执行小批量自动评分

### 当前在线批量评测支持的任务

- `1-2`
- `2-4`
- `2-8`
- `3-6`

原因很直接：这四个任务都是单选题，模型输出可以稳定归一化为 `A/B/C/D`，自动评分最稳。

## 本地运行

如果你的 PowerShell 里已经设置过：

```powershell
$env:DEEPSEEK_API_KEY="你的 key"
```

那么运行后端：

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
& "D:\Program Files\IBM\SPSS\Statistics\27\Python3\python.exe" .\backend\server.py
```

打开浏览器访问：

```text
http://127.0.0.1:8787
```

## 命令行跑一个官方任务

```powershell
.\run-lawbench-deepseek.ps1 -TaskId 1-2 -Shot zero_shot -Model deepseek-v4-flash -MaxSamples 5
```

## 页面里能展示什么

这个前端页面不是普通聊天页，而是围绕 benchmark 设计的：

- LawBench 总览
- 20 个任务目录表
- 数据集设计说明
- 单个任务的层级、指标、类型、来源
- 样本预览
- Prompt 结构预览
- 单条样本运行结果
- 历史评测记录

## 部署方向

这套项目后续可以部署到 Render 一类平台，形成公网可访问的演示链接。

部署前要注意两点：

1. 线上环境必须配置 `DEEPSEEK_API_KEY`
2. 线上 Python 运行时必须能直接启动 `backend/server.py`

当前仓库已经保留了 `render.yaml` 入口，后面可以继续沿这个方向上线。
