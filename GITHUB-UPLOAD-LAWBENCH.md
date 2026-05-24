# GitHub 上传说明（LawBench 版）

## 1. 仓库名建议

建议直接用：

- `lawbench-deepseek-demo`

这个名字足够清楚，面试官一眼就能看出：

- 你做的是 LawBench
- 你接了 DeepSeek
- 这是一个可演示项目

## 2. 现在这个项目适合上传哪些内容

建议保留并上传：

- `backend/`
- `webapp/`
- `docs/`
- `lawbench-opencompass/`
- `README.md`
- `render.yaml`
- `run-lawbench-deepseek.ps1`
- `start-lawbench-demo.ps1`
- `DEPLOY-RENDER-LAWBENCH.md`

## 3. 不要上传什么

不要把你的密钥上传：

- 不要把 `DEEPSEEK_API_KEY` 写进代码
- 不要把带 key 的截图传到仓库

当前 `.gitignore` 已经忽略了本地运行输出和 DeepSeek 的部分预测目录。

## 4. 建议的上传命令

在 PowerShell 里进入项目目录后执行：

```powershell
& "D:\Program Files\Git\bin\git.exe" status
& "D:\Program Files\Git\bin\git.exe" add .
& "D:\Program Files\Git\bin\git.exe" commit -m "Build LawBench x DeepSeek Chinese demo"
```

然后把远程仓库地址换成你自己的 GitHub 仓库地址：

```powershell
& "D:\Program Files\Git\bin\git.exe" remote remove origin
& "D:\Program Files\Git\bin\git.exe" remote add origin https://github.com/你的用户名/lawbench-deepseek-demo.git
& "D:\Program Files\Git\bin\git.exe" push -u origin main
```

## 5. 上传后你可以怎么介绍

仓库介绍建议写成这一类：

> A Chinese legal benchmark demo built on open-compass/LawBench, integrated with DeepSeek API, supporting dataset exploration, single-sample inference, small-batch evaluation, and frontend visualization.

## 6. 仓库首页你要突出什么

最值得展示的是三件事：

1. 这是基于中文法律 benchmark 的项目，不是随便写的聊天页
2. 你把数据集设计、模型调用、评测流程和前端展示串起来了
3. 这套系统既能本地跑，也能往公网部署
