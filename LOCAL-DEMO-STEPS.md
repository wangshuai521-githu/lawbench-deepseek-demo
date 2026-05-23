# 本地演示最短步骤

## 方式一：直接查看结果

直接打开：

`dashboard\index.html`

这是离线结果展示页，不需要启动后端。

## 方式二：交互演示

1. 打开 PowerShell
2. 进入项目目录：

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
```

3. 设置 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY="你的DeepSeek API Key"
```

4. 启动后端：

```powershell
python .\backend\server.py
```

5. 浏览器打开：

`http://127.0.0.1:8787`

## 推荐演示顺序

1. 先展示 `任务说明`
2. 再展示 `这个数据集是怎么组织的`
3. 再展示 `评测流程说明`
4. 运行单条样本
5. 最后展示批量评测结果和历史记录
