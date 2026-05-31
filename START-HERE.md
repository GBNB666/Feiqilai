# 新对话启动提示词 — 复制粘贴即可

```
我要继续 paper-formatter V3 项目。

## 项目位置
C:\Users\博博\paper-formatter\

## 先读这两个文件（已写完，不用重新设计）
1. docs/superpowers/specs/2026-05-31-paper-formatter-v3-design.md — V3 设计（5板块5API单页面）
2. docs/superpowers/plans/2026-05-31-paper-formatter-v3.md — V3 实施计划（6个任务，每步有代码）

## 背景（30秒理解）
V1和V2都失败了，V2有10个Bug修不完。复盘教训见 docs/project-retrospective.md。
V3 核心变化：砍掉非核心功能，只做上传→AI分析→排版→下载四步。

## 当前状态
- 代码已清空，只有 docs/ + .git + .env.backup
- V3 设计文档和计划已写好并 commit
- 任务 0（项目脚手架）刚开始就被中断了

## 直接开始写代码
按照 docs/superpowers/plans/2026-05-31-paper-formatter-v3.md 里的计划逐任务执行。
不要重新设计、不要重新规划、不要 brainstorming。直接按计划写代码。

## 核心铁律（来自10个Bug的教训）
1. 每步写完必须在浏览器验证，不只是 curl
2. 前后端字段名统一用 "id"，不用 "job_id"
3. AppError 继承 HTTPException
4. 下载用 Content-Disposition: attachment + <a target="_blank">
5. matcher Strategy 0c 用 startswith + 长度≤30，不做子串匹配

## API Key
DeepSeek API key 在 .env.backup 里

## 完成标准
浏览器里完整走通：上传docx → AI分析 → 排版 → 下载，格式正确，无控制台报错
```
