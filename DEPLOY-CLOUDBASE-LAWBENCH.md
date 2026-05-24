# 腾讯云 CloudBase 部署说明

这份说明对应当前项目：

- GitHub 仓库：`wangshuai521-githu/lawbench-deepseek-demo`
- 后端入口：`backend/server.py`
- 前端目录：`webapp/`
- 数据集目录：`lawbench-opencompass/`

当前项目已经补好了 `Dockerfile`，可以直接按腾讯云 CloudBase 云托管的 Git 仓库部署方式上线。

## 1. 这条路线的定位

这不是传统买服务器自己运维的路线，而是：

- 项目代码放在 GitHub
- 腾讯云 CloudBase 从 GitHub 拉代码
- 平台自动构建并启动容器
- 你只需要配置环境变量和少量部署参数

适合你现在这个“作品演示型项目”。

## 2. 需要准备什么

1. 腾讯云账号
2. 完成实名认证
3. 开通 CloudBase 环境
4. 一个可用的 `DEEPSEEK_API_KEY`

说明：

- 腾讯云账号购买和使用云产品通常要求实名认证
- CloudBase 提供开发期免费环境，但正式使用和部分能力可能进入按量计费

## 3. 推荐部署方式

推荐直接用：

- `云托管`
- `Git 仓库部署`
- `Dockerfile` 构建

不要走静态托管，因为这个项目不是纯前端站点，它需要 Python 后端实时调用模型。

## 4. 控制台里的核心思路

你在 CloudBase 控制台里大致按下面路径操作：

1. 登录腾讯云 CloudBase 控制台
2. 开通或选择一个环境
3. 进入 `云托管`
4. 新建服务
5. 选择 `Git 仓库部署`
6. 连接 GitHub 仓库 `wangshuai521-githu/lawbench-deepseek-demo`
7. 分支选择 `main`
8. 构建方式选择 `Dockerfile`
9. Dockerfile 路径填 `Dockerfile`

## 5. 部署参数建议

服务名建议：

- `lawbench-deepseek-demo`

端口：

- `8080`

环境变量至少配置：

- `DEEPSEEK_API_KEY=你的 DeepSeek Key`
- `APP_ROOT=/app`
- `HOST=0.0.0.0`

说明：

- 项目代码里已经支持读取平台注入的 `PORT`
- `Dockerfile` 默认也把容器监听端口设成了 `8080`

## 6. 部署成功后如何验证

优先检查两个地址：

1. 首页 `/`
2. 接口 `/api/overview`

如果 `/api/overview` 能返回 JSON，说明后端起来了。

## 7. 常见问题

### 1. GitHub 仓库还有没有用

有用，而且很重要。

它至少有三个作用：

1. 作为 CloudBase 的部署源码来源
2. 作为你的项目展示入口，方便别人看代码
3. 作为后续更新部署的版本管理中心

## 8. 目前这条路线的麻烦点

和 Render 相比，CloudBase 的主要麻烦点是：

1. 需要腾讯云账号和实名认证
2. 控制台概念比 Render 多一点
3. 可能会涉及按量计费，需要你注意资源规格和调用量

但和自己买服务器比，它已经省事很多。

## 9. 后续可优化方向

如果你后面想进一步贴合腾讯云生态，可以再考虑两步升级：

1. 把外部 `DeepSeek API` 改成 CloudBase/腾讯云统一模型接入
2. 把前端和后端拆分成静态托管 + 云托管

这两步现在都不是必须。
